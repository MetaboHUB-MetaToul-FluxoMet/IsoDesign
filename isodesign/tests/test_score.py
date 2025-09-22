import pytest
import pandas as pd
from isodesign.base.score import Score, ScoreHandler
from decimal import Decimal as D
from collections import namedtuple
import numpy as np

@pytest.mark.parametrize(
    "series, weight, expected",
    [
        (Score(pd.Series([0.2, 0.2, 0.3])), 1, 0.7),
        (Score(pd.Series([1.0, 2.0, 3.0])), 2.5, 15.0),
        (Score(pd.Series([])), 1, 0.0),
    ],
)

def test_apply_sum_sd(series, weight, expected):
    assert series.apply_sum_sd(weight) == expected

@pytest.mark.parametrize(
    "series, weight, threshold, expected",
    [
        (Score(pd.Series([0.2, 0.2, 0.3])), 1, 0.3, 2.0),
        (Score(pd.Series([1.0, 2.0, 3.0])), 2.5, 2.0, 2.5),
        (Score(pd.Series([])), 1, 12.0, 0.0),
    ],
)
def test_apply_sum_nb_flux_sd(series, weight, threshold, expected):
    assert series.apply_sum_nb_flux_sd(threshold, weight_flux=weight) == expected


def test_apply_number_labeled_inputs(summary_dataframe):
    label_input = Score(summary_dataframe["ID_2"])
    linp_files_infos = {
        "ID_1": namedtuple("InfoLinp", ["nb_labeled_inputs", "total_price"])(0, 75.0),
        "ID_2": namedtuple("InfoLinp", ["nb_labeled_inputs", "total_price"])(1, 87.5),  
        "ID_3": namedtuple("InfoLinp", ["nb_labeled_inputs", "total_price"])(1, 100.0),
    }
    assert label_input.apply_number_labeled_inputs(linp_files_infos, weight_labeled_input=2) == 2
   

def test_apply_price(summary_dataframe):
    label_input = Score(summary_dataframe["ID_2"])
    linp_files_infos = {
        "ID_1": namedtuple("InfoLinp", ["nb_labeled_inputs", "total_price"])(0, 75.0),
        "ID_2": namedtuple("InfoLinp", ["nb_labeled_inputs", "total_price"])(1, 87.5),  
        "ID_3": namedtuple("InfoLinp", ["nb_labeled_inputs", "total_price"])(1, 100.0),
    }
    
    assert label_input.apply_price(linp_files_infos) == 87.5

def test_structurally_identified_fluxes(summary_dataframe):
    fluxes = Score(summary_dataframe["ID_2"])
    structurally_identified_fluxes = {"ID_1": 3, "ID_2": 2, "ID_3": 1}

    assert fluxes.structurally_identified_fluxes(structurally_identified_fluxes) == 2

def test_apply_criteria_multiple_methods(summary_dataframe):
    handler = ScoreHandler(summary_dataframe.iloc[:, 5:])
    handler.apply_criteria(
        ["sum of SDs", "number of fluxes with SDs < threshold"],
        weight_sum_sd=2,
        threshold=0.1,
        weight_flux=3
    )
    # Check sum of SDs
    assert handler.columns_scores["ID_1"]["sum of SDs"] == 1.4
    assert handler.columns_scores["ID_2"]["sum of SDs"] == 1.24
    assert handler.columns_scores["ID_3"]["sum of SDs"] == 1.82
    # Check number of fluxes with SDs < threshold
    assert handler.columns_scores["ID_1"]["number of fluxes with SDs < threshold"] == 0
    assert handler.columns_scores["ID_2"]["number of fluxes with SDs < threshold"] == 3
    assert handler.columns_scores["ID_3"]["number of fluxes with SDs < threshold"] == 3

def test_apply_criteria_with_empty_column():
    df = pd.DataFrame({
        "ID_1": [],
        "ID_2": []
    })
    handler = ScoreHandler(df)
    handler.apply_criteria(
        ["sum of SDs"],
        weight_sum_sd=1
    )
    assert handler.columns_scores["ID_1"]["sum of SDs"] == 0.0
    assert handler.columns_scores["ID_2"]["sum of SDs"] == 0.0

def test_apply_operations_add(summary_dataframe):
    handler = ScoreHandler(summary_dataframe.iloc[:, 5:])
    handler.apply_criteria(
        ["sum of SDs", "number of fluxes with SDs < threshold"],
        weight_sum_sd=1,
        threshold=0.1,
        weight_flux=2
    )
    handler.apply_operations("Add")
    # For ID_1: sum of SDs = 0.7, number of fluxes with SDs < threshold = 0
    # Add: 0.7 + 0 = 0.7
    assert handler.columns_scores["ID_1"]["Add"] == 0.7
    # For ID_2: sum of SDs = 0.62, number of fluxes with SDs < threshold = 2
    # Add: 0.62 + 2 = 2.62
    assert handler.columns_scores["ID_2"]["Add"] == 2.62

def test_apply_operations_multiplication(summary_dataframe):
    handler = ScoreHandler(summary_dataframe.iloc[:, 5:])
    handler.apply_criteria(
        ["sum of SDs", "number of fluxes with SDs < threshold"],
        weight_sum_sd=2,
        threshold=0.1,
        weight_flux=3
    )
    handler.apply_operations("Multiplication")

    assert np.isclose(handler.columns_scores["ID_1"]["Multiplication"], 0.0)
    assert np.isclose(handler.columns_scores["ID_2"]["Multiplication"], 3.72)
    assert np.isclose(handler.columns_scores["ID_3"]["Multiplication"], 5.46)

def test_apply_operations_division(summary_dataframe):
    handler = ScoreHandler(summary_dataframe.iloc[:, 5:])
    handler.apply_criteria(
        ["sum of SDs", "number of fluxes with SDs < threshold"],
        weight_sum_sd=1,
        threshold=0.3,
        weight_flux=2
    )
    handler.apply_operations("Division")

    assert np.isclose(handler.columns_scores["ID_1"]["Division"], 0.175)
    assert np.isclose(handler.columns_scores["ID_2"]["Division"], 0.155)
    assert np.isclose(handler.columns_scores["ID_3"]["Division"], 0.2275)

def test_apply_operations_empty_scores():
    df = pd.DataFrame({
        "ID_1": []
    })
    handler = ScoreHandler(df)
    handler.apply_criteria(["sum of SDs"], weight_sum_sd=1)
    handler.apply_operations("Add")
    assert handler.columns_scores["ID_1"]["Add"] == 0.0


