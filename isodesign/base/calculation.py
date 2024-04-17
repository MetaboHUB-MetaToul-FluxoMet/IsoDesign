""" Module for calculation """
from itertools import product
from pathlib import Path
from collections import namedtuple
import tempfile
import math

import os
import shutil
import logging
from decimal import Decimal
import pandas as pd
import numpy as np
from influx_si import influx_s, C13_ftbl, txt2ftbl

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

        return np.array([Decimal(fraction) / Decimal(100) for fraction in
                         range(self.lower_bound, self.upper_bound + self.step, self.step)])
    

    def __len__(self):
        return self.num_carbon

    def __repr__(self) -> str:
        return f"\nNumber of associated carbon(s) : {self.num_carbon},\
        \nName = {self.name},\
        \nLabelling = {self.labelling},\
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
        for isotopomer_name, isotopomer in self.isotopomer_group.items():
            #logger.debug(f"Running combinatory function on {isotopomer_name} group")
            # For all isotopomers present, all possible fractions are generated except for the first 
            # First isotopomer's fraction will be deduced from the other ones
            if len(isotopomer) > 1:
                fractions = [fracs.generate_fraction() for fracs in isotopomer[1:]]
            else:
                fractions = [fracs.generate_fraction() for fracs in isotopomer]

            # logger.debug(f"Generated fractions:\n {fractions}")
            # fractions : list containing vectors of fractions of each isotopomer 
            # np.meshgrid is used to return matrices corresponding to all possible combinations of vectors present in the list of fractions
            # -1 parameter in reshape permit to adjusts the size of the first dimension (rows) according to the total number of elements in the array
            all_combinations = np.array(np.meshgrid(*fractions)).T.reshape(-1, len(fractions))

            # filter with sum <= 1 as condition 
            filtered_combinations = np.array(
                [combination for combination in all_combinations if np.sum(combination) <= Decimal(1)])
            # logger.debug(f"Combinations with a sum <= 1: \n{filtered_combinations}")

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
    The Process class is the main class that uses the other classes to perform various tasks:
    - importing and reading data files
    - generating combinations of isotopomers that are stored in influx_si .linp files
    - runs simulations with influx_s to get predicted fluxes and associated SD's
    - generates a summary.

    """
    FILES_EXTENSION = [".netw", ".tvar", ".mflux", ".miso", ".cnstr"]

    def __init__(self):
        # Dictionary to store imported file contents. Key : files extension, value : namedtuple with file path and contents 
        self.imported_files_dict = {}
        self.netw_files_prefixes = None
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
        # stores all elements analyzed in the input network 
        self.netan = {}
        # key : file name, value : number of marked shapes 
        self.labeled_species = {}
        self.summary_dataframe = None
        
    
    def initialize_data(self, directory_path):
        """
        This function initializes the data import process by setting the input 
        folder path and identifying all .netw files in the folder and store 
        prefixes found

        :param directory_path: str containing the path to the input folder 
        """

        if not isinstance(directory_path, str):
            msg = f"{directory_path} should be of type string and not {type(directory_path)}"
            logger.error(msg)
            raise TypeError(msg)

        self.path_input_folder = Path(directory_path)

        if not self.path_input_folder.exists():
            msg = f"{self.path_input_folder} doesn't exist."
            logger.error(msg)
            raise ValueError(msg)
        
        logger.debug(f"Input folder directory = {self.path_input_folder}")
        
        # store prefixes found in the folder
        self.netw_files_prefixes = [file.stem for file in self.path_input_folder.iterdir() if file.suffix == '.netw']

        logger.debug(f"Prefixes from netw files in the folder = {self.netw_files_prefixes}")

    def load_file(self, prefix):
        """ 
        Load tvar, mflux, miso, cnstr and netw files (csv or tsv)
        depending on the prefix chosen.

        :param prefix: str containing the prefix of the file to be loaded

        """
        self.prefix = prefix
        logger.info(f"Prefix {self.prefix}")

        if prefix not in self.netw_files_prefixes:
            msg = f"Prefix '{prefix}' is not found in this folder."
            logger.error(msg)
            raise ValueError(msg)
    
        # namedtuple containing file path and data 
        files_infos = namedtuple("file_info", ['path', 'data'])
        for files in self.path_input_folder.iterdir():
            if files.stem == prefix and files.suffix in self.FILES_EXTENSION:
                data = pd.read_csv(str(files), sep="\t", comment="#", header=None if files.suffix == ".netw" else 'infer')
                self.imported_files_dict.update({files.suffix[1:]: files_infos(files, data)})
                
        logger.debug(f"Imported files dictionary = {self.imported_files_dict}")


    def input_network_analysis(self):
        """
        Analyzes the input network using modules from influx_si 
        """

        # temporarily stores files generated by the use of modules
        # with tempfile.TemporaryDirectory() as tmpdir:
        #     for contents in self.path_input_folder.iterdir():
        #         # copy all files contained in self.path_input_folder (contains input files) 
        #         if contents.is_file():
        #             shutil.copy(contents, tmpdir)
            # will contain the paths to the ftbl files generated by the txt2ftbl module
        li_ftbl = []  
            # convert mtf to ftbl
        txt2ftbl.main(["--prefix", os.path.join(str(self.path_input_folder), self.prefix)], li_ftbl) 
            # parse and analyze first ftbl store in li_ftbl
            # returns a dictionary 
        ftbl=C13_ftbl.ftbl_parse(li_ftbl[0]) 

        emu=False # can be advantageous to set to "True" when there are only mass measurements
        fullsys=False
        case_i=False # for influx_i, must be "True"
            # analyze the ftbl dictionary to find different network elements such as substrates, metabolites...  
        C13_ftbl.ftbl_netan(ftbl, self.netan, emu, fullsys, case_i)
        logger.debug(f"self.netan dictionary keys : {self.netan.keys()}")
        
    def files_copy(self):
        """
        Copy the imported files in the linp folder. 
        All the files that will be passed to influx_si 
        have to be in the same folder.
        """
        logger.info("Copy of the imported files to folder containing linp files...")

        for path in self.imported_files_dict.values():
            logger.debug(f"path {path[0]}")
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

        # logger.debug(f"path isodesign folder {self.path_isodesign_folder}")
        logger.info("Creation of the linp files...")

        # create mapping to associate file number with its respective combinations
        with open(os.path.join(str(self.path_isodesign_folder), 'files_combinations.txt'), 'w', encoding="utf-8") as f:
            for index, pair in enumerate(self.labelinput.isotopomer_combination["combinations"], start=1):
                df = pd.DataFrame({'Id': None,
                                   'Comment': None,
                                   'Specie': self.labelinput.names,
                                   'Isotopomer': self.labelinput.labelling_patterns,
                                   'Value': pair})

                # remove rows with value = 0
                df = df.loc[df["Value"] != 0]
                logger.debug(f"Folder path : {self.path_isodesign_folder}\n Dataframe {index:02d}:\n {df}")

                df.to_csv(os.path.join(str(self.path_isodesign_folder), f"file_{index:02d}.linp"), sep="\t", index=False)
                f.write(
                    f"File_{index:02d} - {df['Specie'].tolist()}\n \t {df['Isotopomer'].tolist()}\n \t {df['Value'].astype(float).tolist()} \n")
                # Add a new key "linp" with all the combinations as value
                self.vmtf_element_dict.update({"linp": [f"file_{number_file:02d}" for number_file in range(1, index+1)]})

                # Counts the number of labeled species in each generated dataframe 
                count_labeled_species = len([isotopomer for isotopomer in df["Isotopomer"] if "1" in isotopomer])
                self.labeled_species.update({f"file_{index:02d}" : count_labeled_species})

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
        for (root, folders_names, files_names) in os.walk(self.path_isodesign_folder.absolute()):
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
        merged_tvar = pd.merge(input_tvar_file, tvar_sim_value, on=["Name", "Kind"], how="outer", suffixes=('_tvar', None))
        merged_tvar["Value difference"] = merged_tvar["Value_tvar"] - merged_tvar["Value"]
        logger.debug(f"Merged_tvar : {merged_tvar}")

        # merge the "merged_tvar" dataframe with concatenated dataframes from the "tvar_sim_dataframes" list 
        # delete the "Value_tvar" column, which is not required 
        self.summary_dataframe = pd.merge(merged_tvar, pd.concat(tvar_sim_dataframes, axis=1, join="inner"), on=[ "Name","Kind"]).drop("Value_tvar", axis=1)
        logger.debug(f"{self.summary_dataframe}")

        # Creating a Styler object for the summary_dataframe DataFrame
        summary_dataframe_styler=self.summary_dataframe.style.apply(
            # If at least one value is missing in the row, set the style with a pale yellow background color
            # Repeating the style determined earlier for each cell in the row
            lambda row: np.repeat('background-color: #fffbcc' if row.isnull().any() else '', row.shape[0]),
            # Applying the lambda function along the rows of the DataFrame
            axis=1)
        summary_dataframe_styler.to_excel(f"{self.path_isodesign_folder}/summary.xlsx", index=None)
 

class Score:
    def __init__(self, data):
        # Dictionary containing the scoring name as the key and the function to be applied as the value 
        self.SCORES = {
            "sum_sd" : self.apply_sum_sd, 
            "flux_sd" : self.apply_sum_nb_flux_sd,
            "number_labeled_species" : self.apply_number_labeled_species
            }

        self.data = data

    def __repr__(self) -> str:
        return f"\n{self.data}\n"

    def apply_sum_sd(self, weight=1):
        """
        Sum of sd 

        :param weight: weight of the score
        """
        return self.data.sum() * weight
    
    def apply_sum_nb_flux_sd(self, threshold, weight=1):
        """
        Sum of number of flux with sd less than a threshold

        :param threshold: the threshold value used to filter the flux values
        :param weight: weight of the score
        """
        return (self.data < threshold).sum() * weight

    def apply_number_labeled_species(self, results_files :list, dict_labeled_species):
        """ 
        Returns number of labeled species according to file(s)

        :param results_files: list of result file names on which to apply the function   
        :param dict_labeled_species: dictionary containing file names and numbers of marked shapes 
        """
        for file_name in results_files:
            if file_name in dict_labeled_species.keys():
                print(f"{file_name} {dict_labeled_species[file_name]}")


class ScoreHandler:
    def __init__(self, score_objects :list):
        self.score_objects = score_objects
        

    def __repr__(self) -> str:
        return f"\n List of files for scoring :\n{self.score_objects}"
    
    def data_filter(self, fluxes_names:list=None, kind:str=None, files_res:list=None):
        """
        Filters self.data according to input parameters. 

        :param fluxes_names: list of fluxes names to be displayed 
        :param kind: "NET", "XCH", "METAB"
        :param files_res: name of output files to be displayed 
        """

        if fluxes_names:
            self.data = self.data.loc[self.data["Name"].isin(fluxes_names)]
        if kind:
            self.data = self.data.loc[self.data["Kind"] == kind]
        if files_res:
            # join the first 4 columns (Name, Kind, Value_tvar.sim, Diff_value) with the SD columns of the files to be displayed 
            self.data = pd.concat((self.data.iloc[:,:4], self.data[files_res]), axis=1)
        logger.info(f"Filtered dataframe :\n{self.data}")
        return self.data
        
    
    def multiply_scores(self):
        """
        Multiplies the elements of the `score_objects` attribute together
        """
        logger.info(f"Multiplication result = {math.fsum(self.score_objects)}")
        return math.prod(self.score_objects)
    
    def sum_scores(self):
        """
        Calculates the sum of the elements in the `score_objects` attribute
        """
        logger.info(f"Addition result = {math.fsum(self.score_objects)}")
        return math.fsum(self.score_objects)
        
    def divide_scores(self):
        """
        This function divides the first element of the `score_objects`
        attribute by the second element.
        """
        if len(self.score_objects) < 2:
            msg = "At least two values are required for division."
            logger.error(msg)
            raise ValueError(msg)

        if any(scores == 0 for scores in self.score_objects):
            msg = "All values must be different from 0."
            logger.error(msg)
            raise ValueError(msg)
        
        logger.info(f"Division result = {self.score_objects[0]/self.score_objects[1]}")
        return self.score_objects[0]/self.score_objects[1]
        

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
    test.initialize_data(r"C:\Users\kouakou\Documents\IsoDesign\isodesign\test_data\acetate_LLE")
    test.load_file("design_test_1")
    test.input_network_analysis()
    test.generate_combinations(mix1)
    test.generate_linp_files()
    test.files_copy()
    test.generate_vmtf_file()
    test.influx_simulation()
    test.generate_summary()

    # test for dataframe filtering and number of marked shapes 
    # filtered_dataframe = Score(test.summary_dataframe)
    # print(filtered_dataframe.data_filter(fluxes_names=["BM", "ald", "eno"], kind="NET", files_res=["file_01_SD", "file_06_SD"]))

    sd_sum = Score(test.summary_dataframe["file_07_SD"])

    fluxes_sd = Score(test.summary_dataframe["file_11_SD"])
    # test4 = Score(test.summary_dataframe["file_08_SD"])

    # test for 
    handler = ScoreHandler([sd_sum.apply_sum_sd(), fluxes_sd.apply_sum_nb_flux_sd(100, weight=3)])
    
    handler.multiply_scores()
    handler.sum_scores()
    handler.divide_scores()

    
    

    

