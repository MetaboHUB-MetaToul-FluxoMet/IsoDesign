""" Module for calculation """
from itertools import product
from pathlib import Path

import subprocess
import os
import shutil 
import logging
from decimal import Decimal
import pandas as pd
import numpy as np


logging.basicConfig(format= " %(levelname)s:%(name)s: Method %(funcName)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# import timeit

class Isotopomer:
    """ 
    Class for the initiation of isotopomer

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
        return "\nNumber of associated carbon(s) : {self.num_carbon},\
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
    def __init__(self, isotopomer_group: dict):
        """
        Class containing the logic for handling labelling input generation.

        :param isotopomers_group: dictionary containing as key substrate name of the isotopomer group
                                and as values a list of isotopomer 
        """
        
        self.isotopomer_group = isotopomer_group

        # Container for all label input combinations
        # keys : substrate name of the isotopomers group, Values : label input combinations
        self.isotopomer_combination = {}
        # Isotopomer names and labelling patterns.
        self.names = []
        self.labelling_patterns = []

    def generate_labelling_combinations(self):
        """
        Generate combination inside a isotopomers group and/or 
        combination between isotopomers group.

        """
        for isotopomer_name, isotopomer in self.isotopomer_group.items():
            # For all isotopomers present, all possible fractions are generated except for the first 
            # First isotopomer's fraction will be deduced from the other ones
            fractions = [fracs.generate_fraction() for fracs in isotopomer[1:]]
            # fractions : list containing vectors of fractions each isotopomer 
            # np.meshgrid is used to return matrices corresponding to all possible combinations of the various vectors present in fractions list
            # 
            # -1 parameter in reshape permit to adjusts the size of the first dimension (rows) according to the total number of elements in the array
            all_combinations = np.array(np.meshgrid(*fractions)).T.reshape(-1, len(fractions))
            filtered_combinations = np.array([combination for combination in all_combinations if np.sum(combination) <= Decimal(1)])
 
            # Calculate the difference between 1 and the sum of the fractions of the other isotopomers  
            # Total sum of all fractions must equal 1
            # Permit to find the fractions of the last isotopomer
            deduced_fraction = np.subtract(np.ones([len(filtered_combinations)], dtype=Decimal), filtered_combinations.sum(axis=1))
            self.isotopomer_combination[isotopomer_name] = np.column_stack((deduced_fraction, filtered_combinations))
            
            self.names += [isotopomers.name for isotopomers in isotopomer]
            self.labelling_patterns += [isotopomers.labelling for isotopomers in isotopomer]
            
        if len(self.isotopomer_group) > 1 :
            # Addition of a key containing all isotopomers group combination if there is multiple isotopomers group 
            self.isotopomer_combination.update({"combinations" : [np.concatenate((*pair,)) for pair in list(product(*self.isotopomer_combination.values()))]})
        else:
            self.isotopomer_combination.update({"combinations" : np.column_stack((deduced_fraction, filtered_combinations))})   
        
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
        # Dictionary to store imported file contents. Keys are files path, contents are stored as values
        self.data_dict = {}
        # LabelInput object
        # To use the generate_labelling_combinations method
        self.labelinput = None

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
            msg = f"{data} should be of type string and not {type(data)}"
            logger.error(msg)
            raise TypeError(msg)
            
        data_path = Path(data).resolve()

        if not data_path.exists():
            msg = f"{data_path} doesn't exist."
            logger.error(msg)
            raise ValueError(msg)
            
        ext = data_path.suffix
        if ext not in self.FILES_EXTENSION:
            msg = f"{data_path} is not in the good format\n Only .netw, .tvar, .mflux, .miso, .cnstr formats are accepted"
            logger.error(msg)
            raise ValueError(msg)

        data = pd.read_csv(str(data_path), sep="\t", comment="#", header=None if ext == ".netw" else 'infer')
        logger.info("Data importation...")
        logger.info(f"\nImported file : {data_path.name}\n Data :\n {data}\n")

        match ext:
            case ".tvar":
                self._check_tvar(data, data_path.name)
            case ".netw":
                self._check_netw(data, data_path.name)
            case ".miso":
                self._check_miso(data, data_path.name)
            case ".mflux":
                self._check_mflux(data, data_path.name)

        self.data_dict.update({str(data_path): data})
        
        # Add in dict_vmtf the files extensions without the dot as key and files names as value 
        self.dict_vmtf.update({ext[1:]: data_path.stem})

    def files_copy(self):
        """
        Copy the imported files in the linp folder. 
        All the files that will be passed to influx_si 
        have to be in the same folder.
        """
        logger.info("Copy of the imported files to folder containing linp files...")
        
        for path in self.data_dict:
            shutil.copy(path, self.path_linp_folder)
        logger.info("Files have been copied \n")
    
    # def check_files_matching(self):
    #     """ 
    #     Check if metabolites and reactions present in 
    #     the files are actually present in the network file. 

    #     """

    #     # Use of the files_matching_dict dictionary, which contains all the columns of the various files to be compared     
    #     for reaction_name in self.files_matching_dict["tvar_reactions_name"]:
    #         if reaction_name not in self.files_matching_dict["netw_reactions_name"]:
    #             raise ValueError(f"'{reaction_name}' from a tvar file is not in the network file")

    #     for flux in self.files_matching_dict["mflux_flux"]:
    #         if flux not in self.files_matching_dict["netw_reactions_name"]:
    #             raise ValueError(f"'{flux}' from a mflux file is not in the network file")

    #     for specie in self.files_matching_dict["miso_species"]:
    #         if specie not in self.files_matching_dict["netw_metabolite"]:
    #             raise ValueError(f"'{specie}' from a miso file is not in the network file")


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
            msg= f"Number of columns isn't correct for {filename} file"
            logger.error(msg)
            raise ValueError(msg)

        # Add reaction names without the ":" separator as sets  
        # self.files_matching_dict.update({"netw_reactions_name": set(reaction[:-1] for reaction in data.iloc[:, 0])})
        # # Add only metabolites and atom mapping to the dictionary 
        # netw_metabolite = set()
        # for reactions in data.iloc[:, 1]:
        #     for element in reactions.split():
        #         if element not in ["<->", "->", "+"]:
        #             netw_metabolite.add(element)
        # # self.files_matching_dict.update({"netw_metabolite": netw_metabolite})

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
                msg=f"Columns {x} is missing from {filename}"
                logger.error(msg)
                raise ValueError(msg)
            if x == "Value":
                self._check_numerical_columns(data[x], filename)

        for x in data["Type"]:
            if x not in ["F", "C", "D"]:
                msg = f"'{x}' type from {filename} is not accepted in 'Type' column. Only F, D or C type are accepted."
                logger.error(msg)
                raise ValueError(msg)

        for x in data["Kind"]:
            if x not in ["NET", "XCH", "METAB"]:
                msg =  f"'{x} type from {filename} is not accepted in 'Kind' column. Only NET, XCH or METAB type are accepted."
                logger.error(msg)
                raise ValueError(msg)
            
        # Add reactions in the "Name" column with NET fluxes only
        # self.files_matching_dict.update({"tvar_reactions_name": set(data.loc[data["Kind"] == "NET", "Name"])})

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
                msg = f"Columns {x} is missing from {filename}"
                logger.error(msg)
                raise ValueError(msg)

        for x in self.NUMERICAL_COLUMNS:
            self._check_numerical_columns(data[x], filename)

        # # Add species
        # self.files_matching_dict.update({"miso_species": set(data["Specie"])})

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
                msg = f"Columns {x} is missing from {filename}"
                logger.error(msg)
                raise ValueError(msg)

        for x in self.NUMERICAL_COLUMNS:
            self._check_numerical_columns(data[x], filename)

        # # Add fluxes 
        # self.files_matching_dict.update({"mflux_flux": set(data["Flux"])})

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
                msg = f"'{x}' from {file_name} is incorrect. Only numerical values are accepted in {column.name} column."
                logger.error(msg)
                raise ValueError(msg)

    def generate_mixes(self, isotopomers_group: dict):
        """
        Generate the combinations from tracer dictionary.

         :param isotopomers_group: dictionary containing as key substrate name of the isotopomer group
                                and as values a list of isotopomer
        """

        # LabelInput class object contained isotopomers group combinations 
        self.labelinput = LabelInput(isotopomers_group)
        self.labelinput.generate_labelling_combinations()
        logger.info(f"Isotopomers : {self.labelinput.names} {self.labelinput.labelling_patterns}\n")
        logger.debug(f"Isotopomers combinations : {self.labelinput.isotopomer_combination}")

    def generate_linp_files(self, output_path: str):
        """
        Generates linp files in a folder in the current directory based 
        on all combinations for one or more isotopomer groups. These files 
        are used for Influx_si.
        Each file contains isotopomer names, labels and fractions.

        A file is generated containing a mapping that associates each file 
        number with its respective combinations. 
        """

        # Create the folder that stock linp files if is doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self.path_linp_folder = os.path.abspath(output_path)

        logger.info("Creation of the linp files...")

        with open(os.path.join(str(output_path), 'files_combinations.txt'), 'w', encoding="utf-8") as f:
            for index, pair in enumerate(self.labelinput.isotopomer_combination["combinations"], start=1):
                df = pd.DataFrame({'Id': None,
                                    'Comment': None,
                                    'Specie': [],
                                    'Isotopomer': [],
                                    'Value': []})

                df["Specie"] = list(self.labelinput.names)
                df["Isotopomer"] = list(self.labelinput.labelling_patterns) 
                df["Value"] = pair
                df = df.loc[df["Value"] != 0]
                logger.debug(f"Folder path : {self.path_linp_folder}\n Dataframe {index}:\n {df}")

                df.to_csv(os.path.join(str(output_path), f"file_{index}.linp"), sep="\t", index=False)   
                f.write(f"File {index} - {self.labelinput.names}\n {[float(decimal_value) for decimal_value in pair]} \n") 
                # Add a new key "linp" with all the combinations as value
                self.dict_vmtf.update({"linp":  [f"file_{number_file}" for number_file in range(1, index)]})
        logger.debug(f"Elements in the vmtf dictionary {self.dict_vmtf}")
        logger.info("Folder containing linp files has been generated on your current directory.\n")

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
        df = pd.DataFrame.from_dict({key: pd.Series(value) for key, value in self.dict_vmtf.items()})
        # Add a new column "ftbl" containing the values that are in the key "linp" of dict_vmtf
        # These values will be the names of the export folders of the results  
        df["ftbl"] = self.dict_vmtf["linp"]

        logger.debug(f"Creation of the vmtf file containing these files :\n {df}")
        vmtf_file_name = self.dict_vmtf["netw"]
        df.to_csv(f"{self.path_linp_folder}/{vmtf_file_name}.vmtf", sep="\t", index=False)
        
        logger.info("Vmtf file has been generated in the linp folder.")


    def influx_simulation(self):
        """
        Methode using influx_si for the test by using subprocess
        """
        logger.info("Influx_s is running...")
        # Going to the folder containing all the file to use for influx_si
        os.chdir(self.path_linp_folder)
        prefix = self.dict_vmtf["netw"]
        # check parameter tells subprocess.run to throw an exception if the command fails
        # If the command returns a non-zero return value, this usually indicates an error 
        subprocess.run(["influx_s", "--prefix", prefix, "--mtf", f"{prefix}.vmtf", "--noopt"], check=True)
        logger.info("You can check your results in the current directory")
    

if __name__ == "__main__":
    gluc_u = Isotopomer("Gluc", "111111", 10, 0, 100)
    gluc_1 = Isotopomer("Gluc", "100000", 10, 0, 100)
    gluc = Isotopomer("Gluc", "000000", 10, 0, 100)
    ace_u = Isotopomer("Ace_U", "11", 20, 0, 100)
    ace_1 = Isotopomer("Ace_1", "10", 20, 0, 100)
    mix1 = {
        "gluc": [gluc_1, gluc_u]
    }
    mix2 = {
        "gluc": [gluc, gluc_u],
        "ace": [ace_u, ace_1]
    }
    # # Create Process class objects
    test_object1 = Process()
    test_object2 = Process()
   
    test_object2.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\design_test_1.mflux")
    test_object2.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\design_test_1.miso")
    test_object2.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\design_test_1.netw")
    test_object2.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\design_test_1.tvar")
    test_object2.read_files(r"U:\Projet\IsoDesign\isodesign\test-data\design_test_1.cnstr")
    
    # test_object2.read_files(r"../test-data/design_test_1.mflux")
    # test_object2.read_files(r"../test-data/design_test_1.miso")
    # test_object2.read_files(r"../test-data/design_test_1.netw")
    # test_object2.read_files(r"../test-data/design_test_1.tvar")
    # test_object2.read_files(r"../test-data/design_test_1.cnstr")

    test_object2.generate_mixes(mix1)

    test_object2.generate_linp_files("test_mtf")

    test_object2.files_copy()
    # # test_object2.check_files_matching()
    test_object2.generate_vmtf_file()
    test_object2.influx_simulation()
    