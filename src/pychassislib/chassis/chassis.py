def init_statsd(prefix=None, host=None, port=8125):
    from statsd import StatsClient
    statsd = StatsClient(host, port, prefix=prefix)
    return statsd


def init_logger(name=None, level=None):
    """
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0
    :param name: log 名称
    :param level: log 等级
    :return:
    """
    import logging
    logger = logging.getLogger() if name is None else logging.getLogger(name)
    logger.setLevel(logging.INFO) if level is None else logging.getLevelName(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(filename)s[line:%(lineno)d] [%(levelname)s] [%(name)s] (%(threadName)-10s) %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def init_sentry():
    from nameko_sentry import SentryReporter
    return SentryReporter()
