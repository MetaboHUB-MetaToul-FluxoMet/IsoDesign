""" Module for calculation """
from itertools import product
import math
from pathlib import Path

import os
import pandas as pd
import numpy as np


class Tracer:
    """ 
    Class for the initiation of tracers

    """

    def __init__(self, name, isotopomer, step, lower_bound, upper_bound):
        """
        :param name: tracer name
        :param isotopomer: carbons labeling 
        :param step: step for proportions to test
        :param lower_bound: minimun proportion to test
        :param upper_bound: maximum proportion to test 

        """
        self.name = name
        self.isotopomer = isotopomer
        self.step = step
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        self.num_carbon = len(self.isotopomer)
        # List of possible fraction between lower_bound and upper_bound depending of the step value
        # Fractions will be used for influx_si simulations. Influx_si takes only values that are between 0 and 1
        self.fraction = [fraction/100 for fraction in range(self.lower_bound, self.upper_bound + self.step, self.step)]

    def __len__(self):
        returnd self.num_carbon

    def __repr__(self) -> str:
        return f"Molecule name: {self.name},\
        \nNumber of associated carbon(s) : {self.num_carbon},\
        \nStep = {self.step},\
        \nLower bound = {self.lower_bound},\
        \nUpper bound = {self.upper_bound},\
        \nVector of fractions = {self.fraction}"

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
        if value <= 0:
            raise ValueError("Step for proportions to test must be greater than 0")
        self._step = value


class Mix:
    def __init__(self, tracers: dict):
        """
        :param tracers: dictionary containing the different tracer 
                        mix with mix name as key and list of 
                        tracers as value   
        """

        self.tracers = tracers

        # List of all combinations inside a tracers mix and/or combination between many tracers mix
        self.mixes = []
        # Lists of all tracers names and all tracers isotopomers. They are used to facilitate the linp files generations
        self.names = []
        self.isotopomer = []

    def tracer_mix_combination(self):
        """
        Generate combination inside a tracers mix and/or 
        combination between many tracers mixes

        """

        # List contained filtered list of possible combinations between tracers inside a mix 
        # The number of list depend on the number of tracers mixes  
        filtered_combinations = []

        for metabolite, tracer_mix in self.tracers.items():
            # Create "generator" for combinations
            prod = product(*[tracer.fraction for tracer in tracer_mix])
        
            self.names += [tracer.name for tracer in tracer_mix]
            self.isotopomer += [tracer.isotopomer for tracer in tracer_mix]
            # Only combinations which their sum is equal to 1 are used for influx_si simulations
            filtered_combinations.append(list(combination for combination in prod if math.fsum(combination) == 1))
            
        
        # If multiple tracers we must build combinations between each metabolite mix
        if len(self.tracers) > 1:
            self.mixes += list(product(*filtered_combinations))
        else:
            # The only list contained in filtered_combinations is stocked
            self.mixes = filtered_combinations[0]

           

class Process:
    """
    Class responsible of most of the processes... 

    """
    
    MISO_COLUMNS = ["Specie", "Fragment", "Dataset", "Isospecies", "Value", "SD", "Time"]
    TVAR_COLUMNS = ["Name", "Kind", "Type", "Value"]
    MFLUX_COLUMNS = ["Flux", "Value", "SD"]
    NUMERICAL_COLUMNS = ["Value", "SD"]

    def __init__(self):
        """

        """
        # Init dictionary containing extension files as keys and a list of their contents (dataframes) and complete name as values
        self.data_dict = {}

        # Mix object
        self.mix = None

        # Dictionary contained element to build the vmtf file.
        self.dict_vmtf = {"Id":None, "Comment":None}

        # Dictionary contained the columns to check between the different imported files in the check_files method
        # Key : file and column name, Value : column content 
        self.check_files_dict = {}

       

    def read_files(self, data):
        """ 
        Read tvar, mflux and netw files (csv or tsv)

        :param data: str containing the path to the file

        """
        if not isinstance(data, str):
            raise TypeError(f"{data} should be of type string and not {type(data)}")

        data_path = Path(data).resolve()


        if not data_path.exists():
            raise ValueError(f"{data_path} doesn't exist.")
        else:
            ext = data_path.suffix
            if ext not in [".netw", ".tvar", ".mflux", ".miso"]:
                raise TypeError(
                    f"{data_path} is not in the good format\n Only .netw, .tvar, .mflux, .miso formats are accepted")
            
            data = pd.read_csv(str(data_path), sep="\t", comment= "#", header=None if ext == ".netw" else 'infer')

            self.data_dict.update(
                {
                    ext : [data_path.name, data]
                }
            )
            # Add in dict_vmtf the files extensions without the dot as key and files names as value 
            self.dict_vmtf.update({ext[1:]:data_path.stem})
            


    def check_files(self):
        """ 
        Check the content of each file by calling up sub-functions 
        specific to each file. Also checks whether metabolites and reactions
        present in the files are actually present in the network file. 

        """

        # Call sub-functions to check each imported file
        self._check_netw()
        self._check_tvar()
        self._check_miso()
        self._check_mflux()
            
        # Check if all the metabolites of the files matching with metabolites contained in the netw file
        # Use of the check_files_dict dictionary, which contains all the columns of the various files to be compared     
        for metabolite in self.check_files_dict["tvar_flux_name"] :
            if metabolite not in self.check_files_dict["netw_reactions_name"]:
                raise ValueError(f"'{metabolite}' from a tvar file is not in the network file")
  
        for flux in self.check_files_dict["mflux_flux"] :
            if flux not in self.check_files_dict["netw_reactions_name"]:
                raise ValueError(f"'{flux}' from a mflux file is not in the network file")

        for specie in self.check_files_dict["miso_flux"] :
            if specie not in self.check_files_dict["netw_metabolite"]:
                raise ValueError(f"'{specie}' from a miso file is not in the network file")
                

    def _check_netw(self):
        """
        Check the contents of the netw file contained in the 
        dictionary self.data_dict. Adds reaction names and metabolites 
        present in the file to the self.check_files_dict dictionary.
        """

        # Retrieve file name 
        file_name = self.data_dict[".netw"][0]

        # Checks the file contents
        if len(self.data_dict[".netw"][1].columns) > 2:
            raise ValueError(f"Number of columns isn't correct for {file_name} file")
        
        # Add reaction names without the ":" separator as sets  
        self.check_files_dict.update({"netw_reactions_name" : set(reaction[:-1] for reaction in self.data_dict[".netw"][1].iloc[:,0])})
        # Add only metabolites to the dictionary 
        netw_metabolite = set()
        for reactions in self.data_dict[".netw"][1].iloc[:,1]:
            for element in reactions.split():
                if element not in ["<->", "->", "+"]:
                    netw_metabolite.add(element)
        self.check_files_dict.update({"netw_metabolite" : netw_metabolite})       

    def _check_tvar(self):
        """
        Check the contents of the tvar contained in the dictionary 
        self.data_dict. Add the fluxes present in the self.check_files_dict 
        dictionary to compare them with the contents of the netw file.

        """
        file_name = self.data_dict[".tvar"][0]

        # Checks the file contents 
        for x in self.TVAR_COLUMNS:
            if x not in self.data_dict[".tvar"][1].columns:
                raise ValueError(f"Columns {x} is missing from {file_name}")
            if x == "Value":
                self._check_numerical_columns(self.data_dict[".tvar"][1][x], file_name)

        for x in self.data_dict[".tvar"][1]["Type"]:
            if x not in ["F", "C", "D"]:
                raise ValueError(f"'{x}' type from {file_name} is not accepted in 'Type' column. Only F, D or C type are accepted.")

        for x in self.data_dict[".tvar"][1]["Kind"]:
            if x not in ["NET","XCH", "METAB"]:
                raise ValueError(f"'{x} type from {file_name} is not accepted in 'Kind' column. Only NET, XCH or METAB type are accepted.")
        
        # Add fluxes in the "Name" column that are NET fluxes only
        self.check_files_dict.update({"tvar_flux_name" : set(self.data_dict[".tvar"][1].loc[self.data_dict[".tvar"][1]["Kind"] == "NET", "Name"])})
        
    def _check_miso(self):
        """
        Check the contents of the miso contained in the dictionary 
        self.data_dict. Add the metabolites to be compared with the 
        contents of the netw file to the self.check_files_dict dictionary.
        """
        file_name = self.data_dict[".miso"][0]

        # Check the file contents
        for x in self.MISO_COLUMNS:
            if x not in self.data_dict[".miso"][1].columns:
                raise ValueError(f"Columns {x} is missing from {file_name}")
            
        for x in self.NUMERICAL_COLUMNS:
            self._check_numerical_columns(self.data_dict[".miso"][1][x], file_name)

        # Add metabolites 
        self.check_files_dict.update({"miso_flux" : set(self.data_dict[".miso"][1]["Specie"])})
            
    
    def _check_mflux(self):
        """
        Check the contents of the mflux contained in the dictionary 
        self.data_dict. Add the feeds to be compared with the contents 
        of the netw file to the self.check_files_dict dictionary.

        """
        file_name = self.data_dict[".mflux"][0]

        # Check the file contents
        for x in self.MFLUX_COLUMNS:
            if x not in self.data_dict[".mflux"][1].columns :
                raise ValueError(f"Columns {x} is missing from {file_name}")
            
        for x in self.NUMERICAL_COLUMNS:
            self._check_numerical_columns(self.data_dict[".mflux"][1][x], file_name)
        
        # Add fluxes 
        self.check_files_dict.update({"mflux_flux" : set(self.data_dict[".mflux"][1]["Flux"])})
    
    def _check_numerical_columns(self, columns, file_name):
        """ 
        Checks that columns contain numerical values.

        :param columns: the column to be checked 
        :param file_name: name of the file 

        """
        for x in columns:
            # Convert all values to float to avoid other value types
            try:
                float(x)
            except ValueError:
                raise ValueError(f"'{x}' from {file_name} is incorrect. Only numerical values are accepted in {columns.name} column.")


    def generate_mixes(self, tracers: dict):
        """
        Generate the mixes from tracer dictionary.

        :param tracers: dictionary containing metabolites and associated tracers for mix
        """

        # Mix class object contained tracers mix combinations 
        self.mix = Mix(tracers)
        self.mix.tracer_mix_combination()

    def generate_file(self, output_path:str):
        """
        Generate linp files to a folder in the current directory depending
        of all combination for one or two mixe(s). Those files are used 
        for influx_si simulations.
        Files containing tracers features including the combinations
        for all tracer mixes.
        """

        output_path = Path(output_path)
        
        for combination in self.mix.mixes:
            df = pd.DataFrame({'Id': None,
                               'Comment': None,
                               'Specie': [],
                               'Isotopomer': [],
                               'Value': []})

            df["Specie"] = [tracer_names for tracer_names in self.mix.names]
            df["Isotopomer"] = [tracer_isotopomer for tracer_isotopomer in self.mix.isotopomer]

            if len(self.mix.tracers) > 1:
                # Tuple contained tuples with all the combination reunited 
                reunited_combination = ()
                for pair in combination:
                    reunited_combination += pair
                df["Value"] = reunited_combination
            else:
                df["Value"] = combination
        
            # Remove all row equals to 0 because linp file doesn't have value equal to 0 
            df = df.loc[df["Value"] != 0] 
            # Create the folder that stock linp files
            output_path.mkdir(exist_ok=True) 
            # Generate linp files depending on the number of combination
            # Join the files created to the new folder created before 
            df.to_csv(os.path.join(str(output_path), f"{combination}.linp"), sep="\t")

            # Add a new key "linp" with all the combinations as value
            self.dict_vmtf.update({"linp" : [f"{combination}" for combination in self.mix.mixes]})

    def generate_vmtf_file(self):
        """
        Generate a vmtf file that permit to combine variable and constant parts in 
        a set of experiment on the same organism to launch a batch of calculation.
        This file contained columns using imported files extensions. Each row contains
        imported files names that will be used to produce a ftbl file used in the calculation. 
        Each row have ftbl column with unique and non empty name. 
        """
        
        # Value convert into Series 
        # Permit to create a dataframe from a dictionary where keys have different length of value   
        df = pd.DataFrame({key:pd.Series(value) for key, value in self.dict_vmtf.items()})
        # Add a new column "ftbl" containing the values that are in the key "linp" of dict_vmtf
        # These values will be the names of the export folders of the results  
        df["ftbl"] = self.dict_vmtf["linp"]
        df.to_csv("file.vmtf", sep="\t", index=False)

    def influx_simulation(self):
        pass
    
    
    
if __name__ == "__main__":
    gluc_u = Tracer("Gluc_U", "111111", 10, 0, 100)
    gluc_1 = Tracer("Gluc_1", "100000", 10, 0, 100)
    ace_u = Tracer("Ace_U", "11", 20, 0, 100)
    ace_1 = Tracer("Ace_1", "10", 20, 0, 100)
    mix1 = {
        "gluc": [gluc_u, gluc_1]
    }
    mix2 = {
        "gluc": [gluc_u, gluc_1],
        "ace": [ace_u, ace_1]
    }
    # print("Dictionary mix1\n\n", mix1)
    # print("\nDictionary mix2\n\n", mix2)

    # print("\n***************\n")
    # Create Process class objects
    test_object1 = Process()
    test_object2 = Process()
    # test_object1.generate_mixes(mix1)
    # print(f"Combination generate for mix1 ({test_object1.mix.names}) : \n",test_object1.mix.mixes)
    # test_object2.generate_mixes(mix2)
    # print(f"\nCombination generate for mix2 ({test_object2.mix.names}) : \n",test_object2.mix.mixes)

    # print("\n***************\n")
    # test_object1.generate_file(f"{test_object1.mix.names}")
    # test_object2.generate_file(f"{test_object2.mix.names}")
    # print("Folder containing linp files has been generated on your current repertory.")

    print("\n***************\n")
    # test_object1.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\e_coli.mflux")
    # test_object1.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\e_coli.tvar")
    # test_object1.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\e_coli.netw")
    # test_object1.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\e_coli.miso")
    test_object1.read_files(r"../test-data/e_coli.mflux")
    test_object1.read_files(r"../test-data/e_coli.miso")
    test_object1.read_files(r"../test-data/e_coli.netw")
    test_object1.read_files(r"../test-data/e_coli.tvar")
    print("Imported files\n\n", test_object1.data_dict)
    test_object1.check_files()
    # print(test_object1.check_files_dict)

    print("\n***************\n")
    # test_object1.generate_vmtf_file()
    # print(f"Dictionary with all vmtf file element for this mix {test_object1.mix.names} : \n", test_object1.dict_vmtf)
    # print("\nVmtf file has been generated on your current repository.")

    
    