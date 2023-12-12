from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..chassis.config import Config
from ..chassis.consts import const

engines = {}


def init_engine(**config_item):
    if config_item:
        databases = config_item[const.DB_CONFIG_ITEM]
    else:
        databases = Config.DB_CONFIG_ITEM[const.DB_CONFIG_ITEM]
    for db_key, db_url in databases.items():
        engine = create_engine(db_url,
                               logging_name=db_key, poolclass=None, pool_size=5, max_overflow=20, pool_recycle=3600,
                               pool_pre_ping=True)
        engines[db_key] = engine


class DBContext(object):
    def __init__(self, rw='r', db_key=None, need_commit=False, **settings):
        self.__db_key = db_key
        if not self.__db_key:
            if rw == 'w':
                self.__db_key = const.DEFAULT_DB_KEY
            elif rw == 'r':
                self.__db_key = const.READONLY_DB_KEY
        engine = self.__get_db_engine(self.__db_key, **settings)
        self.__engine = engine
        self.need_commit = need_commit

    # @property
    # def db_key(self):
    #     return self.__db_key

    @staticmethod
    def __get_db_engine(db_key, **settings):
        if len(engines) == 0:
            init_engine(**settings)
        return engines[db_key]

    @property
    def session(self):
        return self.__session

    def __enter__(self):
        self.__session = sessionmaker(bind=self.__engine)()
        return self.__session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.need_commit:
            if exc_type:
                self.__session.rollback()
            else:
                self.__session.commit()
        self.__session.close()

    def get_session(self):
        return self.__session