"""
Configuration variables for the tests
"""

import pytest 
from isodesign.base.process import Process
import numpy as np

@pytest.fixture
def process():
    process = Process()
    process.netan = {
            'input': {'Gluc': 1,
                    'FTHF_in': 1},
            'Clen':{ 'Gluc': 6,
                    'FTHF_in': 1},
            'metabs': {'Gluc': 1,
                    'FTHF_in': 1},
            'output': {'FTHF_out': 1},
            'pathway': {}
            }
    
    process.linp_dataframes = {
        "ID_1": {"Id": [None, None], "Comment" : [None, None], "Specie" : ["Gluc", "FTHF_in"], "Isotopomer" : ["100000","0"], "Value" : [1.0, 1.0], "Price" : [np.nan, np.nan]},
        "ID_2": {"Id": [None, None, None], "Comment" : [None, None, None], "Specie" : ["Gluc", "Gluc", "FTHF_in"], "Isotopomer" : ["100000","111111","0"], "Value" : [0.5, 0.5, 1.0], "Price" : [np.nan, np.nan, np.nan]},
        "ID_3": {"Id": [None, None], "Comment" : [None, None], "Specie" : ["Gluc", "FTHF_in"], "Isotopomer" : ["111111", "0"], "Value" : [1.0, 1.0], "Price" : [np.nan, np.nan]}
        }
    return process
