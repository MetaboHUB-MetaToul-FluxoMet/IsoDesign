"""
Configuration variables for the tests
"""

import pytest 
from isodesign.base.isotopomer import Isotopomer


@pytest.fixture
def isotopomer():
    return Isotopomer("Gluc", "111111", 10, 0, 100)

@pytest.fixture
def isotopomer_group():
    gluc_u = Isotopomer("Gluc", "111111", 10, 0, 100)
    gluc_1 = Isotopomer("Gluc", "100000", 10, 0, 100)
    fthf_in = Isotopomer("FTHF", "0", 100, 100, 100)
    isotopomers_group = {"Gluc" : [gluc_u, gluc_1],
                         "FTHF" : [fthf_in]}
    return isotopomers_group

 