from pytest import fixture

from datetime import datetime

from six import string_types

from voluptuous import Optional, All, Any, Range

from typedtuple import TypedTuple

IdSchema = All(int, Range(min=0))


def six_string(v):
    if not isinstance(v, string_types):
        raise ValueError
    return v


dt = Any(datetime, datetime.fromtimestamp)


@fixture
def Organization():
    return TypedTuple('Organization', {'id': IdSchema, Optional('name'): six_string, Optional('created_at'): dt})


@fixture
def User():
    return TypedTuple('User', {'organization_id': IdSchema, 'id': IdSchema, Optional('name'): six_string, Optional('created_at'): dt})
