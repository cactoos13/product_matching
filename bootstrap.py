import dotenv

from packages.core.registry import Registry
from packages.core.scheduler import Scheduler, SchedulerConfig
from packages.core.sql_connector import SqlConnectorConfig, SqlConnector
import os

dotenv.load_dotenv()


def register_source_sql_connector():
    source_config = SqlConnectorConfig(
        config_dict={
            'username': os.getenv('SOURCE_MYSQL_DB_USER'),
            'password': os.getenv('SOURCE_MYSQL_DB_PASS'),
            'host': os.getenv('SOURCE_MYSQL_DB_HOST'),
            'port': os.getenv('SOURCE_MYSQL_DB_PORT'),
            'database': os.getenv('SOURCE_MYSQL_DB_DATABASE'),
            'driver': 'mysql'
        },
        read_from_dict=True
    )
    source_sql_connector = SqlConnector(source_config)
    Registry().register(SqlConnector, source_sql_connector, salt='source')


def register_dest_sql_connector():
    dest_config = SqlConnectorConfig(
        config_dict={
            'username': os.getenv('DEST_MYSQL_DB_USER'),
            'password': os.getenv('DEST_MYSQL_DB_PASS'),
            'host': os.getenv('DEST_MYSQL_DB_HOST'),
            'port': os.getenv('DEST_MYSQL_DB_PORT'),
            'database': os.getenv('DEST_MYSQL_DB_DATABASE'),
            'driver': 'mysql'
        },
        read_from_dict=True
    )
    dest_sql_connector = SqlConnector(dest_config)
    Registry().register(SqlConnector, dest_sql_connector)


def register_scheduler():
    Registry().register(Scheduler, Scheduler(
        SchedulerConfig()
        .set_broker_url(os.getenv('CELERY_BROKER_URL'))
        .set_result_backend(os.getenv('CELERY_RESULT_BACKEND'))
        .set_task_serializer('json')
        .set_result_serializer('json')
        .set_accept_content(['json'])
        .set_timezone('GMT')
    ))


def bootstrap(
        source_sql_connector: bool = False,
        des_sql_connector: bool = False,
        scheduler: bool = False,
        total: bool = False
):
    if source_sql_connector or total:
        register_source_sql_connector()
    if des_sql_connector or total:
        register_dest_sql_connector()
    if scheduler or total:
        register_scheduler()


