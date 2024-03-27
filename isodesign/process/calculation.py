""" Module for calculation """
from itertools import product
from pathlib import Path
from collections import namedtuple


import os
import shutil
import logging
from decimal import Decimal
import pandas as pd
import numpy as np
from influx_si import influx_s

logging.basicConfig(format=" %(levelname)s:%(name)s: Method %(funcName)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# import timeit

class Isotopomer:
    """ 
    Class for the initiation of isotopomer

    """

    def __init__(self, name, labelling, step=100, lower_bound=100, upper_bound=100):
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
        return np.array([Decimal(fraction) / Decimal(100) for fraction in
                         range(self.lower_bound, self.upper_bound + self.step, self.step)])

    def __len__(self):
        return self.num_carbon

    def __repr__(self) -> str:
        return f"\nNumber of associated carbon(s) : {self.num_carbon},\
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
        Generate combinations of labelled substrate proportions within
        a isotopomers group and/or combination between isotopomers group.

        """
        # logger.debug(f"Isotopologue groups:\n{self.isotopomer_group}")
        for isotopomer_name, isotopomer in self.isotopomer_group.items():
            logger.debug(f"Running combinatory function on {isotopomer_name}")
            # For all isotopomers present, all possible fractions are generated except for the first 
            # First isotopomer's fraction will be deduced from the other ones
            if len(isotopomer) > 1:
                fractions = [fracs.generate_fraction() for fracs in isotopomer[1:]]
            else:
                fractions = [fracs.generate_fraction() for fracs in isotopomer]
            logger.debug(f"Generated fractions: \n {fractions}")
            # fractions : list containing vectors of fractions of each isotopomer 
            # np.meshgrid is used to return matrices corresponding to all possible combinations of vectors present in the list of fractions
            # -1 parameter in reshape permit to adjusts the size of the first dimension (rows) according to the total number of elements in the array
            all_combinations = np.array(np.meshgrid(*fractions)).T.reshape(-1, len(fractions))
            logger.debug(f"List of all combinations:\n{all_combinations}")

            logger.debug("filtering combinations...")
            # filter with sum <= 1 as condition 
            filtered_combinations = np.array(
                [combination for combination in all_combinations if np.sum(combination) <= Decimal(1)])
            logger.debug(f"Filtered combinations: \n{filtered_combinations}")

            # Calculate the difference between 1 and the sum of the fractions of the other isotopomers  
            # Total sum of all fractions must equal 1
            # Permit to find the fractions of the last isotopomer
            if len(filtered_combinations) > 1:
                deduced_fraction = np.array([np.subtract(np.ones([len(filtered_combinations)], dtype=Decimal),
                                                         filtered_combinations.sum(axis=1))]).reshape(len(filtered_combinations),1)
                self.isotopomer_combination[isotopomer_name] = np.column_stack((deduced_fraction, filtered_combinations))
            else:
                self.isotopomer_combination[isotopomer_name] = filtered_combinations
            
            self.names += [isotopomers.name for isotopomers in isotopomer]
            self.labelling_patterns += [isotopomers.labelling for isotopomers in isotopomer]

        if len(self.isotopomer_group) > 1:
            # Addition of a key containing all isotopomers group combination if there is multiple isotopomers group 
            self.isotopomer_combination.update({"combinations": [np.concatenate((*pair,)) for pair in
                                                                 list(product(*self.isotopomer_combination.values()))]})
        else:
            self.isotopomer_combination.update(
                {"combinations": np.column_stack((deduced_fraction, filtered_combinations))})


class Process:
    """
    Class responsible of most of the processes... 

    """
    FILES_EXTENSION = [".netw", ".tvar", ".mflux", ".miso", ".cnstr"]

    def __init__(self):
        # Dictionary to store imported file contents. Key : files extension, value : namedtuple with file path and contents 
        self.imported_files_dict = {}
        # LabelInput object
        # To use the generate_labelling_combinations method
        self.labelinput = None

        # Dictionary containing element to build the vmtf file
        self.vmtf_element_dict = {"Id": None, "Comment": None}

        # Path to the folder containing all the linp files
        self.path_input_folder = None
        # Path to the folder containing the files created by Isodesign
        self.path_isodesign_folder = None
        # File names without extensions
        # Used for influx_s
        self.prefix = None
        
        self.summary_dataframe = None

    def read_file(self, data):
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
        # if ext not in self.FILES_EXTENSION:
        #     msg = f"{data_path} is not in the good format\n Only .netw, .tvar, .mflux, .miso, .cnstr formats are accepted"
        #     logger.error(msg)
        #     raise ValueError(msg)

        # namedtuple containing file path and data 
        files_infos = namedtuple("file_info", ['path', 'data'])
        if ext in self.FILES_EXTENSION:
            data = pd.read_csv(str(data_path), sep="\t", comment="#", header=None if ext == ".netw" else 'infer')
            self.imported_files_dict.update({ext[1:]: files_infos(data_path, data)})

            self.prefix = data_path.stem
        

    def initialize_data(self, directory):
        """
        Imports all files in a folder

        :param directory: folder path 
        """
        self.path_input_folder = Path(directory)
        logger.debug(f"Input folder directory = {self.path_input_folder}")

        for file in self.path_input_folder.iterdir():
            self.read_file(str(file))
        logger.debug(f"Prefix {self.prefix}")
        logger.debug(f"Imported files dictionary = {self.imported_files_dict}")

    def files_copy(self):
        """
        Copy the imported files in the linp folder. 
        All the files that will be passed to influx_si 
        have to be in the same folder.
        """
        logger.info("Copy of the imported files to folder containing linp files...")

        for path in self.imported_files_dict.values():
            # logger.debug(f"path {path[0]}")
            shutil.copy(path[0], self.path_isodesign_folder)
        logger.info("Files have been copied \n")

    def generate_combinations(self, isotopomers_group: dict):
        """
        Generate the combinations from isotopomers_group dictionary.

        :param isotopomers_group: dictionary containing as key substrate name of the isotopomer group
                                and as values a list of isotopomer
        """

        # LabelInput class object contained isotopomers group combinations 
        self.labelinput = LabelInput(isotopomers_group)
        self.labelinput.generate_labelling_combinations()
        logger.debug(f"Isotopomers : {self.labelinput.names} {self.labelinput.labelling_patterns}\n")
        logger.debug(f"Isotopomers combinations : {self.labelinput.isotopomer_combination}")

    def generate_linp_files(self):
        """
        Generates linp files in a folder in the current directory based 
        on all combinations for one or more isotopomer groups. These files 
        are used for Influx_si.
        Each file contains isotopomer names, labels and fractions.

        A file is generated containing a mapping that associates each file 
        number with its respective combinations. 
        """

        # Create the folder that stock linp files if is doesn't exist
        self.path_isodesign_folder = Path(self.path_input_folder/"tmp")
        self.path_isodesign_folder.mkdir(parents=True, exist_ok=True)
        
        logger.debug(f"path isodesign folder {self.path_isodesign_folder}")
        logger.info("Creation of the linp files...")

        with open(os.path.join(str(self.path_isodesign_folder), 'files_combinations.txt'), 'w', encoding="utf-8") as f:
            for index, pair in enumerate(self.labelinput.isotopomer_combination["combinations"], start=1):
                df = pd.DataFrame({'Id': None,
                                   'Comment': None,
                                   'Specie': [],
                                   'Isotopomer': [],
                                   'Value': []})

                df["Specie"] = list(self.labelinput.names)
                df["Isotopomer"] = list(self.labelinput.labelling_patterns)
                df["Value"] = list(pair)
                df = df.loc[df["Value"] != 0]
                logger.debug(f"Folder path : {self.path_isodesign_folder}\n Dataframe {index}:\n {df}")

                df.to_csv(os.path.join(str(self.path_isodesign_folder), f"file_{index:02d}.linp"), sep="\t", index=False)
                f.write(
                    f"File {index} - {self.labelinput.names}\n \t {self.labelinput.labelling_patterns}\n \t {[float(decimal_value) for decimal_value in pair]} \n")
                # Add a new key "linp" with all the combinations as value
                self.vmtf_element_dict.update({"linp": [f"file_{number_file:02d}" for number_file in range(1, index+1)]})
        
        logger.debug(f"Elements in the vmtf dictionary {self.vmtf_element_dict}")
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
        df = pd.DataFrame.from_dict(self.vmtf_element_dict)
        # Add a new column "ftbl" containing the values that are in the key "linp" of vmtf_element_dict
        # These values will be the names of the export folders of the results  
        df["ftbl"] = self.vmtf_element_dict["linp"]
        logger.debug(f"Creation of the vmtf file containing these files :\n {df}")
        df.to_csv(f"{self.path_isodesign_folder}/{self.prefix}.vmtf", sep="\t", index=False)

        logger.info("Vmtf file has been generated in the linp folder.")

    def influx_simulation(self):
        """
        Methode using influx_si for the test by using subprocess
        """ 

        logger.info("Influx_s is running...")
        # Change directory to the folder containing all the file to use for influx_s
        os.chdir(self.path_isodesign_folder) 
        if influx_s.main(["--prefix", self.prefix, "--emu", "--noopt", "--noscale", "--ln"]):
            raise Exception("Error in influx_si. Check '.err' files")
        logger.info("You can check your results in the current directory")
        
    def generate_summary(self):
        """
        Read the tvar.sim files and generate a summary dataframe containing :
            - flux names, flux types,
            - the flux values in the tvar.sim files, 
            - the difference between the flux values in the input tvar file and the tvar.sim files,
            - flux SDs in each tvar.sim file
        """

        # list of all tvar.sim file paths 
        tvar_sim_paths = []
       
        # use os.walk to generate the names of folders, subfolders and files in a given directory
        for root, folders_names, files_names in os.walk(self.path_isodesign_folder):
            if root.endswith("_res"):
                tvar_sim_paths += [Path(f"{root}/{files}") for files in files_names if files.endswith('.tvar.sim')]

        logger.debug(f"List of tvar.sim file paths : \n {tvar_sim_paths}")

        # list of dataframes containing the "NAME", "kind" and "sd" columns from tvar.sim files 
        tvar_sim_dataframes = [pd.read_csv(files_path, sep="\t", usecols=["Name", "Kind", "SD"], index_col=["Name","Kind"]) for files_path in tvar_sim_paths]
        # logger.debug(f"tvar sim dataframes {tvar_sim_dataframes}")
        # take the flux values from the first tvar.sim file 
        # flux values are the same in all tvar.sim files
        tvar_sim_value = pd.read_csv(tvar_sim_paths[0], sep="\t", usecols=["Value", "Name", "Kind"]) 
        
        for idx, df in enumerate(tvar_sim_dataframes):
            df.rename({
                "SD": f"file_{idx+1:02d}_SD"
            }, axis=1, inplace=True)
        # logger.debug(f"tvar_sim_dataframes: {tvar_sim_dataframes}")

        # take the "Name", "Kind" and "Value" columns from the input tvar file
        input_tvar_file=self.imported_files_dict['tvar'].data[["Name","Kind","Value"]]
        # merge data from the input tvar file with data from tvar.sim files based on flux names and kind
        merged_tvar = pd.merge(input_tvar_file, tvar_sim_value, on=["Name", "Kind"], how="outer", suffixes=('_tvar', '_tvar.sim'))
        merged_tvar["Diff_value"] = merged_tvar["Value_tvar"] - merged_tvar["Value_tvar.sim"]
        logger.debug(f"Merged_tvar : {merged_tvar}")

        # merge the "merged_tvar" dataframe with concatenated dataframes from the "tvar_sim_dataframes" list 
        self.summary_dataframe = pd.merge(merged_tvar, pd.concat(tvar_sim_dataframes, axis=1, join="inner"), on=[ "Name","Kind"])
        logger.debug(f"Summary dataframe {self.summary_dataframe}")
        self.summary_dataframe.to_csv(f"{self.path_isodesign_folder}/summary.txt", sep="\t", index=None)


    def main(self, isotopomer_dict : dict):
        self.generate_combinations(isotopomer_dict)
        self.generate_linp_files()
        # self.files_copy()
        # self.generate_vmtf_file()
        # self.influx_simulation()
        self.generate_summary()
        test1 = Score(self.summary_dataframe)
        test2 = Score(self.summary_dataframe["file_07_SD"])
        test3 = Score(self.summary_dataframe["file_11_SD"])
        handler = ScoreHandler([test2, test3])
        # handler.apply_scores(["flux_sd","sum_sd"], threshold=10)
        test1.data_filter(fluxes_names=["BM", "ald", "eno"], files_res=["file_02_SD","file_06_SD"])

class Score:
    def __init__(self, data):
        # Dictionary containing the scoring name as the key and the function to be applied as the value 
        self.SCORES = {
            "sum_sd" : self.apply_sum_sd, 
            "flux_sd" : self.apply_flux_number,
            }

        self.data = data
        # self.name = data.name  

    def __repr__(self) -> str:
        return f"\n{self.data}\n"

    def data_filter(self, fluxes_names:list=None, kind:str=None, files_res:list=None):
        """
        Filters self.data according to input parameters. 

        :param fluxes_names: list of fluxes names to be displayed in self.data
        :param kind: "NET", "XCH", "METAB"
        :param files_res: name of output files to be displayed 
        """
        if fluxes_names:
            self.data = self.data.loc[self.data["Name"].isin(fluxes_names)]
        if kind:
            self.data = self.data.loc[self.data["Kind"] == kind]
        if files_res:
            self.data = self.data.loc[:,["Name", "Kind", "Diff_value"] + files_res]
        logger.info(f"Filtered dataframe :\n{self.data}")

    def apply_sum_sd(self):
        """
        Sum of sd 
        """
        return self.data.sum()
    
    def apply_flux_number(self, threshold):
        """
        Sum of number of flux with sd less than a threshold
        """
        return (self.data < threshold).sum()
class ScoreHandler:
    def __init__(self, score_objects :list):
        self.score_objects = score_objects

    def __repr__(self) -> str:
        return f"\n List of files for scoring :\n{self.score_objects}"

    def apply_scores(self, score_names : list, **kwargs):
        df_scoring = pd.DataFrame(
                {score_name : [obj.SCORES.get(score_name)(**kwargs) if score_name == "flux_sd" else obj.SCORES.get(score_name)()
                                for obj in self.score_objects] for score_name in score_names},
                index=[obj.name for obj in self.score_objects]
                )
        logger.info(f"{score_names} :\n{df_scoring}")
        
    

if __name__ == "__main__":
    gluc_u = Isotopomer("Gluc", "111111", 10, 0, 100)
    gluc_1 = Isotopomer("Gluc", "100000", 10, 0, 100)
    fthf = Isotopomer("FTHF_in", "0")
    co2 = Isotopomer("CO2_in", "0")
    mix1 = {
        "gluc": [gluc_1, gluc_u],
        "fthf": [fthf],
        "co2": [co2]
    }
    test = Process()
    test.initialize_data(r"U:\Projet\IsoDesign\isodesign\test_data\acetate_LLE")
    test.main(mix1)
   

