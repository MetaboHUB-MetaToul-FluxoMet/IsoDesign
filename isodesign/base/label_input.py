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
        self.isotopomer_combinations = {}
        # Isotopomer names and labelling patterns.
        self.names = []
        self.labelling_patterns = []

    def __repr__(self):
        return "\n".join(f"{substrate_name}: {isotopomers}" for substrate_name, isotopomers in self.isotopomer_group.items())

    def generate_labelling_combinations(self):
        """
        Generate all possible combinations of label input proportions for all isotopomers group

        """
        for isotopomer_name, isotopomers in self.isotopomer_group.items():
            logger.debug(f"Running combinatory function on {isotopomer_name} group")
            # For all isotopomers present, all possible fractions are generated except for the first 
            # First isotopomer's fraction will be deduced from the other ones
            if len(isotopomers) > 1:
                fractions = [isotopomer.generate_fraction() for isotopomer in
                             isotopomers[1:]]
            else:
                fractions = [isotopomer.generate_fraction() for isotopomer in
                             isotopomers]

            logger.debug(f"Generated fractions:\n {fractions}")
            # fractions : list containing vectors of fractions of each isotopomer 
            # np.meshgrid is used to return matrices corresponding to all possible combinations of vectors present in the list of fractions
            # -1 parameter in reshape permit to adjusts the size of the first dimension (rows) according to the total number of elements in the array
            all_combinations = np.array(np.meshgrid(*fractions)).T.reshape(-1, len(fractions))

            # filter with sum <= 1 as condition 
            filtered_combinations = np.array(
                [combination for combination in all_combinations if
                 combination.sum() <= Decimal(1)])
            
            # Ensure sum of all fractions is equal to 1
            # Permit to find the fractions of the last isotopomer
            if len(isotopomers) > 1:
                deduced_fraction = 1 - filtered_combinations.sum(axis=1)
                logger.debug(f'Deduced fraction {deduced_fraction}')
                
                self.isotopomer_combinations[
                    isotopomer_name] = np.column_stack(
                    (deduced_fraction.reshape(-1, 1), filtered_combinations))
            else:
                self.isotopomer_combinations[isotopomer_name] = filtered_combinations

            self.names += [isotopomer.name for isotopomer in isotopomers]
            self.labelling_patterns += [isotopomer.labelling for isotopomer in isotopomers]

        # Addition of a key containing all isotopomers group combination if there is multiple isotopomers group 
        self.isotopomer_combinations["All_combinations"] = [
            np.concatenate(pair) for pair in product(
                *self.isotopomer_combinations.values())
        ]
    
        self._check_labelling_combinations()

    def _check_labelling_combinations(self):
        """
        Check if the sum of all fractions is equal to 1 for all isotopomers group
        """
        for isotopomer_name, isotopomer_combinations in self.isotopomer_combinations.items():
            if isotopomer_name == "All_combinations":
                continue
            if any(np.sum(combination) != 1 for combination in isotopomer_combinations):
                raise ValueError(f"Sum of all fractions is not equal to 1 for {isotopomer_name} group")
                # logger.error(f"Sum of all fractions is not equal to 1 for {isotopomer_name} group")
                    


    