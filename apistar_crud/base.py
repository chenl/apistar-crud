from typing import Any, Dict, Iterable

from apistar import Route


class CRUDResource(type):
    METHODS = {
        'list': ('/', 'GET'),  # List resource collection
        'replace': ('/', 'PUT'),  # Replace resource entire collection with a new one
        'drop': ('/', 'DELETE'),  # Drop resource entire collection
        'create': ('/', 'POST'),  # Create a new element for this resource
        'retrieve': ('/{element_id}/', 'GET'),  # Retrieve an element of this resource
        'update': ('/{element_id}/', 'PUT'),  # Update an element of this resource
        'delete': ('/{element_id}/', 'DELETE'),  # Delete an element of this resource
    }
    AVAILABLE_METHODS = tuple(METHODS.keys())
    DEFAULT_METHODS = ('create', 'retrieve', 'update', 'delete', 'list')

    def __new__(mcs, name, bases, namespace):
        try:
            model = namespace['model']
        except KeyError:
            raise AttributeError('{} needs to define attribute: "model"'.format(name))

        try:
            type_ = namespace['type']
        except KeyError:
            raise AttributeError('{} needs to define attribute: "type"'.format(name))

        methods = namespace.get('methods', mcs.DEFAULT_METHODS)

        mcs.add_methods(namespace, methods, model, type_)
        mcs.add_routes(namespace, methods)

        return type(name, bases, namespace)

    @classmethod
    def add_routes(mcs, namespace: Dict[str, Any], methods: Iterable[str]):
        routes = [Route(*mcs.METHODS[method], namespace[method], name=method) for method in methods]
        namespace['routes'] = routes

    @classmethod
    def add_methods(mcs, namespace: Dict[str, Any], methods: Iterable[str], model, type_):
        methods = set(methods) - set(namespace.keys())

        for method in methods:
            try:
                getattr(mcs, 'add_{}'.format(method))(namespace, model, type)
            except AttributeError:
                raise AttributeError('Invalid method "{}", must be one of: {}.'.format(
                    method, ', '.join(mcs.AVAILABLE_METHODS)))