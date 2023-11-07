from __future__ import absolute_import, unicode_literals

from flask import g
from nameko.standalone.rpc import ServiceRpcProxy

from .connection_pool import ConnectionPool
from .errors import (
    BadConfigurationError,
    ClusterNotConfiguredError
)


class PooledClusterRpcProxy(object):

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
                "Please configure your cluster beore requesting a connection.")
        return self._pool.get_connection()

    def release_connection(self, connection):
        return self._pool.release_connection(connection)


class LazyServiceProxy(object):
    def __init__(self, get_connection, service):
        self.get_connection = get_connection
        self.service = service

    def __getattr__(self, name):
        return getattr(getattr(self.get_connection(), self.service), name)


class FlaskPooledClusterRpcProxy(PooledClusterRpcProxy):
    def __init__(self, app=None, connect_on_method_call=True, extra_config=None):
        self._connect_on_method_call = connect_on_method_call
        if app:
            self.init_app(app, extra_config=extra_config)

    def init_app(self, app, extra_config=None):
        config = dict()
        for key, val in app.config.items():
            if key == 'NAMEKO_AMQP_URI':
                config['uri'] = val
        if isinstance(extra_config, dict):
            config.update(extra_config)
        self.configure(config)

        self._connect_on_method_call = config.get(
            'NAMEKO_CONNECT_ON_METHOD_CALL',
            self._connect_on_method_call
        )

        app.teardown_appcontext(self._teardown_nameko_connection)

    def get_connection(self):
        connection = getattr(g, '_nameko_connection', None)
        if not connection:
            connection = super(
                FlaskPooledClusterRpcProxy, self).get_connection()
            g._nameko_connection = connection
        return connection

    def _teardown_nameko_connection(self, exception):
        connection = getattr(g, '_nameko_connection', None)
        if connection is not None:
            self.release_connection(connection)

    def _get_service(self, service):
        if self._connect_on_method_call:
            return LazyServiceProxy(lambda: self.get_connection(), service)
        else:
            return getattr(self.get_connection(), service)

    def __getattr__(self, name):
        return self._get_service(name)

    def __getitem__(self, name):
        return self._get_service(name)