"""
Python Test Configuration
Auto-generated conftest.py with common fixtures.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_object():
    """Create a generic mock object."""
    return MagicMock()
