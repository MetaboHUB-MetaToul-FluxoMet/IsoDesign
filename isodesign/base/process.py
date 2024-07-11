""" Module for calculation """

import logging
import os
import shutil
import tempfile
from collections import namedtuple
from pathlib import Path

import numpy as np
import pandas as pd
from influx_si import influx_s, C13_ftbl, txt2ftbl

from isodesign.base.isotopomer import Isotopomer
from isodesign.base.label_input import LabelInput

logger = logging.getLogger(f"IsoDesign.{__name__}")  

class Process:
    """
    The Process class is the main class to organise IsoDesign functionalities.
    Key features:
    - importing and reading data files
    - generating combinations of isotopomers that are stored in influx_si .linp files
    - runs simulations with influx_s to get predicted fluxes and associated SDs
    - generates a summary.

    """
    FILES_EXTENSION = [".netw", ".tvar", ".mflux", ".miso", ".cnstr", ".mmet", ".opt"]

    def __init__(self):

        # Dictionary to store imported file contents. Key : files extension,
        # value : namedtuple with file path and contents
        self.mtf_files = {}
        self.model_names = None
        # LabelInput object
        # To use the generate_labelling_combinations method
        self.label_input = None

        # Dictionary containing element to build the vmtf file
        self.vmtf_element_dict = {"Id": None, "Comment": None}

        # Path to the folder containing all the linp files
        self.input_folder_path = None
        # Path to the folder containing the files created by Isodesign
        self.res_folder_path = None
        # File names without extensions
        # Used for influx_s
        self.model_name = None
        # List of paths to tvar.sim files (after simulation with influx_si)
        self.tvar_sim_paths = []
        # Elements analyzed (substrates, metabolites, etc.) in the network using the model_analysis method
        self.netan = {}
        # key : file name, value : number of marked shapes 
        self.labeled_species = {}
        # summary dataframe generated after simulation with influx_si
        self.summary_dataframe = None
        # filtered dataframe after filter use
        self.filtered_dataframe = None
        # Dictionary containing isotopomers
        # key : substrate name, value : list of isotopomers
        self.isotopomer_dict = {}
        # Get the tvar.def file generated during the model analysis
        self.tvar_def_file = None

    def get_path_input_folder(self, directory_path):
        """
        This function initializes the data import process by setting the input 
        folder path.

        :param directory_path: str containing the path to the input folder 
        """

        if not isinstance(directory_path, str):
            msg = (f"{directory_path} should be of type string and not"
                   f" {type(directory_path)}")
            logger.error(msg)
            raise TypeError(msg)

        self.input_folder_path = Path(directory_path)

        if not self.input_folder_path.exists():
            msg = f"{self.input_folder_path} doesn't exist."
            logger.error(msg)
            raise ValueError(msg)
        
        logger.info(f"Input folder path = {self.input_folder_path}\n")


    def get_model_names(self):
        """
        Retrieves all the model names (via .netw files) present in the input folder. 

        """

        self.model_names = [file.stem for file in self.input_folder_path.iterdir() if file.suffix == '.netw']

        logger.info(f"Model names = {self.model_names}\n")

    def load_model(self, model_name):
        """ 
        Load MTF files depending on the model name chosen.

        :param model_name: model name denoted as prefix of mtf files

        """
        
        self.model_name = model_name

        # Reset the dictionary to store imported files
        self.mtf_files = {}

        if model_name not in self.model_names:
            msg = f"The model '{model_name}' is not found in this folder."
            logger.error(msg)
            raise ValueError(msg)
    
        # namedtuple containing file path and data 
        file_info = namedtuple("file_info", ['path', 'data'])
        for file in self.input_folder_path.iterdir():
            if file.stem == model_name and file.suffix in self.FILES_EXTENSION:
                # Read the file and store its content in a namedtuple
                # TODO: Add checks on file paths
                data = pd.read_csv(str(file), sep="\t", comment="#", header=None if file.suffix == ".netw" else 'infer')
                self.mtf_files.update({file.suffix[1:]: file_info(file, data)})

        logger.info(f"'{self.model_name}' has been imported.\n")
        logger.debug(f"Imported files = {self.mtf_files}\n")


    def model_analysis(self):
        """
        Analyze model network to identify substrates, metabolites, etc.
        """
        
        logger.info("Analyzing model...")

        # Reset self.netan to a new empty dictionary
        # Useful if you want to reuse the function for another prefix
        self.netan = {}
        # temporarily stores files generated by the use of modules
        with tempfile.TemporaryDirectory() as tmpdir:
            for contents in self.input_folder_path.iterdir():
                # copy all files contained in self.res_folder_path (contains input files, linp files and vmtf file) 
                if contents.is_file():
                    shutil.copy(contents, tmpdir)

            # will contain the paths to the ftbl files generated by the txt2ftbl module
            li_ftbl = []  
            # convert mtfs to ftbl
            txt2ftbl.main(["--prefix", os.path.join(str(tmpdir), self.model_name)], li_ftbl)

            # get the tvar.def file
            for file in os.listdir(tmpdir):
                if file.endswith(".tvar.def"):
                    self.tvar_def_file = pd.read_csv(os.path.join(tmpdir, file), sep="\t", comment="/")

            # parse and analyze ftbl stored in li_ftbl
            model: dict = C13_ftbl.ftbl_parse(li_ftbl[0])

            emu = False # can be advantageous to set to "True" when there are
            # only mass measurements
            fullsys = False
            case_i = False # for influx_i, must be "True"
            # analyze the model dictionary to find different network elements
            # such as substrates, metabolites...
            C13_ftbl.ftbl_netan(model, self.netan, emu, fullsys, case_i)
        logger.debug(f"self.netan dictionary keys : {self.netan.keys()}\n")
        logger.info("Network analysis finished successfully.\n")

    
    def copy_files(self):
        """
        Copy the imported files in the linp folder. 
        All the files that will be passed to influx_si have to be in the
        same folder.
        """

        logger.info(f"Copy of the imported files to '{self.res_folder_path}'.\n")

        for file in self.mtf_files.values():
            # File paths are contained as first elements in the namedtuple
            logger.debug(f"File path: {file.path}")
            shutil.copy(file.path, self.res_folder_path)
        

    def generate_isotopomer(self, substrate_name, labelling, nb_intervals, lower_b, upper_b):
        """
        Initialize isotopomer and store in the  dictionary
        self.isotopomer_dict with the substrate name as key and initialized
        isotopomers as values.
        """
        isotopomer = Isotopomer(substrate_name, labelling, nb_intervals, lower_b, upper_b)
        
        if f"{substrate_name}" not in self.isotopomer_dict:
           self.isotopomer_dict.update({f"{substrate_name}" : [isotopomer]})
        else:
            self.isotopomer_dict[f"{substrate_name}"].append(isotopomer)
    
    def generate_combinations(self):
        """
        Generate combinations from stored labeled substrates.
        """

        # Initialize LabelInput from stored substrate isotopomers
        self.label_input = LabelInput(self.isotopomer_dict)
        logger.info(f"Label Input - {self.label_input}")

        self.label_input.generate_labelling_combinations()
        logger.debug(
            f"Isotopomers combinations:"
            f"{self.label_input.isotopomer_combinations}\n"
        )

    def results_folder_creation(self, res_folder_path):
        """ 
        Create a folder to store all the files generated by Isodesign.

        :param res_folder_path: path to the folder where the results will be stored
        """
        self.res_folder_path = Path(f"{res_folder_path}/IsoDesign_tmp")
        self.res_folder_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Results folder path '{res_folder_path}'.\n")

    def generate_linp_files(self):
        """
        Generates linp files (TSV format) in the results folder (self.res_folder_path). 
        Each file contains a combination of labelled substrates. 
        The files contain the names of the isotopomers, their labelling positions and their values.

        A file is generated containing a mapping that associates each file 
        number with its respective combinations. 

        """

        # # Create a folder to store all the linp files
        # self.res_folder_path = Path(f"{self.res_folder_path}/IsoDesign_tmp")
        # self.res_folder_path.mkdir(parents=True, exist_ok=True)

        logger.info("Creation of the linp files...")

        # create mapping to associate file number with its respective combinations
        with open(os.path.join(str(self.res_folder_path), 'files_combinations.txt'), 'w', encoding="utf-8") as f:
            for index, pair in enumerate(self.label_input.isotopomer_combinations["All_combinations"], start=1):
                df = pd.DataFrame({'Id': None,
                                   'Comment': None,
                                   'Specie': self.label_input.names,
                                   'Isotopomer': self.label_input.labelling_patterns,
                                   'Value': pair})

                # remove rows with value = 0
                df = df.loc[df["Value"] != 0]
                logger.debug(f"Folder path : {self.res_folder_path}\n Dataframe {index:02d}:\n {df}")

                df.to_csv(os.path.join(str(self.res_folder_path), f"file_{index:02d}.linp"), sep="\t", index=False)
                f.write(
                    f"File_{index:02d} - {df['Specie'].tolist()}\n \t {df['Isotopomer'].tolist()}\n \t {df['Value'].astype(float).tolist()} \n")
                # Add a new key "linp" with all the combinations as value
                self.vmtf_element_dict.update({"linp": [f"file_{number_file:02d}" for number_file in range(1, index+1)]})

                # Counts the number of labeled species in each generated dataframe 
                count_labeled_species = len([isotopomer for isotopomer in df["Isotopomer"] if "1" in isotopomer])
                self.labeled_species.update({f"file_{index:02d}_SD" : count_labeled_species})

        logger.info(f"{len(self.vmtf_element_dict['linp'])} linp files have been generated.")
        logger.info(f"Folder containing linp files has been generated on this directory : {self.res_folder_path}.\n")
        
    def generate_vmtf_file(self):
        """
        Generate a vmtf file (TSV format) that permit to combine variable
        and constant parts of a network model.
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
        df.to_csv(f"{self.res_folder_path}/{self.model_name}.vmtf", sep="\t", index=False)

        logger.info(f"Vmtf file has been generated in '{self.res_folder_path}.'\n")

    def influx_simulation(self, command_list):
        """
        Run the simulation with influx_si.
        
        :param command_list: list of command line arguments to pass to influx_si
        """ 
       
        logger.info("influx_s is running...")
        # Change directory to the folder containing all the file to use for influx_s
        os.chdir(self.res_folder_path)
        if influx_s.main(command_list):
            raise Exception("Error in influx_si. Check '.err' files")
        logger.info(f"influx_s has finished running. Results files in '{self.res_folder_path}'\n")


    def generate_summary(self):
        """
        Read the tvar.sim files and generate a summary dataframe containing :
            - flux names, flux types,
            - the flux values in the tvar.sim files, 
            - the difference between the flux values in the input tvar file and the tvar.sim files,
            - flux SDs in each tvar.sim file
        """

        # use os.walk to generate the names of folders, subfolders and files in a given directory
        for (root, folders_names, files_names) in os.walk(Path(self.res_folder_path).absolute()):
            if root.endswith("_res"):
                self.tvar_sim_paths += [Path(f"{root}/{files}") for files in files_names if files.endswith('.tvar.sim')]
        logger.debug(f"List of tvar.sim file paths : \n {self.tvar_sim_paths}")

        # list of dataframes containing the "NAME", "kind" and "sd" columns from tvar.sim files 
        tvar_sim_dataframes = [pd.read_csv(files_path, sep="\t", usecols=["Name", "Kind", "SD"], index_col=["Name","Kind"]) for files_path in self.tvar_sim_paths]
        # take the flux values from the first tvar.sim file 
        # flux values are the same in all tvar.sim files
        tvar_sim_value = pd.read_csv(self.tvar_sim_paths[0], sep="\t", usecols=["Value", "Name", "Kind"]) 
        
        for idx, df in enumerate(tvar_sim_dataframes):
            df.rename({
                "SD": f"file_{idx+1:02d}_SD"
            }, axis=1, inplace=True)
        logger.debug(f"tvar_sim_dataframes: {tvar_sim_dataframes}")

        # take the "Name", "Kind" and "Value" columns from the input tvar file
        input_tvar_file=self.mtf_files['tvar'].data[["Name", "Kind", "Value"]]
        # merge data from the input tvar file with data from tvar.sim files based on flux names and kind
        merged_tvar = pd.merge(input_tvar_file, tvar_sim_value, on=["Name", "Kind"], how="outer", suffixes=('_tvar', None))
        merged_tvar["Value difference"] = merged_tvar["Value_tvar"] - merged_tvar["Value"]
        logger.debug(f"Merged_tvar_values : {merged_tvar}")

        # merge the "merged_tvar" dataframe with concatenated dataframes from the "tvar_sim_dataframes" list 
        # delete the "Value_tvar" column, which is not required 
        self.summary_dataframe = pd.merge(merged_tvar, pd.concat(tvar_sim_dataframes, axis=1, join="inner"), on=["Name","Kind"]).drop("Value_tvar", axis=1)
        logger.info(f"Summary dataframe present in '{self.res_folder_path}' : {self.summary_dataframe}\n")

        # Creating a Styler object for the summary_dataframe DataFrame
        summary_dataframe_styler=self.summary_dataframe.style.apply(
            # If at least one value is missing in the row, set the style with a pale yellow background color
            # Repeating the style determined earlier for each cell in the row
            lambda row: np.repeat('background-color: #fffbcc' if row.isnull().any() else '', row.shape[0]),
            # Applying the lambda function along the rows of the DataFrame
            axis=1)
        summary_dataframe_styler.to_excel(f"{self.res_folder_path}/summary.xlsx", index=None)
 
    
    def data_filter(self, fluxes_names:list=None, kind:list=None, pathways:list=None):
        """
        Filters output dataframe by fluxes names, kind and/or metabolic pathway 

        :param fluxes_names: list of fluxes names to be displayed 
        :param kind: "NET", "XCH", "METAB"
        :param pathway: name of metabolic pathways to be displayed  
        """
        
        self.filtered_dataframe = self.summary_dataframe.copy()

        if fluxes_names:
            # keep only rows with fluxes names in the list
            self.filtered_dataframe = self.filtered_dataframe.loc[self.filtered_dataframe["Name"].isin(fluxes_names)]
        if kind:
            # keep only rows with kind in the list
            self.filtered_dataframe = self.filtered_dataframe.loc[self.filtered_dataframe["Kind"].isin(kind)]
        if pathways:
            # list storing all flows concerned by the selected metabolic pathway(s) 
            all_fluxes = []
            for pathway_name in pathways:
                # key "pathway" in netan dictionary contains another dictionary as value
                # In netan dictionary, key : pathway names, value : list with fluxes names involved in this pathway as value
                all_fluxes.extend(self.netan["pathway"][pathway_name])
        
            self.filtered_dataframe = self.filtered_dataframe.loc[self.filtered_dataframe["Name"].isin(all_fluxes)]
        logger.info(f"Filtered dataframe :\n{self.filtered_dataframe}")
        return self.filtered_dataframe
        

if __name__ == "__main__":

    test = Process()
    test.get_path_input_folder(r"C:\Users\kouakou\Documents\test_ecoli2")
    test.get_model_names()
    test.load_model("design_test_1")
    test.model_analysis()
    test.results_folder_creation(r"C:\Users\kouakou\Documents")
    test.generate_isotopomer("Gluc", "111111", 10, 0, 100)
    test.generate_isotopomer("Gluc", "100000", 10, 0, 100)
    test.generate_isotopomer("FTHF_in", "0", 100, 100, 100)
    test.generate_isotopomer("CO2_in", "0", 100, 100, 100)
    test.generate_combinations()
    test.generate_linp_files()
    test.copy_files()
    test.generate_vmtf_file()
   
    # # test.influx_simulation(["--prefix","design_test_1", "--emu","--noscale","--ln","--noopt"])
    
    # test.generate_summary()
    
    # test.data_filter(pathways=["GLYCOLYSIS"],kind=["NET"])

   
    # sd = ScoreHandler(test.summary_dataframe.iloc[:, 4:])
    # sd.apply_scores(["Sum SDs", "nb of labeled input"], weight_sum_sd=1, labeled_species_dict = test.labeled_species)
    # # sd.apply_scores("number_of_flux", threshold = 100)

    # # # labeled = ScoreHandler(test.summary_dataframe.iloc[:, 4:])
    # # # labeled.apply_scores("labeled_species", labeled_species_dict = test.labeled_species)

    # print(sd.get_scores(operation="Addition"))


    # print(labeled.get_scores())
    
    

    

