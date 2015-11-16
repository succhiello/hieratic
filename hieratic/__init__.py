from six import iteritems


class ResourceBase(dict):

    def __init__(self, parent, name=None):
        self.__parent__ = parent
        self.__name__ = name
        self.__root = None

    @property
    def parent(self):
        return self.__parent__

    @property
    def name(self):
        return self.__name__

    @property
    def root(self):
        if self.__root is None:
            self.__root = self.__get_root(self)
        return self.__root

    @classmethod
    def __get_root(cls, instance):
        if instance.__parent__ is None:
            return instance
        else:
            return cls.__get_root(instance.__parent__)


class Resource(ResourceBase):

    @classmethod
    def get_child_definitions(cls):
        try:
            cls.__child_definitions
        except AttributeError:
            cls.__child_definitions = {}
        return cls.__child_definitions

    @classmethod
    def register_child(cls, name, definition):
        cls.get_child_definitions()[name] = definition

    @classmethod
    def get_child_definition(cls, name):
        return cls.get_child_definitions()[name]

    @staticmethod
    def children(definitions):
        def f(clazz):
            for k, v in iteritems(definitions):
                clazz.register_child(k, v)
            return clazz
        return f

    def __getitem__(self, key):
        return self.setdefault(key, self.__make_child(key))

    def __make_child(self, key):
        definition = self.get_child_definition(key)
        return definition(self, key)
