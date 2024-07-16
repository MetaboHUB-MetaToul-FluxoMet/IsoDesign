import pytest
import isodesign

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
    assert isotopomer.upper_bound >= isotopomer.lower_bound
    assert isotopomer.num_carbon == 6


def test_wrong_isotopomer_creation():
    with pytest.raises(TypeError):
        isodesign.base.isotopomer.Isotopomer(1, "111111", 10, 0, 100)
        isodesign.base.isotopomer.Isotopomer("Gluc", 111111, 10, 0, 100)
        isodesign.base.isotopomer.Isotopomer("Gluc", "111111", "10", "0", "100")
    with pytest.raises(ValueError):
        isodesign.base.isotopomer.Isotopomer("Gluc", "111111", -10, 0, 100)
        isodesign.base.isotopomer.Isotopomer("Gluc", "111111", 10, -1, 100)
        isodesign.base.isotopomer.Isotopomer("Gluc", "111111", 10, 0, 101)
        isodesign.base.isotopomer.Isotopomer("Gluc", "111111", 10, 100, 0)


def test_generate_isotopomer(isotopomer_group):
    for key, value in isotopomer_group.items():
        assert isinstance(key, str)
        assert isinstance(value, list)
        for isotopomer in value:
            assert isinstance(isotopomer, isodesign.base.isotopomer.Isotopomer)


# def test_generate_labelling_combinations(isotopomer_group):
#     label_input = isodesign.base.process.LabelInput(isotopomer_group)
#     label_input.generate_labelling_combinations()
#     assert ["Gluc", "FTHF"] in label_input.isotopomer_combinations
#     for combination in label_input.isotopomer_combinations["Gluc"]:
#         assert sum(combination) == 1
    
#     assert label_input.names == ["Gluc", "Gluc", "FTHF"]
#     assert label_input.labelling_patterns == ["111111", "100000","0"]
            



 





        