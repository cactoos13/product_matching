from packages.business.modules.advertisement.services import AdvertisementSqlService
from packages.core.module import Module
from packages.core.registry import Registry
from packages.core.scheduler import SchedulerConfig, Scheduler
from packages.core.sql_connector import SqlConnectorConfig, SqlConnector
from redis import Redis
from datasketch import MinHashLSH
from sklearn.feature_extraction.text import CountVectorizer
import joblib

import pymysql
pymysql.install_as_MySQLdb()
import os
import dotenv
dotenv.load_dotenv()

#
# def register_vectorizer():
#     vectorizer_path = os.getenv('VECTORIZER_PATH')
#     if not vectorizer_path:
#         raise Exception('VECTORIZER_PATH must be set in environment variables')
#     if  os.path.exists(vectorizer_path):
#         vectorizer = joblib.load(vectorizer_path)
#         Registry().register(CountVectorizer, vectorizer)
#     print("Vectorizer created")
#


def register_index_redis():
    host = os.getenv('LSH_REDIS_HOST')
    port = os.getenv('LSH_REDIS_PORT')
    db = os.getenv('LSH_REDIS_DB')
    if host is None or port is None or db is None:
        raise Exception('LSH_REDIS_HOST, LSH_REDIS_PORT, LSH_REDIS_DB must be set in environment variables')
    Registry().register(Redis, Redis(
        host = host,
        port = int(port),
        db = int(db),
        decode_responses=True
    ))
def register_lsh():
    threshold = os.getenv('LSH_SIMILARITY_THRESHOLD')
    if threshold is None:
        raise Exception('LSH_THRESHOLD must be set in environment variables')

    perms = os.getenv('LSH_PERMUTATIONS')
    if perms is None:
        raise Exception('LSH_PERMUTATIONS must be set in environment variables')

    db = os.getenv('LSH_REDIS_DB')
    if db is None:
        raise Exception('LSH_REDIS_DB must be set in environment variables')
    Registry().register(
        MinHashLSH,
        MinHashLSH(
            threshold= float(threshold),
            num_perm= int(perms),
            storage_config={
                'type': 'redis',
                'redis': {
                    'host': os.getenv('LSH_REDIS_HOST'),
                    'port': os.getenv('LSH_REDIS_PORT'),
                    'db': int(db),
                },
                'basename': b'minhash',
                'key': 'minhash'
            }
        )
    )
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
    print(os.getenv('CELERY_BROKER_URL'))
    print(os.getenv('CELERY_RESULT_BACKEND'))
    Registry().register(Scheduler, Scheduler(
        SchedulerConfig()
        .set_broker_url(os.getenv('CELERY_BROKER_URL'))
        .set_result_backend(os.getenv('CELERY_RESULT_BACKEND'))
        .set_task_serializer('json')
        .set_result_serializer('json')
        .set_accept_content(['json'])
        .set_timezone('GMT')
    ))
def register_modules(modules: list[Module]):
    for module in modules:
        module.install()
        Registry().register(module.__class__, module)

def bootstrap(
        modules: list[Module] = None,
        source_sql_connector: bool = False,
        des_sql_connector: bool = False,
        index_redis: bool = False,
        lsh: bool = False,
        scheduler: bool = False,
        vectorizer: bool = False,
        total: bool = False,
):

    if source_sql_connector or total:
        register_source_sql_connector()
    if des_sql_connector or total:
        register_dest_sql_connector()
    if scheduler or total:
        register_scheduler()
    if index_redis or total:
        register_index_redis()
    if lsh or total:
        register_lsh()
    if vectorizer or total:
        register_vectorizer()
    if modules:
        register_modules(modules)


