from decimal import Decimal
import numpy as np
import pytest
from isodesign.process.calculation import LabelInput


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
    
def test_generate_labelling_combinations(label_input):
    isotopomers_group = LabelInput(label_input)
    isotopomers_group.generate_labelling_combinations()
    assert "glucose" in isotopomers_group.isotopomers_combination
    for combination in isotopomers_group.isotopomers_combination.values():
        for pair in combination: 
            assert sum(pair) == 1 
