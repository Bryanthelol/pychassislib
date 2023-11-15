from __future__ import absolute_import, unicode_literals

from nameko.standalone.rpc import ServiceRpcProxy

from namekoproxy_pool import BadConfigurationError, ClusterNotConfiguredError
from namekoproxy_pool.connection_pool import ConnectionPool


class PooledServiceRpcProxy(object):

    _pool = None
    _config = None

    def __init__(self, config=None):
        if config:
            self.configure(config)

    def configure(self, config):
        if not config.get('uri'):
            raise BadConfigurationError(
                "Please provide a valid configuration.")

        self._config = config
        self._pool = ConnectionPool(
            self._get_nameko_connection,
            initial_connections=config.get('INITIAL_CONNECTIONS', 2),
            max_connections=config.get('MAX_CONNECTIONS', 8),
            recycle=config.get('POOL_RECYCLE')
        )

    def _get_nameko_connection(self):
        proxy = ServiceRpcProxy(
            timeout=6,
            uri=self._config.get('uri')
        )
        return proxy.start()

    def get_connection(self):
        if not self._pool:
            raise ClusterNotConfiguredError(
                "Please configure your cluster before requesting a connection.")
        return self._pool.get_connection()

    def release_connection(self, connection):
        return self._pool.release_connection(connection)
