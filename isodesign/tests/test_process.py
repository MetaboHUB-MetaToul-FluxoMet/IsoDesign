import pytest
# from isodesign.base.process import Process
from isodesign.base.isotopomer import Isotopomer
import numpy as np
from decimal import Decimal as D

def test_configure_unlabelled_form(process):
    process.configure_unlabelled_form()
    assert len(process.isotopomers["Gluc"]) == 1
    assert process.isotopomers["Gluc"][0].labelling == "000000"
    assert process.isotopomers["Gluc"][0].intervals_nb == 10
    assert process.isotopomers["Gluc"][0].lower_bound == 100
    assert process.isotopomers["Gluc"][0].upper_bound == 100
    assert process.isotopomers["Gluc"][0].price is None

    assert len(process.isotopomers["FTHF_in"]) == 1
    assert process.isotopomers["FTHF_in"][0].labelling == "0"
    assert process.isotopomers["FTHF_in"][0].intervals_nb == 10
    assert process.isotopomers["FTHF_in"][0].lower_bound == 100
    assert process.isotopomers["FTHF_in"][0].upper_bound == 100
    assert process.isotopomers["FTHF_in"][0].price is None

def test_add_isotopomer_valid(process):
    process.isotopomers = {"Gluc": [Isotopomer("Gluc", "000000", 10, 0, 100)]}  
    process.add_isotopomer("Gluc", "100000", 10, 0, 100)
    assert len(process.isotopomers["Gluc"]) == 2
    assert process.isotopomers["Gluc"][1].labelling == "100000"
 
def test_add_isotopomer_invalid_length(process):
    with pytest.raises(ValueError, match="Number of atoms for Gluc should be equal to 6"):
        process.add_isotopomer("Gluc", "10000", 10, 0, 100)

def test_add_isotopomer_duplicate_labelling(process):
    process.isotopomers = {"Gluc": [Isotopomer("Gluc", "100000", 10, 0, 100)]}  
    with pytest.raises(ValueError, match="Isotopomer 100000 already exists for Gluc"):
        process.add_isotopomer("Gluc", "100000", 10, 0, 100)

def test_remove_isotopomer(process):
    process.isotopomers = {"Gluc": [Isotopomer("Gluc", "100000", 10, 0, 100)]}  
    process.add_isotopomer("Gluc", "111111", 10, 0, 100)
    process.remove_isotopomer("Gluc", "111111")
    assert len(process.isotopomers["Gluc"]) == 1
    assert process.isotopomers["Gluc"][0].labelling == "100000"  

def test_generate_combinations_no_isotopomers(process):
    with pytest.raises(ValueError, match="No isotopomers have been added. Please add at least one isotopomer."):
        process.generate_combinations()

def test_generate_combinations_empty_isotopomers(process):
    process.isotopomers = {"Gluc": []}
    with pytest.raises(ValueError, match="No isotopomers for Gluc. Please add at least one isotopomer."):
        process.generate_combinations()

def test_generate_combinations_success(process):
    process.isotopomers = {
        "Gluc": [Isotopomer("Gluc", "100000", 2, 0, 100),
                 Isotopomer("Gluc", "111111", 2, 0, 100)],
        "FTHF_in": [Isotopomer("FTHF_in", "0", 100, 100, 100)]
    }

    process.generate_combinations()
    
    assert np.array_equal(process.label_input.isotopomer_combinations["Gluc"], np.array([[D("1"), D("0")],
                                                                                        [D("0.5"), D("0.5")],
                                                                                        [D("0"), D("1")]]))
    
    assert np.array_equal(process.label_input.isotopomer_combinations["FTHF_in"], np.array([[D("1")]]))
    
    assert np.array_equal(process.label_input.isotopomer_combinations["All_combinations"], [np.array([D("1"), D("0"), D("1")]),
                                                                                            np.array([D("0.5"), D("0.5"), D("1")]),
                                                                                            np.array([D("0"), D("1"), D("1")])])

    assert process.label_input.names == ["Gluc", "Gluc", "FTHF_in"]
    assert process.label_input.labelling_patterns == ["100000", "111111", "0"]

def test_configure_linp_files(process):
    process.isotopomers = {
        "Gluc": [Isotopomer("Gluc", "100000", 2, 0, 100),
                 Isotopomer("Gluc", "111111", 2, 0, 100)],
        "FTHF_in": [Isotopomer("FTHF_in", "0", 100, 100, 100)]
    }

    process.generate_combinations()
    process.configure_linp_files()

    assert process.linp_dataframes == {
        "ID_1": {"Id": [None, None], "Comment" : [None, None], "Specie" : ["Gluc", "FTHF_in"], "Isotopomer" : ["100000","0"], "Value" : [1.0, 1.0], "Price" : [np.nan, np.nan]},
        "ID_2": {"Id": [None, None, None], "Comment" : [None, None, None], "Specie" : ["Gluc", "Gluc", "FTHF_in"], "Isotopomer" : ["100000","111111","0"], "Value" : [0.5, 0.5, 1.0], "Price" : [np.nan, np.nan, np.nan]},
        "ID_3": {"Id": [None, None], "Comment" : [None, None], "Specie" : ["Gluc", "FTHF_in"], "Isotopomer" : ["111111", "0"], "Value" : [1.0, 1.0], "Price" : [np.nan, np.nan]}
        }

def test_remove_linp_configuration(process):
    process.remove_linp_configuration([0, 2])
    
    assert "ID_1" not in process.linp_dataframes
    assert "ID_3" not in process.linp_dataframes
    assert "ID_2" in process.linp_dataframes
    assert process.linp_to_remove == {
        0: {"ID_1": {"Id": [None, None], "Comment" : [None, None], "Specie" : ["Gluc", "FTHF_in"], "Isotopomer" : ["100000","0"], "Value" : [1.0, 1.0], "Price" : [np.nan, np.nan]}},
        2: {"ID_3": {"Id": [None, None], "Comment" : [None, None], "Specie" : ["Gluc", "FTHF_in"], "Isotopomer" : ["111111", "0"], "Value" : [1.0, 1.0], "Price" : [np.nan, np.nan]}}
        }

def test_reintegrate_linp_configuration(process):
    process.remove_linp_configuration([0, 2])
    process.reintegrate_linp_configuration([0, 2])
    
    assert "ID_1" in process.linp_dataframes
    assert "ID_3" in process.linp_dataframes
    assert "ID_2" in process.linp_dataframes
    assert process.linp_to_remove == {}

def test_reintegrate_linp_configuration_invalid_index(process):
    process.remove_linp_configuration([0, 2])
    with pytest.raises(KeyError):
        process.reintegrate_linp_configuration([5])

