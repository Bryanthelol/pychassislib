import os

from .consts import const


class Config:
    """
    基础配置
    """

    # 先读 env 环境变量中的配置

    # 指定加密KEY
    SECRET_KEY = os.getenv('SECRET_KEY')

    # 指定关系型数据库
    DEFAULT_DATABASE_URI = os.getenv('DEFAULT_DATABASE_URI')
    READONLY_DATABASE_URI = os.getenv('READONLY_DATABASE_URI')
    DB_CONFIG_ITEM = {
        const.DB_CONFIG_ITEM: {
            const.DEFAULT_DB_KEY: DEFAULT_DATABASE_URI,
            const.READONLY_DB_KEY: READONLY_DATABASE_URI,
        }
    }

    STATSD_PREFIX = os.getenv('STATSD_PREFIX')
    STATSD_HOST = os.getenv('STATSD_HOST')
    STATSD_PORT = os.getenv('STATSD_PORT')

