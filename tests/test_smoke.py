"""
Smoke Test - Verifies Test Infrastructure Works

This simple test verifies that the testing infrastructure is properly
configured and can run tests successfully.

Run with: pytest tests/test_smoke.py -v
"""

import pytest
import sys
from pathlib import Path

# Add src to path if needed
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def test_smoke_basic():
    """Basic smoke test - always passes."""
    assert True


def test_smoke_imports():
    """Test that basic Python imports work."""
    import os
    import sys
    import pathlib

    assert os is not None
    assert sys is not None
    assert pathlib is not None


def test_smoke_numeric():
    """Test basic numeric operations."""
    result = 2 + 2
    assert result == 4


def test_smoke_string():
    """Test basic string operations."""
    text = "Hello, World!"
    assert "World" in text
    assert text.startswith("Hello")


def test_smoke_list():
    """Test basic list operations."""
    items = [1, 2, 3, 4, 5]
    assert len(items) == 5
    assert sum(items) == 15
    assert max(items) == 5


def test_smoke_dict():
    """Test basic dictionary operations."""
    data = {"key1": "value1", "key2": "value2"}
    assert "key1" in data
    assert data["key1"] == "value1"
    assert len(data) == 2


class TestSmokeClass:
    """Smoke test class."""

    def test_class_method(self):
        """Test that class-based tests work."""
        assert True

    def test_with_fixture(self, tmp_path):
        """Test that pytest fixtures work."""
        # tmp_path is a built-in pytest fixture
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        assert test_file.exists()
        assert test_file.read_text() == "test content"


@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
    (4, 8),
])
def test_smoke_parametrized(input, expected):
    """Test that parametrized tests work."""
    result = input * 2
    assert result == expected


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
