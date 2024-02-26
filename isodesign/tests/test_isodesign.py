from decimal import Decimal
import numpy as np
import pytest
import isodesign


def test_isotopomer_creation(isotopomer):
    for value in [isotopomer.name, isotopomer.labelling]:
        assert isinstance(value, str)
    for value in [isotopomer.step, isotopomer.lower_bound, isotopomer.upper_bound]:
        assert isinstance(value, int)

    assert isotopomer.step > 0
    assert isotopomer.lower_bound >= 0
    assert isotopomer.upper_bound <= 100
    assert isotopomer.upper_bound > isotopomer.lower_bound
    assert isotopomer.num_carbon == 6

def test_fractions_generation(isotopomer):
    fractions = isotopomer.generate_fraction()
    for fraction in fractions:
        assert fraction >= 0
        assert fraction <= 1
        assert isinstance(fraction, Decimal)
    
    assert isinstance(fractions, np.ndarray)
    
