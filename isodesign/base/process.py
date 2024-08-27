""" Module for calculation """

import logging
import os
import shutil
import tempfile
from collections import namedtuple
from pathlib import Path

import pandas as pd
from influx_si import influx_s, influx_i, C13_ftbl, txt2ftbl

from isodesign.base.isotopomer import Isotopomer
from isodesign.base.label_input import LabelInput
from isodesign.base.score import ScoreHandler

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
        # Elements analyzed (substrates, metabolites, etc.) in the network using the analyse_model method
        self.netan = {}
        # summary dataframe generated after simulation with influx_si
        self.summary_dataframe = None
        # filtered dataframe after filter use
        self.filtered_dataframe = None
        # Dictionary containing isotopomers
        # key : substrate name, value : list of isotopomers
        self.isotopomers = {}
        # Get the tvar.def file generated during the model analysis
        self.tvar_def_file = None
        # Dictionary containing scores
        self.score = None
        # Dictionary to store the number of labeled inputs and the total isotopomer prices of each linp file 
        # Key : linp file name, value : namedtuple containing the number of labeled inputs and the total price
        self.info_linp_files = {}

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


    def analyse_model(self):
        """
        Analyze model network to identify substrates, metabolites, etc by using 
        modules from influx_si.
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

            # # get the tvar.def file
            # for file in os.listdir(tmpdir):
            #     if file.endswith(".tvar.def"):
            #         self.tvar_def_file = pd.read_csv(os.path.join(tmpdir, file), sep="\t", comment="/")

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
        

    def add_isotopomer(self, substrate_name, labelling, nb_intervals, lower_b, upper_b, price=None):	
        """
        Initialize isotopomer object and store it in self.isotopomers dictionary
        with the substrate name as key and a list of isotopomers objects as value.

        :param substrate_name: name of the substrate
        :param labelling: labelling of the isotopomer
        :param nb_intervals: number of intervals to test
        :param lower_b: lower bound
        :param upper_b: upper bound
        :param price: price of the isotopomer. 
        """
        isotopomer = Isotopomer(substrate_name, labelling, nb_intervals, lower_b, upper_b, price)
        
        if f"{substrate_name}" not in self.isotopomers:
            self.isotopomers.update({f"{substrate_name}" : [isotopomer]})
        else:
            self.isotopomers[f"{substrate_name}"].append(isotopomer)

    def remove_isotopomer(self, substrate, labelling):
        """
        Remove isotopomer from the isotopomer dictionary (self.isotopomers) 
        according to the substrate name and labelling.

        :param substrate: substrate name
        :param labelling: labelling for isotopomer to remove

        """
    
        for isotopomer in self.isotopomers[f"{substrate}"]:
            if isotopomer.labelling == labelling and isotopomer.name == substrate:
                self.isotopomers[f"{substrate}"].remove(isotopomer)

    def generate_combinations(self):
        """
        Generate all possible combinations of labelled substrates 
        using the LabelInput class.
        """

        # Initialize the LabelInput object with the isotopomers dictionary
        self.label_input = LabelInput(self.isotopomers)
        logger.info(f"Label Input - {self.label_input}")

        self.label_input.generate_labelling_combinations()
        
        logger.debug(
            f"Isotopomers combinations:"
            f"{self.label_input.isotopomer_combinations}\n"
        )

    def create_results_folder(self, res_folder_path):
        """ 
        Create a folder to store all the files generated by Isodesign.

        :param res_folder_path: path to the folder where the results will be stored
        """
        self.res_folder_path = Path(f"{res_folder_path}/IsoDesign_tmp")
        self.res_folder_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Results folder path '{res_folder_path}'.\n")

    def get_isotopomer_price(self, isotopomer_labelling, isotopomer_name):
        """ 
        Get the price of an isotopomer based on its labelling and name 
        from the isotopomers dictionary.
        
        :param isotopomer_labelling: isotopomer labelling
        :param isotopomer_name: isotopomer name
        """

        for isotopomers_list in self.isotopomers.values():
            for isotopomer in isotopomers_list:
                if isotopomer.labelling == isotopomer_labelling and isotopomer.name == isotopomer_name:
                    return isotopomer.price
    
    def generate_linp_files(self):
        """
        Generates linp files (TSV format) in the results folder (self.res_folder_path). 
        Each file contains a combination of labelled substrates. 
        The files contain the names of the isotopomers, their labelling positions and their values.

        A file is generated containing a mapping that associates each file 
        number with its respective combinations. 

        """

        logger.info("Creation of the linp files...")

        # create mapping to associate file number with its respective combinations
        with open(os.path.join(str(self.res_folder_path), 'files_combinations.txt'), 'w', encoding="utf-8") as f:
            for index, pair in enumerate(self.label_input.isotopomer_combinations["All_combinations"], start=1):
                df = pd.DataFrame({'Id': None,
                                   'Comment': None,
                                   'Specie': self.label_input.names,
                                   'Isotopomer': self.label_input.labelling_patterns,
                                   'Value': pair.astype(float)})

                # remove rows with value = 0
                df = df.loc[df["Value"] != 0]
                # add a column "Price" containing the price of each isotopomer multiplied by its fraction
                # applies the 'get_isotopomer_price' method to each row (axis=1) in the dataframe 'df'
                df["Price"] = df.apply(lambda x: self.get_isotopomer_price(x["Isotopomer"], x["Specie"]), axis=1) * df["Value"]
                logger.debug(f"Folder path : {self.res_folder_path}\n Dataframe {index:02d}:\n {df}")
                
                df.to_csv(os.path.join(str(self.res_folder_path), f"file_{index:02d}.linp"), sep="\t", index=False)
                f.write(
                    f"File_{index:02d} - {df['Specie'].tolist()}\n\
                    {df['Isotopomer'].tolist()}\n\
                    {df['Value'].tolist()} \n \
                    {df['Price'].tolist()} \n")
                
                self.vmtf_element_dict["linp"] = [f"file_{number_file:02d}" for number_file in range(1, index+1)]

                # namedtuple containing the number of labeled inputs and the total price for each linp file
                info_linp_file = namedtuple("linp_info", ["nb_labeled_inputs", "total_price"])
                self.info_linp_files[f"file_{index:02d}_SD"] = info_linp_file(len([isotopomer for isotopomer in df["Isotopomer"] if "1" in isotopomer]), 
                                                                          df["Price"].sum())
        
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

    def influx_simulation(self, param_list, influx_mode):
        """
        Run the  simulations with influx_si as a function of experiment type 
        (influx_i = instationnary or influx_s = stationary) 

        :param param_list: list of command line arguments to pass to influx_si
        :param influx_mode: "influx_i" or "influx_s"
        """ 
        
        command_list = ["--prefix", self.model_name] + param_list
        
        # Change directory to the folder containing all the file to use for influx_si
        os.chdir(self.res_folder_path)

        logger.info(f"{influx_mode} is running...")

        if influx_mode == "influx_i":
            if influx_i.main(command_list):
                raise Exception(f"Error in {influx_mode}. Check '.err' files")
        
        if influx_mode == "influx_s":
            if influx_s.main(command_list):
                raise Exception(f"Error in {influx_mode}. Check '.err' files")
        
        logger.info(f"{influx_mode} has finished running. Results files in '{self.res_folder_path}'\n")


    def generate_summary(self):
        """
        Read the tvar.sim files and generate a summary dataframe containing :
            - flux names, flux types,
            - the flux values in the tvar.sim files, 
            - the difference between the flux values in the input tvar file and the tvar.sim files,
            - flux SDs in each tvar.sim file
        
        The summary dataframe is generated in an excel file in the results folder.
        During the simulation, fluxes are added. These are highlighted in the summary dataframe.
        
        """

        # use os.walk to generate the names of folders, subfolders and files in a given directory
        self.tvar_sim_paths = [Path(f"{root}/{files}") 
                              for (root, _ , files_names) in os.walk(self.res_folder_path) 
                                for files in files_names if files.endswith('.tvar.sim')]
    
        logger.debug(f"List of tvar.sim file paths : \n {self.tvar_sim_paths}")
        # list of dataframes containing the "NAME", "kind" and "sd" columns from tvar.sim files 
        tvar_sim_dataframes = [pd.read_csv(files_path, sep="\t", usecols=["Name", "Kind", "SD"], index_col=["Name","Kind"]) 
                               for files_path in self.tvar_sim_paths]
        # take the flux values from the first tvar.sim file 
        # flux values are the same in all tvar.sim files
        tvar_sim_values = pd.read_csv(self.tvar_sim_paths[0], sep="\t", usecols=["Value", "Name", "Kind"]) 
        
        for idx, df in enumerate(tvar_sim_dataframes):
            df.rename({
                "SD": f"file_{idx+1:02d}_SD"
            }, axis=1, inplace=True)
        logger.debug(f"tvar_sim_dataframes: {tvar_sim_dataframes}")

        # take the "Name", "Kind" and "Value" columns from the input tvar file
        input_tvar_file = self.mtf_files['tvar'].data[["Name", "Kind", "Value"]]
        # merge data from the input tvar file with data from tvar.sim files based on flux names and kind
        merged_tvar = pd.merge(input_tvar_file, tvar_sim_values, on=["Name", "Kind"], how="outer", suffixes=('_tvar_init', None))
        merged_tvar["Value difference"] = merged_tvar["Value_tvar_init"] - merged_tvar["Value"]
        logger.debug(f"Merged_tvar_values : {merged_tvar}")

        # merge the "merged_tvar" dataframe with concatenated dataframes from the "tvar_sim_dataframes" list 
        # delete the "Value_tvar_init" column, which is not required 
        self.summary_dataframe = pd.merge(merged_tvar, pd.concat(tvar_sim_dataframes, axis=1, join="inner"), on=["Name","Kind"]).drop(columns="Value_tvar_init")
        logger.info(f"Summary dataframe present in '{self.res_folder_path}' : {self.summary_dataframe}\n")

        # Creating a Styler object for the summary_dataframe DataFrame
        summary_dataframe_styler=self.summary_dataframe.style.apply(
            # If at least one value is missing in the row, set the style with a pale yellow background color
            # Repeating the style for each cell in the row
            lambda row: ['background-color: #fffbcc' if row.isnull().any() else '' for _ in row],
            # Applying the lambda function along the rows of the DataFrame
            axis=1)
        summary_dataframe_styler.to_excel(f"{self.res_folder_path}/summary.xlsx", index=False)


    def data_filter(self, fluxes_names:list=None, kind:list=None, pathways:list=None):
        """
        Filters summary dataframe by fluxes names, kind and/or metabolic pathway 

        :param fluxes_names: list of fluxes names to be displayed 
        :param kind: "NET", "XCH", "METAB"
        :param pathway: name of metabolic pathways to be displayed  

        :return: filtered dataframe
        """
        
        self.filtered_dataframe = self.summary_dataframe.copy()

        if fluxes_names:
            # keep only rows with fluxes names in the list
            self.filtered_dataframe = self.filtered_dataframe.loc[self.filtered_dataframe["Name"].isin(fluxes_names)]
        if kind:
            # keep only rows with kind in the list
            self.filtered_dataframe = self.filtered_dataframe.loc[self.filtered_dataframe["Kind"].isin(kind)]
        if pathways:
            # list storing all fluxes concerned by the selected metabolic pathway(s) 
            all_fluxes = []
            for pathway_name in pathways:
                # key "pathway" in netan dictionary contains another dictionary as value
                # In netan dictionary, key : pathway names, value : list with fluxes names involved in this pathway as value
                all_fluxes.extend(self.netan["pathway"][pathway_name])
        
            self.filtered_dataframe = self.filtered_dataframe.loc[self.filtered_dataframe["Name"].isin(all_fluxes)]
        logger.info(f"Filtered dataframe :\n{self.filtered_dataframe}")
        return self.filtered_dataframe
        
    def generate_score(self, method :list, operation = None, **kwargs):
        """
        Generate a score for each labelled substrate combination according 
        on the rating method(s) applied.

        :param method: list of rating methods to apply
        :param operation: operation to apply to the scores (Addition, Multiply, Divide)
        :param kwargs: additional arguments for the rating methods
        """
        score_object= ScoreHandler(self.filtered_dataframe.iloc[:, 4:] if self.filtered_dataframe is not None else self.summary_dataframe.iloc[:, 4:])
        score_object.apply_criteria(method, **kwargs)
        if operation:
            score_object.apply_operations(operation)
        # Score dictionary storage (present in ScoreHandler class)      
        self.score = score_object.columns_scores
        logger.debug(f"Scores applied to the dataframe :\n{score_object.columns_scores}")
    
    def display_scores(self, columns_names=None):
        """
        Returns as a dataframe the results of the rating method(s) 
        applied according to the desired columns. 

        :param columns_names: the columns to return the scores for
        """
        if columns_names is None:
            # If no columns are specified, all columns are considered
            columns_names = self.score.keys()
        # Create a dataframe from the dictionary containing the scores
        scores_table = pd.DataFrame.from_dict({col: self.score[col] for col in columns_names}, 
                                     orient='index')
        logger.info(f"Scores table :\n{scores_table}")
        return scores_table
        

if __name__ == "__main__":

    test = Process()
    test.get_path_input_folder(r"C:\Users\kouakou\Documents\test_data")
    test.get_model_names()
    test.load_model("design_test_1")
    test.analyse_model()
    test.create_results_folder(r"C:\Users\kouakou\Documents")
    test.generate_isotopomer("Gluc", "111111", 10, 0, 100)
    test.generate_isotopomer("Gluc", "100000", 10, 0, 100)
    test.generate_isotopomer("FTHF_in", "0", 100, 100, 100)
    test.generate_isotopomer("CO2_in", "0", 100, 100, 100)
    # test.generate_combinations()
    # test.generate_linp_files()
    # test.generate_vmtf_file()
    # test.copy_files()
    
    # test.influx_simulation(["--emu","--noscale","--ln","--noopt"], influx_mode="influx_s")
    
    # test.generate_summary()
    
    # # # test.data_filter(pathways=["GLYCOLYSIS"],kind=["NET"])
    # test.generate_score(["sum_sd", "price"], info_linp_file_dict=test.info_linp_file)
    # test.display_scores()
    
    

    

