from lavatory.utils import performance


def test_human_friendly_used_space_should_accept_commas():
    assert performance._get_human_friendly_used_space({'usedSpace': '1,011.13 MB'}) == 1011130000
