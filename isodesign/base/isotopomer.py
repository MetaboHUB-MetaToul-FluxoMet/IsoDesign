from decimal import Decimal
import numpy as np


class Isotopomer:
    """ 
    Class for the initiation of isotopomer

    """

    def __init__(self, name, labelling, intervals_nb=10, lower_bound=100, upper_bound=100, price=None):
        """
        :param name: Isotopomer name
        :param labelling: labelling for isotopomer. 1 denotes heavy isotopes while 0 denotes natural isotope.
        :param intervals_nb: number of intervals for proportions to test
        :param lower_bound: minimum proportion to test
        :param upper_bound: maximum proportion to test 
        :param price: isotopomer price

        """
        self.name = name
        self.labelling = labelling
        self.intervals_nb = intervals_nb
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.price = price

    def generate_fraction(self):
        """
        Generate numpy array containing list of possible fraction 
        between lower_bound and upper_bound depending of the step value. 
        Fractions will be used for influx_si simulations. Influx_si takes 
        only values that are between 0 and 1.

        :return: numpy array containing list of possible fraction
        """
        # If the step value is 0, we cannot generate a range of fractions as it would cause a ZeroDivisionError.
        # In this case, we return a numpy array containing a single value of 1.
        # This represents 100% of the substrate by default.
        # This is useful for isotopomers that are not supposed to be tested for different proportions.
        if self.step == 0:
            return np.array([Decimal(1)])

        # Convert "fraction" to int to avoid type errors when using np.arange
        return np.array([Decimal(int(fraction)) / Decimal(100) for fraction in
                         np.arange(self.lower_bound, self.upper_bound + self.step, self.step)])


    def __repr__(self) -> str:
        return f"\nName = {self.name},\
        \nLabelling = {self.labelling},\
        \nNumber of intervals = {self.intervals_nb},\
        \nLower bound = {self.lower_bound},\
        \nUpper bound = {self.upper_bound},\
        \nPrice = {self.price}\n"
        

    @property
    def lower_bound(self):
        return self._lower_bound

    @lower_bound.setter
    def lower_bound(self, value):
        if not isinstance(value, int):
            raise TypeError("Lower bound must be an integer")
        if value < 0:
            raise ValueError("Lower bound for a tracer proportion must be a positive number")
        self._lower_bound = value

    @property
    def upper_bound(self):
        return self._upper_bound

    @upper_bound.setter
    def upper_bound(self, value):
        if not isinstance(value, int):
            raise TypeError("Upper bound must be an integer")
        if value > 100:
            raise ValueError("Proportions are given as a percentage and thus cannot be higher than 100%")
        if hasattr(self, "lower_bound") and value < self.lower_bound:
            raise ValueError("Upper bound must be greater than lower bound")
        self._upper_bound = value

    @property
    def intervals_nb(self):
        return self._intervals_nb

    @intervals_nb.setter
    def intervals_nb(self, value):
        if not isinstance(value, int):
            raise TypeError("Number of intervals must be an integer")
        if value <= 0:
            raise ValueError("Number of intervals must be greater than 0")
        self._intervals_nb = value

    @property
    def labelling(self):
        return self._labelling
    
    @labelling.setter
    def labelling(self, value):
        for label in value:
            if label not in ["0", "1"]:
                raise ValueError("Labelling must be either 0 (unlabeled) or 1 (labeled).")
        self._labelling = value

    @property
    def step(self): 
        return (self.upper_bound - self.lower_bound) / self.intervals_nb

