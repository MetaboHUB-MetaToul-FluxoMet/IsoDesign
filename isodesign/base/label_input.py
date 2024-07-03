from itertools import product
import numpy as np
import logging

from decimal import Decimal

logger = logging.getLogger(f"IsoDesign.{__name__}")

class LabelInput:
    def __init__(self, isotopomer_group: dict):
        """
        Class for the generation of all possible combinations of labelled substrates

        :param isotopomer_group: dictionary containing as key substrate name of the isotopomer group
                                and as values a list of isotopomer 
        """

        self.isotopomer_group = isotopomer_group

        # Container for all label input combination proportions
        # keys : substrate name of the isotopomers group, Values : label input combination proportions
        self.isotopomer_combination = {}
        # Isotopomer names and labelling patterns.
        self.names = []
        self.labelling_patterns = []


    def generate_labelling_combinations(self):
        """
        Generate all possible combinations of label input proportions for all isotopomers group

        """
        for isotopomer_name, isotopomer in self.isotopomer_group.items():
            logger.debug(f"Running combinatory function on {isotopomer_name} group")
            # For all isotopomers present, all possible fractions are generated except for the first 
            # First isotopomer's fraction will be deduced from the other ones
            if len(isotopomer) > 1:
                fractions = [fracs.generate_fraction() for fracs in isotopomer[1:]]
            else:
                fractions = [fracs.generate_fraction() for fracs in isotopomer]

            logger.debug(f"Generated fractions:\n {fractions}")
            # fractions : list containing vectors of fractions of each isotopomer 
            # np.meshgrid is used to return matrices corresponding to all possible combinations of vectors present in the list of fractions
            # -1 parameter in reshape permit to adjusts the size of the first dimension (rows) according to the total number of elements in the array
            all_combinations = np.array(np.meshgrid(*fractions)).T.reshape(-1, len(fractions))

            # filter with sum <= 1 as condition 
            filtered_combinations = np.array(
                [combination for combination in all_combinations if np.sum(combination) <= Decimal(1)])
            
            
            # Calculate the difference between 1 and the sum of the fractions of the other isotopomers  
            # Total sum of all fractions must equal 1
            # Permit to find the fractions of the last isotopomer
            if len(isotopomer) > 1:
                deduced_fraction = np.array([np.subtract(np.ones([len(filtered_combinations)], dtype=Decimal),
                                                         filtered_combinations.sum(axis=1))]).reshape(len(filtered_combinations),1)
                logger.debug(f'Deduced fraction {deduced_fraction}')
                self.isotopomer_combination[isotopomer_name] = np.column_stack((deduced_fraction, filtered_combinations))
            else:
                self.isotopomer_combination[isotopomer_name] = filtered_combinations

            self.names += [isotopomers.name for isotopomers in isotopomer]
            self.labelling_patterns += [isotopomers.labelling for isotopomers in isotopomer]

        if len(self.isotopomer_group) > 1:
            # Addition of a key containing all isotopomers group combination if there is multiple isotopomers group 
            self.isotopomer_combination.update({"All_combinations": [np.concatenate((*pair,)) for pair in
                                                                 list(product(*self.isotopomer_combination.values()))]})
        else:
            self.isotopomer_combination.update(
                {"combinations": np.column_stack((deduced_fraction, filtered_combinations))})