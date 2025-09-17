import numpy as np
from decimal import Decimal as D
from isodesign.base.label_input import LabelInput


def test_generate_labelling_combinations(isotopomer_group):
    label_input = LabelInput(isotopomer_group)
    label_input.generate_labelling_combinations()
    # Should have 3 combinations: iso1 fraction = 1-x, iso2 fraction = x
    expected = np.array(
        [
            np.array([D("1"), D("0"), D("1")]),
            np.array([D("0.5"), D("0.5"), D("1")]),
            np.array([D("0"), D("1"), D("1")]),
        ],
    )
    assert np.array_equal(label_input.isotopomer_combinations["All_combinations"], expected)
    assert label_input.names == ["Gluc", "Gluc", "FTHF_in"]
    assert label_input.labelling_patterns == ["000000", "111111", "0"]


# def test_single_isotopomer_group_single_isotopomer():
#     iso1 = Isotopomer("Gluc", "100000", 1, 1, 1)
#     group = {"Gluc": [iso1]}
#     label_input = LabelInput(group)
#     label_input.generate_labelling_combinations()
#     # combos = label_input.isotopomer_combinations["Gluc"]
#     expected = np.array([[Decimal(1)]])
#     assert np.array_equal(label_input.isotopomer_combinations["Gluc"], expected)
#     assert label_input.names == ["Gluc"]
#     assert label_input.labelling_patterns == ["100000"]


# def test_multiple_isotopomer_groups():
#     isoA1 = Isotopomer("Gluc", "100000", 2, 0, 1)
#     isoA2 = Isotopomer("Gluc", "100000", 2, 0, 1)
#     isoB1 = Isotopomer("Ace", "10", 1, 1, 1)
#     group = {"A": [isoA1, isoA2], "B": [isoB1]}
#     label_input = LabelInput(group)
#     label_input.generate_labelling_combinations()
#     combos_A = label_input.isotopomer_combinations["A"]
#     combos_B = label_input.isotopomer_combinations["B"]
#     all_combos = label_input.isotopomer_combinations["All_combinations"]
#     # combos_A: [[1,0],[0,1]]
#     # expected_A = np.array([
#     #     [Decimal(1), Decimal(0)],
#     #     [Decimal(0.5), Decimal(0.5)],
#     #     [Decimal(0), Decimal(1)]
#     # ])
#     assert np.array_equal(
#         combos_A,
#         np.array(
#             [
#                 [Decimal(1), Decimal(0)],
#                 [Decimal(0.5), Decimal(0.5)],
#                 [Decimal(0), Decimal(1)],
#             ]
#         ),
#     )
#     # combos_B: [[1]]
#     assert np.array_equal(combos_B, np.array([[Decimal(1)]]))
#     # # all_combos: combinations of A and B
#     expected_all = [
#         np.array([Decimal(1), Decimal(0), Decimal(1)]),
#         np.array([Decimal(0.5), Decimal(0.5), Decimal(1)]),
#         np.array([Decimal(0), Decimal(1), Decimal(1)]),
#     ]
#     # expected_all = [
#     #     np.array([Decimal(1), Decimal(0), Decimal(1)]),
#     #     np.array([Decimal(0), Decimal(1), Decimal(1)])
#     # ]
#     # for combo, expected in zip(all_combos, expected_all):
#     #     assert np.array_equal(combo, expected)
#     assert np.array_equal(all_combos, expected_all)
#     assert label_input.names == ["Gluc", "Gluc", "Ace"]
#     assert label_input.labelling_patterns == ["100000", "100000", "10"]


# def test_invalid_fraction_sum_raises():
#     # This will create a combination where sum != 1
#     iso1 = Isotopomer("Gluc", "100000", 2, 0, 1)
#     # iso2 = DummyIsotopomer("Gluc", "lab2", [Decimal(0.6)])
#     group = {"substrateA": [iso1]}
#     label_input = LabelInput(group)
#     # Should raise ValueError in _check_labelling_combinations
#     with pytest.raises(ValueError):
#         label_input.generate_labelling_combinations()
