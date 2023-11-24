import pytest
from unittest.mock import Mock, MagicMock

from cbr_data_receiver.worker import CbrWorker

@pytest.fixture()
def cbrf_worker():
    server_responce = '''<?xml version="1.0" encoding="windows-1251"?>
    <ValCurs Date="11.06.2022" name="Foreign Currency Market">
    <Valute ID="R01010">
        <NumCode>036</NumCode>
        <CharCode>AUD</CharCode>
        <Nominal>1</Nominal>
        <Name>Австралийский доллар</Name>
        <Value>41,1437</Value>
    </Valute>
    <Valute ID="R01020A">
        <NumCode>944</NumCode>
        <CharCode>AZN</CharCode>
        <Nominal>1</Nominal>
        <Name>Азербайджанский манат</Name>
        <Value>33,9871</Value>
    </Valute>
    </ValCurs>'''
    requester, db_client = Mock(), Mock()
    requester.make_cbrf_request = MagicMock(return_value=server_responce)
    db_client.insert_data_quotes = MagicMock(return_value=None)
    db_client.insert_data_currencies = MagicMock(return_value=None)
    return CbrWorker(config=Mock(),
                     db_client=db_client,
                     requester=requester)


def test_worker_params_completed(cbrf_worker, monkeypatch):
    monkeypatch.setattr(cbrf_worker, '_wait_for_the_next_iteration', MagicMock(return_value=None))
    worker = cbrf_worker.start()
    assert worker._params['completed']


def test__worker_params_message(cbrf_worker, monkeypatch):
    monkeypatch.setattr(cbrf_worker, '_wait_for_the_next_iteration', MagicMock(return_value=None))
    worker = cbrf_worker.start()
    assert worker._params['completed']
