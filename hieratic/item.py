from six import iteritems, callable

from voluptuous import Schema, ALLOW_EXTRA

from typedtuple import TypedTupleType

from hieratic import Resource


class ItemResource(Resource):

    def __init__(self, parent, name, engine_name, item_engine):
        Resource.__init__(self, parent, name)
        self.__engine_name = engine_name
        self.__engine = item_engine
        self.__data = None
        self.__is_deleted = False

    @property
    def engine_name(self):
        return self.__engine_name

    @property
    def engine(self):
        return self.__engine

    @classmethod
    def set_data_class(cls, data_class):
        if not issubclass(data_class, TypedTupleType):
            raise ValueError('data class must be a type of typedtuple.TypedTupleType.')
        cls.__data_class = data_class

    @classmethod
    def get_data_class(cls):
        return cls.__data_class

    @staticmethod
    def data_class(data_class):
        def f(clazz):
            clazz.set_data_class(data_class)
            return clazz
        return f

    @classmethod
    def get_persistence_converters(cls):
        try:
            cls.__persistence_converters
        except AttributeError:
            cls.__persistence_converters = {}
        return cls.__persistence_converters

    @classmethod
    def register_persistence_converter(cls, engine_name, converter):
        if not isinstance(converter, Schema) and not callable(converter):
            converter = Schema(converter, extra=ALLOW_EXTRA)
        cls.get_persistence_converters()[engine_name] = converter

    @classmethod
    def get_persistence_converter(cls, engine_name):
        return cls.get_persistence_converters().get(engine_name)

    @staticmethod
    def persistence_converter(converters):
        def f(clazz):
            for k, v in iteritems(converters):
                clazz.register_persistence_converter(k, v)
            return clazz
        return f

    @staticmethod
    def define(data_class, child_definitions=None, converters=None):
        child_definitions = child_definitions or {}
        converters = converters or {}

        def f(clazz):
            return ItemResource.persistence_converter(converters)(
                Resource.children(child_definitions)(
                    ItemResource.data_class(data_class)(clazz)
                )
            )
        return f

    @property
    def data(self):
        if self.__data is None:
            return self.get_data()
        else:
            return self.__data

    def get_data(self):
        self.__data = None if self.__is_deleted else self.get_data_class()(**self.engine.get_dict())
        return self.__data

    def update(self, patch=True, context=None, **kwargs):

        primary_index = self.parent.get_index()
        found_index_key = None

        if primary_index.first_desc[0] in kwargs:
            found_index_key = primary_index.first_desc[0]
        elif primary_index.second_desc is not None and primary_index.second_desc[0] in kwargs:
            found_index_key = primary_index.second_desc[0]

        if found_index_key is not None:
            raise ValueError('index attribute "{}" cannot be updated.'.format(found_index_key))

        updates = kwargs
        persistence_converter = self.get_persistence_converter(self.engine_name)
        if persistence_converter is not None:
            updates = persistence_converter(updates)
        self.engine.update(primary_index, patch, context, updates)
        self.get_data()

    def delete(self, context=None):
        self.engine.delete(self.parent.get_index(), context)
        del self.__parent__[self.__name__]
        self.__is_deleted = True
        self.get_data()
