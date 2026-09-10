import pytest


@pytest.fixture
def api_key() -> str:
    """A free-tier-looking key (``:fx`` suffix) so the client picks the free host."""
    return "test-key:fx"
