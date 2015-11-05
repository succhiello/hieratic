from hieratic.index import Index, SimpleIndex


def test_simple_index(User):

    index = SimpleIndex(('organization_id', int), ('id', int))
    user = User(organization_id=0, id=1, name='test')

    expected_key = '0_1'
    expected_dict = {'organization_id': 0, 'id': 1}

    assert index.make_key_from_dict(user._asdict()) == expected_key
    assert index.make_key_from_values(0, 1) == expected_key
    assert index.make_key_from_data(user) == expected_key
    assert index.make_key_dict(expected_key) == expected_dict
    assert index.make_key_dict_from_values(0, 1) == expected_dict
    assert index.make_key_dict_from_dict(user._asdict()) == expected_dict
    assert index.make_key_dict_from_data(user) == expected_dict
    assert index.get_first_value_from_dict(user._asdict()) == 0
    assert index.get_first_value_from_data(user) == 0
    assert index.get_second_value_from_dict(user._asdict()) == 1
    assert index.get_second_value_from_data(user) == 1


def test_simple_index_custom_delimiter(User):

    index = SimpleIndex(('organization_id', int), ('id', int), '/')
    user = User(organization_id=0, id=1, name='test')

    expected_key = '0/1'
    expected_dict = {'organization_id': 0, 'id': 1}

    assert index.make_key_from_dict(user._asdict()) == expected_key
    assert index.make_key_from_values(0, 1) == expected_key
    assert index.make_key_from_data(user) == expected_key
    assert index.make_key_dict(expected_key) == expected_dict
    assert index.make_key_dict_from_values(0, 1) == expected_dict
    assert index.make_key_dict_from_dict(user._asdict()) == expected_dict
    assert index.make_key_dict_from_data(user) == expected_dict


def test_custom_index(User):

    class CustomIndex(Index):

        @property
        def first_desc(self):
            return ('organization_id', int)

        @property
        def second_desc(self):
            return ('id', int)

        def make_key_from_dict(self, d):
            return 'custom_key_{}-{}'.format(d['organization_id'], d['id'])

        def make_key_dict(self, key):
            return self.make_key_dict_from_values(*(key[11:].split('-')))

    index = CustomIndex()
    user = User(organization_id=0, id=1, name='test')

    expected_key = 'custom_key_0-1'
    expected_dict = {'organization_id': 0, 'id': 1}

    assert index.make_key_from_dict(user._asdict()) == expected_key
    assert index.make_key_from_values(0, 1) == expected_key
    assert index.make_key_from_data(user) == expected_key
    assert index.make_key_dict(expected_key) == expected_dict
    assert index.make_key_dict_from_values(0, 1) == expected_dict
    assert index.make_key_dict_from_dict(user._asdict()) == expected_dict
    assert index.make_key_dict_from_data(user) == expected_dict
