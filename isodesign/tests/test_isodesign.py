from decimal import Decimal
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from isodesign.process.calculation import LabelInput, Isotopomer

def test_isotopomer_creation(isotopomer):
    for value in [isotopomer.name, isotopomer.labelling]:
        assert isinstance(value, str)
    for value in [isotopomer.step, isotopomer.lower_bound, isotopomer.upper_bound]:
        assert isinstance(value, int)

    assert isotopomer.name == "Gluc"
    assert isotopomer.labelling == "111111"
    assert isotopomer.step > 0
    assert isotopomer.lower_bound >= 0
    assert isotopomer.upper_bound <= 100
    assert isotopomer.upper_bound > isotopomer.lower_bound
    assert isotopomer.num_carbon == 6

def test_error_raise_isotopomer_creation():
    with pytest.raises(ValueError):
        # If step is less than or equal to 0 
        Isotopomer("Gluc", "111111", 0, 10, 100)
        Isotopomer("Gluc", "111111", -1, 0, 100)
        # If lower_bound is negative 
        Isotopomer("Gluc", "111111", 10, -1, 100)
        # If upper_bound is greater than 100 
        Isotopomer("Gluc", "111111", 10, 0, 120)
        # If lower_bound is greater than upper_bound
        Isotopomer("Gluc", "111111", 10, 90, 80)

    with pytest.raises(TypeError):
        # If step, lower_bound and/or upper_bound are not int
        Isotopomer("Gluc", "100000", "10", "0", "90")
        

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
    assert "glucose" in isotopomers_group.isotopomer_combination
    for combination in isotopomers_group.isotopomer_combination.values():
        for pair in combination: 
            assert sum(pair) == Decimal(1)
    
    assert isotopomers_group.names == ["Gluc", "Gluc"]
    assert isotopomers_group.labelling_patterns == ["111111", "100000"]

def test_read_files_invalid_input(process):
    with pytest.raises(TypeError):
        process.read_files(123)
    
    with pytest.raises(ValueError):
        invalid_path = Path(r"U:\Projet\IsoDesign\isodesign\test-data\e_coli2.txt")
        process.read_files(str(invalid_path.resolve()))
   
    with pytest.raises(ValueError):
        invalid_ext = Path(r"U:\Projet\IsoDesign\isodesign\test-data\e_coli.txt")
        process.read_files(str(invalid_ext.resolve()))
 

def test_invalid_netw_file(process):
    # if there is an extra column 
    with pytest.raises(ValueError):
        invalid_netw = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
            "col3": [7, 8, 9]
        })
        process._check_netw(invalid_netw, "invalid_file.netw")
    
def test_invalid_tvar_file(process):
    # If there are missing columns 
    with pytest.raises(ValueError):
        invalid_tvar = pd.DataFrame({
        "Type": ["F", "C", "D"],  
        "Kind": ["NET", "XCH", "METAB"]
        })
        process._check_tvar(invalid_tvar, "invalid_file.tvar")

    # If wrong values in "Type" column
    with pytest.raises(ValueError):
        invalid_tvar = pd.DataFrame({
        "Name": ["BM", "pgi", "pfk"],
        "Kind": ["NET", "XCH", "METAB"],
        "Type": ["X", "Y", "Z"],  
        "Value": [0.06, 0.03, 0.4]
        })
        process._check_tvar(invalid_tvar, "invalid_file.tvar")

    # If wrong values in "Kind" column
    with pytest.raises(ValueError):
        invalid_tvar = pd.DataFrame({
        "Name": ["BM", "pgi", "pfk"],
        "Kind": ["X", "Y", "Z"],
        "Type": ["F", "C", "D"],  
        "Value": [0.06, 0.03, 0.4]
        })
        process._check_tvar(invalid_tvar, "invalid_file.tvar")

def test_invalid_miso_file(process):
    # If there are missing columns 
    with pytest.raises(ValueError):
        invalid_miso = pd.DataFrame({
        "Specie": ["Ala", "Gly", "Val"],  
        "Isospecie": ["M0", "M1","M2"]
        })
        process._check_miso(invalid_miso, "invalid_file.miso")

def test_invalid_mflux_file(process):
    # If there are missing columns 
    with pytest.raises(ValueError):
        invalid_mflux = pd.DataFrame({
        "Flux": ["out_Ac", "BM"],  
        })
        process._check_mflux(invalid_mflux, "invalid_file.mflux")

def test_check_numerical_columns_invalid_values(process):
    invalid_data = pd.Series(["1", "2", "3", "abc"])
    with pytest.raises(ValueError):
        process._check_numerical_columns(invalid_data, "test_column")

def test_generation_linp_empty_combination_list(process):    
    with pytest.raises(AttributeError):
        process.labelinput.isotopomer_combination["combinations"] = None
        process.generate_linp_files("output_path")

def test_generation_vmtf_file_empty_dict(process):
    with pytest.raises(AttributeError):
        process.dict_vmtf = None
        process.generate_vmtf_file()

