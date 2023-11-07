class BadConfigurationError(Exception):
    pass


class ClientUnavailableError(Exception):
    pass


class ClusterNotConfiguredError(Exception):
    pass


class ClientConnectionTimeoutError(Exception):
    pass