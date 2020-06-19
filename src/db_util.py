import dataclasses as dc
import os
import pathlib as pl
from typing import Union, Callable, Any, Optional
import psycopg2 as psy


def generic_db_query(func: Callable, *args: Any) -> Optional[Any]:
    db_info = get_db_info()
    with psy.connect(user=db_info.user, password=db_info.user, database=db_info.db_name, port=db_info.port) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            return func(cursor, *args)


@dc.dataclass(frozen=True)
class DatabaseConfig:
    """Stores name of a database and database info (username and password)"""
    db_name: str  # database name
    user: str  # name to login to database system with
    password: str  # password to login into the database system with
    port: int  # port of database to connect to


def get_db_info() -> DatabaseConfig:
    """Opens the database configuration file at the given path and returns database name and login info stored inside.
    :param config_file: path to config file
    :return: DatabaseConfig with read in file
    """
    return DatabaseConfig(os.environ['POSTGRES_DB'], os.environ['POSTGRES_USER'], os.environ['POSTGRES_PASSWORD'],
                          int(os.environ['POSTGRES_PORT']))


def init_db(schema_file: Union[str, pl.Path]) -> None:
    """Creates a new database for arXives using configuration info stored in given file path, then reads in the needed
    schema stored in the given schema path.
    :param config_file: path to config file
    :param schema_file: path to schema file
    :return: None
    """
    db_info = get_db_info()
    with psy.connect(host='postgres', port=db_info.port, user=db_info.user, password='postgres') as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            # check that database with same name doesn't exist
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            databases = set([database[0] for database in cursor.fetchall()])
            if db_info.db_name not in databases:
                cursor.execute(f'CREATE DATABASE {db_info.db_name}')

    with psy.connect(user=db_info.user, password=db_info.user, database=db_info.db_name, port=db_info.port) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            with open(schema_file, 'r') as schema:
                cursor.execute(schema.read())


if __name__ == '__main__':
    init_db('init.sql')