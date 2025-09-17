import pytest
from isodesign.base.process import Process
import numpy as np
from decimal import Decimal as D
import pandas as pd

def test_get_netw_file_path_valid(tmp_path):
    # Create a dummy .netw file
    netw_file = tmp_path / "model.netw"
    netw_file.write_text("network content")
    process = Process()
    process.get_netw_file_path(str(netw_file))
    assert process.netw_file_path == netw_file
    assert process.metabolic_netw_model_name == "model"
    assert process.metabolic_netw_model_dir_path == tmp_path
    assert process.results_dir_path == tmp_path


def test_get_netw_file_path_invalid_type():
    process = Process()
    with pytest.raises(TypeError):
        process.get_netw_file_path(123)


@pytest.mark.parametrize(
    "invalid_path",
    [
        "missing.netw",
        "model.txt",
    ],
)
def test_get_netw_file_path_file_invalid_path(tmp_path, invalid_path):
    process = Process()
    wrong_file = tmp_path / invalid_path
    with pytest.raises(ValueError):
        process.get_netw_file_path(str(wrong_file))


@pytest.mark.parametrize(
    "name, labelling, intervals_nb, lower_bound, upper_bound",
    [("Gluc", "000000", 10, 1, 1), ("FTHF_in", "0", 10, 1, 1)],
)
def test_configure_unlabelled_form(
    netan, name, labelling, intervals_nb, lower_bound, upper_bound
):
    process = Process()
    process.netan = netan
    process.configure_unlabelled_form()
    isotopomers = process.isotopomers.get(name)
    assert isotopomers is not None
    assert len(isotopomers) == 1
    iso = isotopomers[0]
    assert iso.labelling == labelling
    assert iso.intervals_nb == intervals_nb
    assert iso.lower_bound == lower_bound
    assert iso.upper_bound == upper_bound


def test_add_isotopomer_valid(netan, isotopomer_group):
    process = Process()
    process.netan = netan
    process.isotopomers = isotopomer_group
    process.add_isotopomer("Gluc", "100000", 10, 1, 1, price=60.0)
    assert len(process.isotopomers["Gluc"]) == 3
    assert process.isotopomers["Gluc"][-1].labelling == "100000"
    assert process.isotopomers["Gluc"][-1].price == 60.0
    assert process.isotopomers["Gluc"][-1].intervals_nb == 10


@pytest.mark.parametrize(
    "invalid_labelling",
    [
        "111111",  # duplicate
        "1000000",
    ],
)
def test_add_isotopomer_invalid_labelling(netan, isotopomer_group, invalid_labelling):
    process = Process()
    process.netan = netan
    process.isotopomers = isotopomer_group
    with pytest.raises(ValueError):
        process.add_isotopomer("Gluc", invalid_labelling, 10, 0, 1)


def test_add_isotopomer_invalid_substrate(netan, isotopomer_group):
    process = Process()
    process.netan = netan
    process.isotopomers = isotopomer_group
    with pytest.raises(ValueError):
        process.add_isotopomer("Unknown", "100000", 10, 0, 1)


def test_remove_isotopomer(isotopomer_group):
    process = Process()
    process.isotopomers = isotopomer_group
    process.remove_isotopomer("Gluc", "111111")
    assert len(process.isotopomers["Gluc"]) == 1
    assert process.isotopomers["Gluc"][0].labelling == "000000"


@pytest.mark.parametrize(
    "invalid_substrate, invalid_labelling, expected_message",
    [
        ("Unknown", "000000", "not found in the isotopomers dictionary"),
        ("Gluc", "123456", "Isotopomer 123456 not found for Gluc"),
    ],
)
def test_remove_isotopomer_wrong(
    isotopomer_group, invalid_substrate, invalid_labelling, expected_message
):
    process = Process()
    process.isotopomers = isotopomer_group
    with pytest.raises(ValueError, match=expected_message):
        process.remove_isotopomer(invalid_substrate, invalid_labelling)


def test_generate_combinations_success(isotopomer_group):
    process = Process()
    process.isotopomers = isotopomer_group
    process.generate_combinations()
    assert np.array_equal(
        process.label_input.isotopomer_combinations["Gluc"],
        [[D("1"), D("0")], [D("0.5"), D("0.5")], [D("0"), D("1")]],
    )

    assert np.array_equal(
        process.label_input.isotopomer_combinations["FTHF_in"], np.array([[D("1")]])
    )

    assert np.array_equal(
        process.label_input.isotopomer_combinations["All_combinations"],
        [
            np.array([D("1"), D("0"), D("1")]),
            np.array([D("0.5"), D("0.5"), D("1")]),
            np.array([D("0"), D("1"), D("1")]),
        ],
    )

    assert process.label_input.names == ["Gluc", "Gluc", "FTHF_in"]
    assert process.label_input.labelling_patterns == ["000000", "111111", "0"]


@pytest.mark.parametrize("incorrect_isotopomer_group", [{}, {"Gluc": []}])
def test_generate_combinations_incorrect(incorrect_isotopomer_group):
    process = Process()
    process.isotopomers = incorrect_isotopomer_group
    with pytest.raises(ValueError):
        process.generate_combinations()


def test_get_isotopomer_price(isotopomer_group):
    process = Process()
    process.isotopomers = isotopomer_group
    assert process.get_isotopomer_price("000000", "Gluc") == 50
    assert process.get_isotopomer_price("111111", "Gluc") == 75
    assert process.get_isotopomer_price("0", "FTHF_in") == 25


def test_configure_linp_files(isotopomer_group, linp_dataframes):
    process = Process()
    process.isotopomers = isotopomer_group
    process.generate_combinations()
    process.configure_linp_files()

    assert process.linp_dataframes == linp_dataframes


def test_remove_linp_configuration(linp_dataframes):
    process = Process()
    process.linp_dataframes = linp_dataframes
    process.remove_linp_configuration([0, 2])

    assert "ID_1" not in process.linp_dataframes
    assert "ID_3" not in process.linp_dataframes
    assert "ID_2" in process.linp_dataframes
    assert process.linp_config_deleted == {
        0: {
            "ID_1": {
                "Id": [None, None, None],
                "Comment": [None, None, None],
                "Specie": ["Gluc", "Gluc", "FTHF_in"],
                "Isotopomer": ["000000", "111111", "0"],
                "Value": [1.0, 0.0, 1.0],
                "Price": [50.0, 0.0, 25.0],
            }
        },
        2: {
            "ID_3": {
                "Id": [None, None, None],
                "Comment": [None, None, None],
                "Specie": ["Gluc", "Gluc", "FTHF_in"],
                "Isotopomer": ["000000", "111111", "0"],
                "Value": [0.0, 1.0, 1.0],
                "Price": [0.0, 75.0, 25.0],
            }
        },
    }


def test_remove_linp_configuration_out_of_range_index(linp_dataframes):
    process = Process()
    process.linp_dataframes = linp_dataframes
    # Remove index that does not exist (should not raise, just ignore)
    # process.remove_linp_configuration([3])

    with pytest.raises(IndexError):
        process.remove_linp_configuration([4])


def test_reintegrate_linp_configuration(linp_dataframes):
    process = Process()
    process.linp_dataframes = linp_dataframes
    process.remove_linp_configuration([0, 2])
    process.reintegrate_linp_configuration([0, 2])

    assert "ID_1" in process.linp_dataframes
    assert "ID_3" in process.linp_dataframes
    assert "ID_2" in process.linp_dataframes
    assert process.linp_config_deleted == {}


def test_reintegrate_linp_configuration_invalid_index(linp_dataframes):
    process = Process()
    process.linp_dataframes = linp_dataframes
    process.remove_linp_configuration([0, 2])
    with pytest.raises(KeyError):
        process.reintegrate_linp_configuration([5])

def test_generate_score_basic(summary_dataframe):
    process = Process()
    process.summary_dataframe = summary_dataframe
    process.generate_score(method=["sum of SDs"])
    # Should create scores for columns F and G
    assert process.scores.equals(
        pd.DataFrame({"sum of SDs": [0.70, 0.62, 0.91]}, index=["ID_1", "ID_2", "ID_3"])
    )
    assert process.selected_criteria == ["sum of SDs"]


def test_log_application_on_generated_scores(summary_dataframe):
    process = Process()
    process.summary_dataframe = summary_dataframe
    process.generate_score(method=["sum of SDs"])
    process.apply_log()
    assert process.scores.equals(
        pd.DataFrame(
            {"sum of SDs": [np.log10(0.70), np.log10(0.62), np.log10(0.91)]},
            index=["ID_1", "ID_2", "ID_3"],
        )
    )
