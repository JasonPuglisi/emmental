"""Tests filesystem search functionality (including vulnerability.)"""

import pytest
from src.search import search_ls


@pytest.mark.parametrize('directory, query, match', [
    ('/', 'e', 'etc'),
    ('/', ';echo BAD_OUTPUT!', 'BAD_OUTPUT!')
])
def test_search_ls(directory, query, match):
    """Test searching the filesystem and injecting shell commands."""
    assert match in search_ls(directory, query)
