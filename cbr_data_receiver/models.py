from sqlalchemy.schema import Column, Table, MetaData, ForeignKey
from sqlalchemy.types import Integer, String, Date, Float

metadata = MetaData()
schema_name = 'cbr_data'

currencies = Table('currencies', metadata,
                   Column('id', String, primary_key=True),
                   Column('name_rus', String),
                   Column('code', String),
                   Column('nominal', Integer),
                   schema=schema_name)

quotes = Table('quotes', metadata,
               Column('id', Integer, primary_key=True, autoincrement=True),
               Column('currency', String),
               Column('date', Date),
               Column('value', Float),
               schema=schema_name)
