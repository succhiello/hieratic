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
    def update(self, patch, updates):
        pass

    @abstractmethod
    def delete(self):
        pass


@add_metaclass(ABCMeta)
class CollectionEngine(object):

    def __init__(self, name, *args, **kwargs):
        pass

    @abstractmethod
    def create_raw_item(self, index, data_dict):
        pass

    @abstractmethod
    def retrieve_raw_item(self, key_dict):
        pass

    @abstractmethod
    def query_raw_items(self, index_name, **kwargs):
        pass
