from hieratic import Resource
from hieratic.service import ServiceResource


class TestChildResource0(Resource):
    pass


class TestGrandchildResource(Resource):
    pass


@Resource.children({
    'grandchild': TestGrandchildResource,
})
class TestChildResource1(Resource):
    pass


@ServiceResource.utilize('child0', 'child1')
class FooService(ServiceResource):
    pass


@Resource.children({
    'child0': TestChildResource0,
    'child1': TestChildResource1,
    'foo_service': FooService,
})
class RootResource(Resource):
    pass


def test_resource():

    root = RootResource(None, 'test')

    assert root.__parent__ is None
    assert root.__name__ == 'test'

    assert isinstance(root['child0'], TestChildResource0)
    assert root['child0'].__name__ == 'child0'

    assert isinstance(root['child1'], TestChildResource1)
    assert root['child1'].__name__ == 'child1'

    assert isinstance(root['child1']['grandchild'], TestGrandchildResource)
    assert root['child1']['grandchild'].__name__ == 'grandchild'

    assert root['child0'].__parent__ == root['child1'].__parent__ == root
    assert root['child1']['grandchild'].__parent__ == root['child1']

    assert root['child1']['grandchild'].root == root

    assert root['foo_service'].child0 == root['child0']
    assert root['foo_service'].child1 == root['child1']
