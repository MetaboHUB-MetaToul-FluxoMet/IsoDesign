""" Module for calculation """
from itertools import product, combinations
import math

import pandas as pd


class Tracer:
    """ 
    Class for the initiation of tracers.

    """

    def __init__(self, name, isotopomer, step, lower_bound, upper_bound):
        """
        :param name: tracer name
        :param isotopomer: carbons labeling 
        :param step: step for proportions to test
        :param lower_bound: minimun proportion to test
        :param upper_bound: maximum proportion to test 

        :param self.num_carbon: carbon number from isotopomer count
        :param self.fraction: list of possible fraction between 
                            lower_bound and upper_bound depending 
                            of the step value
        """
        self.name = name
        self.isotopomer = isotopomer
        self.num_carbon = len(self.isotopomer)
        self.step = step
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.fraction = [fraction for fraction in range(self.lower_bound, self.upper_bound + self.step, self.step)]
       
    def __len__(self):
        return self.num_carbon

    def __repr__(self) -> str:
        return f"Molecule name: {self.name},\nNumber of associated carbon(s) : {self.num_carbon}\nStep = {self.step}\nLower bound = {self.lower_bound}\n Upper bound = {self.upper_bound}\n Vector of fractions = {self.fraction}"
    
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
    def step(self):
        return self._step
    
    @step.setter
    def step(self, value):
        if not isinstance(value, int):
            raise TypeError("Step for proportions to test must be an integer")
        if value <= 0 :
            raise ValueError("Step for proportions to test must be greater than 0")
        self._step = value


class Mix:
    def __init__(self, tracers: dict):
        """
        :param tracers: dictionnary containing the different tracer 
                        groups with group name as key and list of 
                        tracers as value   

        :param self.mixes: list of all combinations inside a tracers group 
                            and/or combination between many tracers groups 
        :param self.names: list of all tracers names
        """
    
        self.tracers = tracers
        self.mixes = []
        self.names = []

    def tracer_mix_combination(self):
        """
        Generate combination inside a tracers group and/or 
        combination between many tracers groups

        """
        intermediate_combination = [] #list containing lists of combinations inside a tracers mix
        intermediate_name = [] #list containing lists of tracers names 

        for metabolite, tracer_mix in self.tracers.items():
            prod = product(*[tracer.fraction for tracer in tracer_mix])
            intermediate_name.append([tracer.name for tracer in tracer_mix])
            intermediate_combination.append(list(combination for combination in prod if math.fsum(combination) == 100))
        
        for names in intermediate_name:
            self.names += names 

        if len(self.tracers) > 1:
            self.mixes += list(product(*intermediate_combination))
        else:
            self.mixes = intermediate_combination
        

class Process:
    def __init__(self):
        pass

    def input_files(self):
        pass

    def generate_files(self):
        pass

    def influx_simulation(self):
        pass

if __name__ == "__main__":
    gluc_u = Tracer("Gluc_U", "111111", 10, 20, 100)
    gluc_1 = Tracer("Gluc_1", "100000", 20, 20, 100)
    gluc_23 = Tracer("Gluc_23", "011000", 10, 10, 100)
    ace_u = Tracer("Ace_U", "11", 10, 0, 100)
    ace_1 = Tracer("Ace_1", "10", 10, 0,100)
    tracers = {
        "gluc": [gluc_u, gluc_1, gluc_23],
        "ace" : [ace_u, ace_1]
    }
    mix = Mix(tracers)
    mix.tracer_mix_combination()
    print(mix.mixes)
    print(mix.names)
    #mix.tracer_mix_combination()
    #print(mix.names)
    # for key, value in mix.mixes.items():
    #     print(f"{key}: {value}")
    # print(generate_mixes_comb([gluc_u.name, gluc_1.name], [ace_u.name, ace_1.name]))
    # ace_U = Tracer("Ace_U", 11)
    # ace_1 = Tracer("Ace_1", 10)
    #generate_file([gluc_u, gluc_1], [ace_u, ace_1], [eth_1, eth_2])
    # Get for Acetate
    # mol_2 = comb_fraction(2,0,100,10)
    # print(mol_2)
