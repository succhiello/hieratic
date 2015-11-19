from abc import ABCMeta, abstractmethod, abstractproperty

from collections import OrderedDict

from six import add_metaclass


@add_metaclass(ABCMeta)
class Index(object):

    @abstractproperty
    def first_desc(self):
        """must return tuple(str, type)"""
        pass

    @property
    def second_desc(self):
        """must return tuple(str, type)"""
        return None

    @abstractmethod
    def make_key_from_dict(self, d):
        pass

    def make_key_from_values(self, *args):
        return self.make_key_from_dict(self.make_key_dict_from_values(*args))

    def make_key_from_data(self, data):
        values = [getattr(data, self.first_desc[0])]
        if self.second_desc is not None:
            values.append(getattr(data, self.second_desc[0]))
        return self.make_key_from_values(*values)

    @abstractmethod
    def make_key_dict(self, key):
        """must return OrderedDict"""
        pass

    def make_key_dict_from_values(self, *args):

        arg_length = len(args)

        key_dict = OrderedDict(((self.first_desc[0], self.first_desc[1](args[0])),))

        if arg_length == 1:
            if self.second_desc is not None:
                raise ValueError('two values required for making key.')
            return key_dict

        if arg_length > 2 or self.second_desc is None:
            raise ValueError('too many values "{}" for making key.'.format(args))

        key_dict[self.second_desc[0]] = self.second_desc[1](args[1])
        return key_dict

    def make_key_dict_from_dict(self, d):
        values = [d[self.first_desc[0]]]
        if self.second_desc is not None:
            values.append(d[self.second_desc[0]])
        return self.make_key_dict_from_values(*values)

    def make_key_dict_from_data(self, data):
        values = [getattr(data, self.first_desc[0])]
        if self.second_desc is not None:
            values.append(getattr(data, self.second_desc[0]))
        return self.make_key_dict_from_values(*values)

    def get_first_value_from_dict(self, d):
        return d[self.first_desc[0]]

    def get_first_value_from_data(self, data):
        return getattr(data, self.first_desc[0])

    def get_second_value_from_dict(self, d):
        return d[self.second_desc[0]]

    def get_second_value_from_data(self, data):
        return getattr(data, self.second_desc[0])


class SimpleIndex(Index):

    def __init__(self, first_desc, second_desc=None, delimiter='_'):
        self.__first_desc = first_desc
        self.__second_desc = second_desc
        self.__delimiter = delimiter

    @property
    def first_desc(self):
        return self.__first_desc

    @property
    def second_desc(self):
        return self.__second_desc

    @property
    def delimiter(self):
        return self.__delimiter

    def make_key_from_dict(self, d):
        first_value = d[self.first_desc[0]]
        if self.second_desc is None:
            return first_value
        else:
            return '{}{}{}'.format(first_value, self.delimiter, d[self.second_desc[0]])

    def make_key_dict(self, key):
        if self.second_desc is None:
            values = [key]
        else:
            values = str(key).rsplit(self.delimiter, 1)
        return self.make_key_dict_from_values(*values)
