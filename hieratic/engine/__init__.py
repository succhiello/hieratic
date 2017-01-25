from abc import ABCMeta, abstractmethod

from six import add_metaclass


@add_metaclass(ABCMeta)
class ItemEngine(object):

    def __init__(self, collection, raw_item):
        self.__collection = collection

    @property
    def collection(self):
        return self.__collection

    @abstractmethod
    def get_dict(self):
        pass

    @abstractmethod
    def update(self, index, patch, context, updates):
        pass

    @abstractmethod
    def delete(self, index, context):
        pass


@add_metaclass(ABCMeta)
class CollectionEngine(object):

    def __init__(self, name, *args, **kwargs):
        pass

    @abstractmethod
    def create_raw_item(self, index, data_dict, context):
        pass

    @abstractmethod
    def retrieve_raw_item(self, key_dict):
        pass

    @abstractmethod
    def query_raw_items(self, index_name, **kwargs):
        pass

    class __DefaultContext(object):

        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, tracaback):
            return False

    @classmethod
    def get_context(cls, *args, **kwargs):
        return cls.__DefaultContext(*args, **kwargs)
