def init_statsd(key):
    from nameko_statsd import StatsD
    statsd = StatsD(key)
    return statsd


def init_logger():
    import logging
    from logstash_formatter import LogstashFormatterV1
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = LogstashFormatterV1()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def init_sentry():
    from nameko_sentry import SentryReporter
    return SentryReporter()
