import os
from peewee import PostgresqlDatabase

db = PostgresqlDatabase(os.environ['POSTGRES_URL'])

db.connect()