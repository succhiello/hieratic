from six import itervalues, iteritems

from hieratic.engine import ItemEngine, CollectionEngine


class Item(ItemEngine):

    def __init__(self, collection, raw_item):
        ItemEngine.__init__(self, collection, raw_item)
        self.__data = raw_item

    def update(self, index, patch, context, updates):
        if patch:
            self.__data.update(updates)
        else:
            self.__data = updates

    def delete(self, index, context):
        self.collection._delete_raw_item(index.make_key_dict_from_dict(self.__data))
        self.__data = None

    def get_dict(self):
        return self.__data


class Collection(CollectionEngine):

    def __init__(self, name):
        self.__data = {}

    def create_raw_item(self, index, data_dict, context):
        first_value = index.get_first_value_from_dict(data_dict)
        if index.second_desc is None:
            self.__data[first_value] = data_dict
        else:
            self.__data.setdefault(first_value, {})[index.get_second_value_from_dict(data_dict)] = data_dict
        return data_dict

    def retrieve_raw_item(self, key_dict):
        values = tuple(itervalues(key_dict))
        if len(values) == 1:
            raw_item = self.__data.get(values[0])
        else:
            raw_item = self.__data.get(values[0], {}).get(values[1])
        if raw_item is None:
            raise KeyError(key_dict)
        return raw_item

    def query_raw_items(self, index, parent_key_value, **kwargs):
        return itervalues(self.__data[parent_key_value[1]])

    def _delete_raw_item(self, key_dict):

        items = list(iteritems(key_dict))

        if len(items) == 1:
            del self.__data[items[0][1]]
        elif len(items) == 2:
            del self.__data[items[0][1]][items[1][1]]
