"""
Pytest configuration and shared fixtures for the test suite.

This file contains shared test fixtures, configurations, and utilities
that can be used across all test modules.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path for imports during testing
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
