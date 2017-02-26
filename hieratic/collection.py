from pkg_resources import iter_entry_points

from hieratic import ResourceBase
from hieratic.item import ItemResource
from hieratic.exceptions import InvalidStructure


class CollectionResource(ResourceBase):

    __engine_modules = {}
    __indices = {}

    def __init__(self, parent, name, engine_name, *args, **kwargs):
        if isinstance(parent, CollectionResource):
            raise InvalidStructure('Collection must not be a child of Collection.')
        ResourceBase.__init__(self, parent, name)
        self.__engine_name = engine_name
        engine_module = self.get_engine_module()
        self.__engine = engine_module.Collection(name, *args, **kwargs)

    @property
    def engine_name(self):
        return self.__engine_name

    @property
    def engine(self):
        return self.__engine

    @classmethod
    def set_item_class(cls, item_class):
        if not issubclass(item_class, ItemResource):
            raise InvalidStructure('item class must be the ItemResource.')
        cls.__item_class = item_class

    @classmethod
    def get_item_class(cls):
        return cls.__item_class

    @staticmethod
    def item_class(item_class):
        def f(clazz):
            clazz.set_item_class(item_class)
            return clazz
        return f

    @classmethod
    def set_indices(cls, indices):
        cls.__indices = indices

    @classmethod
    def get_index(cls, name=None):
        return cls.__indices[name]

    @staticmethod
    def indices(primary_index, **secondary_indices):
        indices = secondary_indices
        indices.update({None: primary_index})

        def f(clazz):
            clazz.set_indices(indices)
            return clazz
        return f

    @staticmethod
    def define(item_class, primary_index, **secondary_indices):
        def f(clazz):
            return CollectionResource.indices(primary_index, **secondary_indices)(
                CollectionResource.item_class(item_class)(clazz)
            )
        return f

    def create(self, data, context=None):
        item_class = self.get_item_class()
        data_class = item_class.get_data_class()
        if not isinstance(data, data_class):
            raise ValueError('{} is not instance of {}'.format(data, data_class.__name__))

        primary_index = self.get_index()

        if isinstance(self.parent, ItemResource):
            first_value = primary_index.get_first_value_from_data(data)
            if first_value != self.parent.name:
                raise ValueError("{} doesn't match parent name \"{}\".".format(
                    data,
                    self.parent.name,
                ))
            key = primary_index.get_second_value_from_data(data)
        else:
            key = primary_index.make_key_from_data(data)

        data_dict = data._asdict()

        persistence_converter = item_class.get_persistence_converter(self.engine_name)
        if persistence_converter is not None:
            data_dict = persistence_converter(data_dict)

        item_engine = self.get_engine_module().Item(
            self.engine,
            self.engine.create_raw_item(primary_index, data_dict, context)
        )

        item = item_class(self, key, self.engine_name, item_engine)
        self[key] = item
        return item

    def retrieve(self, *args):
        try:
            return self[self.get_index().make_key_from_values(*args)]
        except KeyError:
            return None

    def __getitem__(self, key):
        return self.setdefault(key, self.__make_item(key))

    def __make_item(self, key, index=None):
        item_engine_class = self.get_engine_module().Item
        idx = self.get_index(index)

        if isinstance(self.parent, ItemResource):
            key_dict = idx.make_key_dict_from_values(self.parent.name, key)
        else:
            key_dict = idx.make_key_dict(key)

        item_engine = item_engine_class(self.engine, self.engine.retrieve_raw_item(key_dict))

        return self.get_item_class()(self, key, self.engine_name, item_engine)

    def query(self, index=None, **kwargs):

        is_parent_item_resource = isinstance(self.parent, ItemResource)
        parent_key_value = None
        if index is None and is_parent_item_resource:
            parent_key_value = (self.get_index().first_desc[0], self.parent.name)

        return self.make_items_generator(
            self.engine.query_raw_items(index, parent_key_value, **kwargs)
        )

    def bulk_get(self, **kwargs):
        return self.make_items_generator(self.engine.bulk_get_raw_items(**kwargs))

    def get_engine_module(self):
        return self.__get_engine_module(self.engine_name)

    def make_items_generator(self, result):

        primary_index = self.get_index()
        is_parent_item_resource = isinstance(self.parent, ItemResource)

        item_class = self.get_item_class()
        item_engine_class = self.get_engine_module().Item

        for raw_item in result:
            item_engine = item_engine_class(self.engine, raw_item)
            d = item_engine.get_dict()
            if is_parent_item_resource:
                key = primary_index.get_second_value_from_dict(d)
            else:
                key = primary_index.make_key_from_dict(d)
            item = item_class(self, key, self.engine_name, item_engine)
            self[key] = item
            yield item

    @classmethod
    def __get_engine_module(cls, engine_name):
        return cls.__engine_modules.setdefault(
            engine_name,
            cls.__load_entry_point('hieratic.engine', engine_name)
        )

    @classmethod
    def get_context(cls, engine_name, *args, **kwargs):
        return cls.__get_engine_module(engine_name).Collection.get_context(*args, **kwargs)

    @staticmethod
    def __load_entry_point(group, name):
        entry_point = next((x for x in iter_entry_points(group, name) if x.name == name), None)
        if entry_point is None:
            raise ValueError('entry point "{}.{}" not found.'.format(group, name))
        return entry_point.load()
