def init_statsd(prefix=None, host=None, port=8125):
    from statsd import StatsClient
    statsd = StatsClient(host, port, prefix=prefix)
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
