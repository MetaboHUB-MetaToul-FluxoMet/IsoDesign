""" Module for calculation """
from itertools import product
from pathlib import Path

import subprocess
import os
import shutil 
import pandas as pd
import numpy as np
from decimal import Decimal, getcontext

# import timeit

class Isotopomer:
    """ 
    Class for the initiation of tracers

    """

    def __init__(self, name, labelling, step, lower_bound, upper_bound):
        """
        :param name: Isotopomer name
        :param labelling: labelling for isotopomer. 1 denotes heavy isotopes while 0 denotes natural isotope.
        :param step: step for proportions to test
        :param lower_bound: minimum proportion to test
        :param upper_bound: maximum proportion to test 

        """
        self.name = name
        self.labelling = labelling
        self.step = step
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        self.num_carbon = len(self.labelling)
       
        
    def generate_fraction(self):
        """
        Generate numpy array containing list of possible fraction 
        between lower_bound and upper_bound depending of the step value.
        Fractions will be used for influx_si simulations. Influx_si takes 
        only values that are between 0 and 1.
        """

        # getcontext().prec = 3
        return np.array([Decimal(fraction)/Decimal(100) for fraction in range(self.lower_bound, self.upper_bound + self.step, self.step)])

    def __len__(self):
        return self.num_carbon

    def __repr__(self) -> str:
        return f"Molecule name: {self.name},\
        \nNumber of associated carbon(s) : {self.num_carbon},\
        \nStep = {self.step},\
        \nLower bound = {self.lower_bound},\
        \nUpper bound = {self.upper_bound}"

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


class LabelInput:
    def __init__(self, isotopomers_group: dict):
        """
        Class containing the logic for handling labelling input generation for influx_si simulations.

        :param isotopomers: dictionary of isotopomers
        """
        
        self.isotopomers_group = isotopomers_group

        # Container for all label input combinations
        # keys : substrate name of the isotopomers group, Values : label input combinations
        self.isotopomers_combination = {}
        # Isotopomer names and labelling patterns.
        self.names = []
        self.patterns = []

    def generate_labelling_combinations(self):
        """
        Generate combination inside a isotopomers group and/or 
        combination between isotopomers group.

        """
        for name_isotopomers, isotopomers in self.isotopomers_group.items():
            # All isotopomers fractions are generated except for the first one 
            # First isotopomer's fraction will be deduced from the other ones
            fractions = [fracs.generate_fraction() for fracs in isotopomers[1:]]
            all_combinations = np.array(np.meshgrid(*fractions)).T.reshape(-1, len(fractions))
            filtered_combinations = np.array([combination for combination in all_combinations if np.sum(combination) <= Decimal(1)])
            first_isotopomer_fraction = np.subtract(np.ones([len(filtered_combinations)], dtype=Decimal), filtered_combinations.sum(axis=1))
            self.isotopomers_combination[name_isotopomers] = np.column_stack((first_isotopomer_fraction, filtered_combinations))
            
            self.names += [isotopomers.name for isotopomers in isotopomers]
            self.patterns += [isotopomers.labelling for isotopomers in isotopomers]
            
        if len(self.isotopomers_group) > 1 :
            # Addition of a key containing all isotopomers group combination if there is multiple isotopomers group 
            self.isotopomers_combination.update({"combinations" : [np.concatenate((*pair,)) for pair in list(product(*self.isotopomers_combination.values()))]})
        else:
            self.isotopomers_combination.update({"combinations" : np.column_stack((first_isotopomer_fraction, filtered_combinations))})   
        
class Process:
    """
    Class responsible of most of the processes... 

    """
    FILES_EXTENSION = [".netw", ".tvar", ".mflux", ".miso",".cnstr"]
    MISO_COLUMNS = ["Specie", "Fragment", "Dataset", "Isospecies", "Value", "SD", "Time"]
    TVAR_COLUMNS = ["Name", "Kind", "Type", "Value"]
    MFLUX_COLUMNS = ["Flux", "Value", "SD"]
    NUMERICAL_COLUMNS = ["Value", "SD"]

    def __init__(self):
        # Dictionary to store imported file contents. Keys are file full names, contents are stored as values
        self.data_dict = {}

        # Mix object
        self.mix = None

        # Dictionary containing element to build the vmtf file.
        self.dict_vmtf = {"Id": None, "Comment": None}
        
        # Path to the folder containing all the linp files
        self.path_linp_folder = None

        # Dictionary contained the columns to check between the different imported files in the check_files method
        # Key : file and column name, Value : column content 
        self.files_matching_dict = {}

    def read_files(self, data):
        """ 
        Read tvar, mflux, miso, cnstr and netw files (csv or tsv)

        :param data: str containing the path to the file

        """
        if not isinstance(data, str):
            raise TypeError(f"{data} should be of type string and not {type(data)}")

        data_path = Path(data).resolve()

        if not data_path.exists():
            raise ValueError(f"{data_path} doesn't exist.")

        ext = data_path.suffix
        if ext not in self.FILES_EXTENSION:
            raise TypeError(
                f"{data_path} is not in the good format\n Only .netw, .tvar, .mflux, .miso, .cnstr formats are accepted")

        data = pd.read_csv(str(data_path), sep="\t", comment="#", header=None if ext == ".netw" else 'infer')

        match ext:
            case ".tvar":
                self._check_tvar(data, data_path.name)
            case ".netw":
                self._check_netw(data, data_path.name)
            case ".miso":
                self._check_miso(data, data_path.name)
            case ".mflux":
                self._check_mflux(data, data_path.name)

        shutil.copy(data_path, self.path_linp_folder)

        self.data_dict.update({data_path.name: data})
        # Add in dict_vmtf the files extensions without the dot as key and files names as value 
        self.dict_vmtf.update({ext[1:]: data_path.stem})

    def check_files_matching(self):
        """ 
        Check if metabolites and reactions present in 
        the files are actually present in the network file. 

        """

        # Use of the files_matching_dict dictionary, which contains all the columns of the various files to be compared     
        for reaction_name in self.files_matching_dict["tvar_reactions_name"]:
            if reaction_name not in self.files_matching_dict["netw_reactions_name"]:
                raise ValueError(f"'{reaction_name}' from a tvar file is not in the network file")

        for flux in self.files_matching_dict["mflux_flux"]:
            if flux not in self.files_matching_dict["netw_reactions_name"]:
                raise ValueError(f"'{flux}' from a mflux file is not in the network file")

        for specie in self.files_matching_dict["miso_species"]:
            if specie not in self.files_matching_dict["netw_metabolite"]:
                raise ValueError(f"'{specie}' from a miso file is not in the network file")

    def _check_netw(self, data, filename):
        """
        Check the contents of a netw file. Add reaction names and 
        reactions present in the file in self.files_matching_dict 
        dictionary to compare them with the reactions present in 
        the other files.

        :param data: Dataframe with file contents
        :param filename: complete file name
        """

        # Checks the file contents
        if len(data.columns) > 2:
            raise ValueError(f"Number of columns isn't correct for {filename} file")

        # Add reaction names without the ":" separator as sets  
        self.files_matching_dict.update({"netw_reactions_name": set(reaction[:-1] for reaction in data.iloc[:, 0])})
        # Add only metabolites and atom mapping to the dictionary 
        netw_metabolite = set()
        for reactions in data.iloc[:, 1]:
            for element in reactions.split():
                if element not in ["<->", "->", "+"]:
                    netw_metabolite.add(element)
        self.files_matching_dict.update({"netw_metabolite": netw_metabolite})

    def _check_tvar(self, data, filename):
        """
        Check the contents of a tvar file. Add the reactions present 
        in the file in the self.files_matching_dict dictionary to compare 
        them with the reactions names present in netw files.
        
        :param data : Dataframe with file contents
        :param filename : complete file name
        """
        # Checks the file contents 
        for x in self.TVAR_COLUMNS:
            if x not in data.columns:
                raise ValueError(f"Columns {x} is missing from {filename}")
            if x == "Value":
                self._check_numerical_columns(data[x], filename)

        for x in data["Type"]:
            if x not in ["F", "C", "D"]:
                raise ValueError(
                    f"'{x}' type from {filename} is not accepted in 'Type' column. Only F, D or C type are accepted.")

        for x in data["Kind"]:
            if x not in ["NET", "XCH", "METAB"]:
                raise ValueError(
                    f"'{x} type from {filename} is not accepted in 'Kind' column. Only NET, XCH or METAB type are accepted.")

        # Add reactions in the "Name" column with NET fluxes only
        self.files_matching_dict.update({"tvar_reactions_name": set(data.loc[data["Kind"] == "NET", "Name"])})

    def _check_miso(self, data, filename):
        """
        Check the contents of a miso file. Add the species names present 
        in the file in the self.files_matching_dict dictionary to compare 
        them with the reactions present in netw files.
        
        :param data : Dataframe with file contents
        :param filename : complete file name
        """

        # Check the file contents
        for x in self.MISO_COLUMNS:
            if x not in data.columns:
                raise ValueError(f"Columns {x} is missing from {filename}")

        for x in self.NUMERICAL_COLUMNS:
            self._check_numerical_columns(data[x], filename)

        # Add species
        self.files_matching_dict.update({"miso_species": set(data["Specie"])})

    def _check_mflux(self, data, filename):
        """
        Check the contents of a mflux file. Add the fluxes present 
        in the file in the self.files_matching_dict dictionary to compare 
        them with metabolites present in reactions in netw files.
        
        :param data : Dataframe with file contents
        :param filename : complete file name

        """

        # Check the file contents
        for x in self.MFLUX_COLUMNS:
            if x not in data.columns:
                raise ValueError(f"Columns {x} is missing from {filename}")

        for x in self.NUMERICAL_COLUMNS:
            self._check_numerical_columns(data[x], filename)

        # Add fluxes 
        self.files_matching_dict.update({"mflux_flux": set(data["Flux"])})

    def _check_numerical_columns(self, column, file_name):
        """ 
        Check that column contain numerical values.

        :param column: the column to be checked 
        :param file_name: name of the file 

        """
        for x in column:
            # Convert all values to float to avoid other value types
            try:
                float(x)
            except ValueError:
                raise ValueError(
                    f"'{x}' from {file_name} is incorrect. Only numerical values are accepted in {column.name} column.")

    def generate_mixes(self, tracers: dict):
        """
        Generate the mixes from tracer dictionary.

        :param tracers: dictionary containing metabolites and associated tracers for mix
        """

        # Mix class object contained tracers mix combinations 
        self.mix = LabelInput(tracers)
        self.mix.generate_labelling_combinations()

    def generate_file(self, output_path: str):
        """
        Generate linp files to a folder in the current directory depending 
        of all combinations for one or multiple isotopomers groups. 
        Those files are used for influx_si simulations.
        Files have a number as name and contained isotopomers 
        features including the combinations for all isotopomer group.

        A file is generated containing all the file number and combinations 
        informations. 
        """
        
        counter = 1

        # Create the folder that stock linp files if is doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self.path_linp_folder = os.path.abspath(output_path)

        with open(os.path.join(str(output_path), 'files_combinations.txt'), 'w', encoding="utf-8") as f:
            for pair in self.mix.isotopomers_combination["combinations"]:
                df = pd.DataFrame({'Id': None,
                                    'Comment': None,
                                    'Specie': [],
                                    'Isotopomer': [],
                                    'Value': []})

                df["Specie"] = list(self.mix.names)
                df["Isotopomer"] = list(self.mix.patterns) 
                df["Value"] = pair
                df = df.loc[df["Value"] != 0]
                
                df.to_csv(os.path.join(str(output_path), f"{counter}.linp"), sep="\t")   
                f.write(f"File {counter} - {self.mix.names}\n {[float(decimal_value) for decimal_value in pair]} \n") 
                # Add a new key "linp" with all the combinations as value
                self.dict_vmtf.update({"linp":  [f"{number_file}" for number_file in range(1, counter+1)]})
                counter += 1

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
        df = pd.DataFrame({key: pd.Series(value) for key, value in self.dict_vmtf.items()})
        # Add a new column "ftbl" containing the values that are in the key "linp" of dict_vmtf
        # These values will be the names of the export folders of the results  
        df["ftbl"] = self.dict_vmtf["linp"]
        vmtf_file_name = self.dict_vmtf["netw"]
        df.to_csv(f"{self.path_linp_folder}/{vmtf_file_name}.vmtf", sep="\t", index=False)

    def influx_simulation(self):
        """
        Methode using influx_si for the test by using subprocess.
        """

        # Going to the folder containing all the file to use for influx_si
        os.chdir(self.path_linp_folder)
        prefix = self.dict_vmtf["netw"]
        subprocess.run(["influx_s", "--prefix", prefix, "--mtf", f"{prefix}.vmtf", "--noopt"], shell=True, check=True)


if __name__ == "__main__":
    gluc_u = Isotopomer("Gluc", "111111", 10, 0, 100)
    gluc_1 = Isotopomer("Gluc", "100000", 10, 0, 100)
    gluc = Isotopomer("Gluc", "000000", 10, 0, 100)
    ace_u = Isotopomer("Ace_U", "11", 20, 0, 100)
    ace_1 = Isotopomer("Ace_1", "10", 20, 0, 100)
    mix1 = {
        "gluc": [gluc, gluc_u]
    }
    mix2 = {
        "gluc": [gluc, gluc_u],
        "ace": [ace_u, ace_1]
    }
    print("Dictionary mix1\n\n", mix1)
    print("\nDictionary mix2\n\n", mix2)

    print("\n***************\n")
    # Create Process class objects
    test_object1 = Process()
    test_object2 = Process()
    test_object1.generate_mixes(mix1)
    print(f"Combination generate for mix1 ({test_object1.mix.names}) : \n",test_object1.mix.isotopomers_combination)
    test_object2.generate_mixes(mix2)
    print(f"\nCombination generate for mix2 ({test_object2.mix.names}) : \n",test_object2.mix.isotopomers_combination)

    print("\n***************\n")
    test_object1.generate_file("test_mtf")
    print("Folder containing linp files has been generated on your current repertory.")

    print("\n***************\n")
    # test_object1.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\e_coli.mflux")
    # test_object1.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\e_coli.miso")
    # test_object1.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\e_coli.netw")
    # test_object1.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\e_coli.tvar")
    # test_object1.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\e_coli.cnstr")
    test_object1.read_files(r"../test-data/e_coli.mflux")
    test_object1.read_files(r"../test-data/e_coli.miso")
    test_object1.read_files(r"../test-data/e_coli.netw")
    test_object1.read_files(r"../test-data/e_coli.tvar")
    test_object1.read_files(r"../test-data/e_coli.cnstr")
    # test_object1.check_files_matching()
    print("Imported files\n\n", test_object1.data_dict)

    print("\n***************\n")
    test_object1.generate_vmtf_file()
    print(f"Dictionary with all vmtf file element for this mix {test_object1.mix.names} : \n", test_object1.dict_vmtf)
    print("\nVmtf file has been generated on your current repository.")
    # test_object1.influx_simulation()