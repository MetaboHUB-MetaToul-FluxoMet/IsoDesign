"""
Configuration variables for the tests
"""

import pytest
from isodesign.base.process import Process
from isodesign.base.isotopomer import Isotopomer
import pandas as pd


@pytest.fixture
def netan():
    return {
        "input": {"Gluc": 1, "FTHF_in": 1},
        "Clen": {"Gluc": 6, "FTHF_in": 1},
        "metabs": {"Gluc": 1, "FTHF_in": 1},
        "output": {"FTHF_out": 1},
        "pathway": {"Gluc": "Glycolysis"},
    }


@pytest.fixture
def isotopomer_group():
    return {
        "Gluc": [
            Isotopomer(
                name="Gluc",
                labelling="000000",
                intervals_nb=2,
                lower_bound=0,
                upper_bound=1,
                price=50.0,
            ),
            Isotopomer(
                name="Gluc",
                labelling="111111",
                intervals_nb=2,
                lower_bound=0,
                upper_bound=1,
                price=75.0,
            ),
        ],
        "FTHF_in": [
            Isotopomer(
                name="FTHF_in",
                labelling="0",
                intervals_nb=10,
                lower_bound=1,
                upper_bound=1,
                price=25.0,
            )
        ],
    }


@pytest.fixture
def linp_dataframes():
    return {
        "ID_1": {
            "Id": [None, None, None],
            "Comment": [None, None, None],
            "Specie": ["Gluc", "Gluc", "FTHF_in"],
            "Isotopomer": ["000000", "111111", "0"],
            "Value": [1.0, 0.0, 1.0],
            "Price": [50.0, 0.0, 25.0],
        },
        "ID_2": {
            "Id": [None, None, None],
            "Comment": [None, None, None],
            "Specie": ["Gluc", "Gluc", "FTHF_in"],
            "Isotopomer": ["000000", "111111", "0"],
            "Value": [0.5, 0.5, 1.0],
            "Price": [25.0, 37.5, 25.0],
        },
        "ID_3": {
            "Id": [None, None, None],
            "Comment": [None, None, None],
            "Specie": ["Gluc", "Gluc", "FTHF_in"],
            "Isotopomer": ["000000", "111111", "0"],
            "Value": [0.0, 1.0, 1.0],
            "Price": [0.0, 75.0, 25.0],
        },
    }


@pytest.fixture
def summary_dataframe():
    return pd.DataFrame(
        {
            "Name": ["Gluc", "FTHF_in", "Arg"],
            "Kind": ["NET", "XCH", "NET"],
            "Initial flux value": [None, 0.2, 0.1],
            "Value": [0.5, 0.02, 0.1],
            "Value difference": [None, 0.18, 0.0],
            "ID_1": [0.2, 0.2, 0.3],
            "ID_2": [0.5, 0.02, 0.1],
            "ID_3": [0.8, 0.01, 0.1],
        }
    )
