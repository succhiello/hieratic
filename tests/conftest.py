from pytest import fixture

from datetime import datetime

from six import string_types

from voluptuous import Optional, All, Any, Range

from typedtuple import typedtuple

IdSchema = All(int, Range(min=0))


def six_string(v):
    if not isinstance(v, string_types):
        raise ValueError
    return v


dt = Any(datetime, datetime.fromtimestamp)


@fixture
def Organization():
    return typedtuple('Organization', {'id': IdSchema, Optional('name'): six_string, Optional('created_at'): dt})


@fixture
def User():
    return typedtuple('User', {'organization_id': IdSchema, 'id': IdSchema, Optional('name'): six_string, Optional('created_at'): dt})
