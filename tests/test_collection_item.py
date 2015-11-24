from pytest import raises, fixture

from time import mktime
from datetime import datetime

from hieratic import Resource
from hieratic.item import ItemResource
from hieratic.collection import CollectionResource
from hieratic.index import SimpleIndex


@fixture
def UserResource(User):

    @ItemResource.define(User)
    class UserRes(ItemResource):
        pass

    return UserRes


@fixture
def UsersResource(UserResource):

    @CollectionResource.define(
        item_class=UserResource,
        primary_index=SimpleIndex(('organization_id', int), ('id', int)),
    )
    class UsersRes(CollectionResource):
        def __init__(self, parent, name):
            CollectionResource.__init__(self, parent, name, 'memory')

    return UsersRes


@fixture
def OrganizationResource(Organization, UsersResource):

    @ItemResource.define(
        data_class=Organization,
        child_definitions={'users': UsersResource},
        converters={
            'memory': {
                'created_at': lambda dt: mktime(dt.timetuple()) + dt.microsecond / 1e6,
            },
        },
    )
    class OrganizationRes(ItemResource):
        pass

    return OrganizationRes


@fixture
def OrganizationsResource(OrganizationResource):

    @CollectionResource.define(
        item_class=OrganizationResource,
        primary_index=SimpleIndex(('id', int),)
    )
    class OrganizationsRes(CollectionResource):
        def __init__(self, parent, name):
            CollectionResource.__init__(self, parent, name, 'memory')

    return OrganizationsRes


@fixture
def RootResource(OrganizationsResource):

    @Resource.children({
        'organizations': OrganizationsResource
    })
    class RootRes(Resource):
        pass

    return RootRes


def test_CRUD(RootResource, Organization, User):

    root_res = RootResource(None, 'root')

    now = datetime.now()

    # create
    organization_res = root_res['organizations'].create(Organization(id=0, created_at=now))
    organization = organization_res.data
    assert organization.id == 0
    assert organization.created_at == now

    with raises(ValueError):
        root_res['organizations'].create(User(organization_id=0, id=0))

    # retrieve
    organization_res = root_res['organizations'][0]
    organization = organization_res.data
    assert organization.id == 0

    organization_res = root_res['organizations'].retrieve(0)
    organization = organization_res.data
    assert organization.id == 0

    assert root_res['organizations'].retrieve(100) is None

    # update
    organization_res.update(name='updated')
    organization = organization_res.data
    assert organization.name == 'updated'

    with raises(ValueError):
        organization_res.update(id=1)

    # delete
    organization_res.delete()
    organization = organization_res.data
    assert organization is None

    with raises(KeyError):
        root_res['organizations'][0]


def test_query(RootResource, Organization, User):

    root_res = RootResource(None, 'root')

    organization_res = root_res['organizations'].create(Organization(id=0))
    organization_res['users'].create(User(organization_id=0, id=0))
    organization_res['users'].create(User(organization_id=0, id=1))
    organization_res['users'].create(User(organization_id=0, id=2))

    assert(len(list(organization_res['users'].query()))) == 3


def test_hierarchy(RootResource, Organization, User):

    root_res = RootResource(None, 'root')

    organization_res = root_res['organizations'].create(Organization(id=0))
    organization_res['users'].create(User(organization_id=0, id=0))

    user = root_res['organizations'][0]['users'][0].data
    assert user.organization_id == 0
    assert user.id == 0

    with raises(ValueError):
        organization_res['users'].create(User(organization_id=1, id=0))

    root_res['organizations'][0]['users'][0].delete()
    with raises(KeyError):
        root_res['organizations'][0]['users'][0]
