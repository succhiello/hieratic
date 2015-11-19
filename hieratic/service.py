from hieratic import Resource


class ServiceResource(Resource):

    @classmethod
    def get_utility_names(cls):
        try:
            cls.__utility_names
        except AttributeError:
            cls.__utility_names = set()
        return cls.__utility_names

    @classmethod
    def add_utility_names(cls, name):
        cls.get_utility_names().add(name)

    @staticmethod
    def utilize(*args):
        def f(clazz):
            for name in args:
                clazz.add_utility_names(name)
            return clazz
        return f

    def __init__(self, parent, name):
        Resource.__init__(self, parent, name)
        for name in self.get_utility_names():
            setattr(self, name, self.root[name])
