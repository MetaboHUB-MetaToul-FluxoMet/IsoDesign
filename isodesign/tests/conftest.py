import pytest 
import pandas as pd
from isodesign.process.calculation import Isotopomer, Process

@pytest.fixture
def isotopomer():
    return Isotopomer("Gluc", "111111", 10, 0, 100)

@pytest.fixture
def label_input():
    gluc_u = Isotopomer("Gluc", "111111", 10, 0, 100)
    gluc_1 = Isotopomer("Gluc", "100000", 10, 0, 100)
    isotopomers_group = {"glucose" : [gluc_u, gluc_1]}
    return isotopomers_group

@pytest.fixture 
def process():
    return Process()

 