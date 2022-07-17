import pytest

from route import *

test_file = "tests/data/route_1.kml"


@pytest.fixture
def sample_route() -> Route:
    route = Route(test_file)
    return route
