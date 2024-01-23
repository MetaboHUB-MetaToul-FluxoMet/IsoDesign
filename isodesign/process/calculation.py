""" Module for calculation """
import os
from itertools import product, combinations
import math

import pandas as pd
import numpy as np

class Tracer:
    """ 
    Class for the initiation of tracers.

    """

    def __init__(self, name, labeling, step, lower_bound, upper_bound):
        self.name = name
        self.labeling = labeling
        self.num_carbon = len(self.labeling)
        self.step = step
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.fraction = [fraction for fraction in range(self.lower_bound, self.upper_bound + self.step, self.step)]
       
    def __len__(self):
        return self.num_carbon

    def __repr__(self) -> str:
        return f"Molecule name: {self.name}, Number of associated carbon(s) : {self.num_carbon}"
    
    @property
    def lower_bound(self):
        return self._lower_bound
    
    @lower_bound.setter
    def lower_bound(self, value):
        if value < 0:
            raise ValueError(f"{value} isn't correct. Use a positive value.")
        self._lower_bound = value

    @property
    def upper_bound(self):
        return self._upper_bound
    
    @upper_bound.setter
    def upper_bound(self, value):
        if value > 100:
            raise ValueError(f"{value} isn't correct. Value must be less than 100.")
        self._upper_bound = value

class Mix:
    def __init__(self, tracers: dict):
        """
        :param tracers: dictionnary containing the different tracer 
                        groups with gourp name as key and list of 
                        tracers as value    
        """
        self.tracers = tracers
        self.mixes = {}

        # self.combination_mix = list(product(*[tracer.fraction for tracer in self.mix]))
        
    def mix_combination(self):
        """
        Generate combinations for one or more mix(es)

        :return:  list of tuples of tuples...

        """

        for metabolite, tracer_mix in self.tracers.items():
            prod = product(*[tracer.fraction for tracer in tracer_mix])
            self.mixes.update({metabolite : [combination for combination in prod if math.fsum(combination) == 100]})

        if len(self.mixes) > 1:
            pass

        # if len(self.tracers) > 1:
        #     list_all_combination = [self.combination_mix]
        #     for args in self.args:
        #         list_all_combination.append(list(product(*[tracer.fraction for tracer in args])))
        #     return list(product(*list_all_combination))
        # else:
        #     return self.combination_mix
        

if __name__ == "__main__":
    # Get for Glucose
    # final = generate_mixes_comb(["Ace_U", "Ace_1"], ["Gluc_U", "Gluc_1", "Gluc_23"])
    # print(final)
    # print(mol_1)
    # print(mol_2)
    # #print(mol_1)
    # #mol = inter_mol_comb(["Gluc_U", "Gluc_1", "Gluc_23"], ["Ace_U", "Ace_1"], 10, 0,100)
    # #print(mol)
    gluc_u = Tracer("Gluc_U", "111111", 10, 30, 100)
    #print(gluc_u.combination)
    gluc_1 = Tracer("Gluc_1", "100000", 20, 20, 100)
    gluc_23 = Tracer("Gluc_23", "011000", 10, 50, 100)
    ace_u = Tracer("Ace_U", "11", 30, 0, 100)
    ace_1 = Tracer("Ace_1", "10", 10,30,100)
    #print(gluc_1.combination)
    # tracers = {
    #     "gluc": [gluc_u, gluc_1, gluc_23],
    #     "ace": [ace_u, ace_1]
    # }
    # mix = Mix(tracers)
    # mix.mix_combination()
    #for key, value in mix.mixes.items():
        #print(f"{key}: {value}")
    # print(generate_mixes_comb([gluc_u.name, gluc_1.name], [ace_u.name, ace_1.name]))
    # ace_U = Tracer("Ace_U", 11)
    # ace_1 = Tracer("Ace_1", 10)
    #generate_file([gluc_u, gluc_1], [ace_u, ace_1], [eth_1, eth_2])
    # Get for Acetate
    # mol_2 = comb_fraction(2,0,100,10)
    # print(mol_2)
