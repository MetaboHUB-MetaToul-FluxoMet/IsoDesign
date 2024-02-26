import pytest 
import pandas as pd
from isodesign.process.calculation import Isotopomer, LabelInput, Process

@pytest.fixture
def isotopomer():
    return Isotopomer("Gluc", "111111", 10, 0, 100)

# @pytest.fixture
# def LabelInput():
#     return LabelInput()