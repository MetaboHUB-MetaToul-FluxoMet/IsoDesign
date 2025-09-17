import pytest
import numpy as np
from decimal import Decimal
from isodesign.base.isotopomer import Isotopomer

@pytest.mark.parametrize("iso, expected_fractions",
                        [(Isotopomer(name="Glucose", labelling="100000", intervals_nb=4, lower_bound=0, upper_bound=1), 
                        [Decimal("0.0"), Decimal("0.25"), Decimal("0.5"), Decimal("0.75"), Decimal("1.0")]),
                        (Isotopomer(name="Glucose", labelling="100000", intervals_nb=1, lower_bound=1, upper_bound=1), 
                        [Decimal("1.0")])])


def test_generate_fraction(iso, expected_fractions):
    # iso = Isotopomer(name="Glucose", labelling="100000", intervals_nb=4, lower_bound=0, upper_bound=1)
    fractions = iso.generate_fraction()
    assert np.array_equal(fractions, expected_fractions)

