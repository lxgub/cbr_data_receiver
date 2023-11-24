"""
CbrWorker module
"""
import time
from typing import Any, Dict, List, Tuple

import requests
import xmltodict

import sqlalchemy as sa
from cbr_data_receiver.logger import get_logger
from cbr_data_receiver.models import currencies, quotes, schema_name
from cbr_data_receiver.singletons import Config
from sqlalchemy.dialects.postgresql import insert
from tenacity import TryAgain, retry


class Requester:
    """
    HTTP client
    """

    def __init__(self, cbrf_api: str) -> None:
        self._cbrf_api = cbrf_api

    @retry()
    def make_cbrf_request(self) -> str:
        """
        Making a request.
        In case of unsuccessful result, repeat.
        """
        result = requests.get(self._cbrf_api)
        if result.status_code == 200:
            return result.text
        time.sleep(10)
        raise TryAgain


class PostgreSQLClient:
    """
    PostgreSQL DB client
    """

    def __init__(self, conf: Config) -> None:
        self.conf = conf
        self._schema = schema_name

    @classmethod
    def get_client(cls, **options):
        """
        Creates DB client
        """
        self = cls(**options)
        self._init_connect()
        return self

    def _init_connect(self) -> None:
        """
        Initializes the connection to the database
        """
        self.engine = sa.create_engine(f"postgresql://{self.conf['user']}"
                                       f":{self.conf['password']}"
                                       f"@{self.conf['host']}"
                                       f":{self.conf['port']}"
                                       f"/{self.conf['dbname']}")

    def insert_data_quotes(self, data_lst: List) -> None:
        """
        Adds data to the quotes table
        """
        with self.engine.begin() as connection:
            connection.execute(quotes.insert(), data_lst)

    def insert_data_currencies(self, data_lst: List) -> None:
        """
        Adds data to the currencies table.
        In case of conflict currencies_pkey, update the data
        """
        with self.engine.begin() as connection:
            stmt = insert(currencies).values(data_lst)
            stmt = stmt.on_conflict_do_update(constraint="currencies_pkey",
                                              set_={
                                                  "name_rus": stmt.excluded.name_rus,
                                                  "code": stmt.excluded.code,
                                                  "nominal": stmt.excluded.nominal,
                                              })
            connection.execute(stmt)


class CbrWorker:
    """
    The worker receives data from the Central Bank of the
    Russian Federation and adds it to the user database
    """

    def __init__(self, config: Config,
                 db_client: PostgreSQLClient,
                 requester: Requester) -> None:
        self._db_client = db_client
        self._requester = requester
        self._waiting_time = config.waiting_time
        self._tasks = [QuotesTask, CurrenciesTask]
        self._params = {'completed': True, 'message': 'Data received and successfully added to DB.'}
        self._logger = get_logger()

    def start(self):
        """
        Starts running tasks
        """
        server_response = self._requester.make_cbrf_request()
        for task in self._tasks:
            if self._params['completed']:
                task.start(server_response, self._db_client, self._params)
            # TODO telegram notifier, to inform about CB RF format changes
        self._logger.info(f"{self._params['message']}")
        self._logger.info(f'Waiting for the next iteration ...')
        self._wait_for_the_next_iteration()
        return self

    def _wait_for_the_next_iteration(self):
        """
        Wait a day for the next update
        """
        time.sleep(self._waiting_time)


class BaseTask:
    """
    Base class, implements tasks methods for CbrWorker
    """

    def __init__(self,
                 server_response: str,
                 db_client: PostgreSQLClient,
                 params: Dict[str, Any]) -> None:
        self._server_response = server_response
        self._db_client = db_client
        self._params = params

    def _get_date_and_currencies(self, json_server_response: Dict[str, Any]) -> Tuple:
        date, currencies_data = None, None
        try:
            val_curs = json_server_response['ValCurs']
            date = val_curs['@Date']
            currencies_data = val_curs['Valute']
        except KeyError:
            self._params['completed'] = False
            self._params['message'] = 'Problem with parsing data, ' \
                                      'received from the Central Bank ' \
                                      'of the Russian Federation'
        return date, currencies_data


class QuotesTask(BaseTask):
    """
    Task fills in quotes table
    """

    @classmethod
    def start(cls, server_response: str,
              db_client: PostgreSQLClient,
              params: Dict[str, Any]) -> None:
        """
        Starting the quotes task
        """
        self = cls(server_response, db_client, params)
        json_server_response = xmltodict.parse(server_response)
        date, currencies_data = self._get_date_and_currencies(json_server_response)
        if date and currencies_data:
            clean_data = self._get_quotes(date, currencies_data)
            self._db_client.insert_data_quotes(clean_data)

    @staticmethod
    def _get_quotes(date: str, currencies_data: List) -> List:
        """
        Parsing quotes data
        """
        result = []
        for val in currencies_data:
            result.append({'currency': val.get('@ID', ''),
                           'date': date,
                           'value': float(val.get('Value', '').replace(',', '.')),
                           })
        return result


class CurrenciesTask(BaseTask):
    """
    Task fills in currencies table
    """

    @classmethod
    def start(cls, server_response: str, db_client: PostgreSQLClient, params: Dict[str, Any]):
        """
        Starting the currencies task
        """
        self = cls(server_response, db_client, params)
        json_server_response = xmltodict.parse(server_response)
        date, currencies_data = self._get_date_and_currencies(json_server_response)
        if date and currencies_data:
            clean_data = self._get_currencies(currencies_data)
            self._db_client.insert_data_currencies(clean_data)

    @staticmethod
    def _get_currencies(currencies: List) -> List:
        """
        Parsing currencies data
        """
        result = []
        unique_currencies = {i['@ID']: i for i in currencies}.values()
        for val in unique_currencies:
            result.append({'id': val.get('@ID'),
                           'name_rus': val.get('Name'),
                           'code': val.get('CharCode'),
                           'nominal': int(val.get('Nominal')),
                           })
        return result
