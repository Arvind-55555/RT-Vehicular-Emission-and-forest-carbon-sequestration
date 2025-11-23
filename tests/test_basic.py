"""
Basic tests to ensure CI pipeline works
"""

def test_basic_import():
    """Test that basic imports work"""
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        assert True
    except ImportError:
        assert False, "Required packages not installed"

def test_basic_math():
    """Test basic functionality"""
    assert 1 + 1 == 2

def test_data_structures():
    """Test basic data structure operations"""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert sum(test_list) == 6