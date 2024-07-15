import pandas as pd
import os
import logging
import functools 

logger = logging.getLogger(f"IsoDesign.{__name__}")  

class Score:
    """
    Class containing the implementation of the rating criteria 
    """
    def __init__(self, sd_fluxes_columns):
        """
        :param sd_fluxes_columns: the SDs of the fluxes for a given label input are contained as columns in the summary dataframe
        """

        # The different rating methods that can be applied. Key: method name, value: method to be applied 
        self.SCORING_METHODS = {
        "sum_sd" : self.apply_sum_sd, 
        "number_of_flux" : self.apply_sum_nb_flux_sd,  
        "labeled_input" : self.apply_number_labeled_inputs,
        }

        self.sd_fluxes_columns = sd_fluxes_columns 
        self.score = None

    def __call__(self):
        """
        Returns the score obtained after applying the criteria
        """
        return self.score
    
    def compute(self, method, **kwargs):
        """
        Computes the score for a given method
        
        :param method: the method to apply to the sd_fluxes_columns
        :param kwargs: additional arguments to pass to the method
        
        """
        match method:
            case "number_of_flux":
                self.score = self.SCORING_METHODS[method](kwargs["threshold"], kwargs["weight_flux"] if "weight_flux" in kwargs else 1)
            case "labeled_species":
                self.score = self.SCORING_METHODS[method](kwargs["labeled_species_dict"], kwargs["weight_labeled_input"] if "weight_labeled_input" in kwargs else 1)
            case "sum_sd":
                self.score = self.SCORING_METHODS[method](kwargs["weight_sum_sd"] if "weight_sum_sd" in kwargs else 1)
       

    def apply_sum_sd(self, weight_sum_sd=1):
        """
        Returns the sum of standard deviations for a given label input

        :param weight: he weight to apply to the score
        """
        return self.sd_fluxes_columns.sum() * weight_sum_sd
        
    
    def apply_sum_nb_flux_sd(self, threshold, weight_flux=1):
        """
        Returns the total number of fluxes with sds below a given threshold.

        :param threshold: the threshold value used to filter the flux values
        :param weight: he weight to apply to the score
        """

        return (self.sd_fluxes_columns < threshold).sum() * weight_flux
    
    def apply_number_labeled_inputs(self, labeled_species_dict, weight_labeled_input=1):
        """
        Returns the number of labelled substrates for each labelled input.

        :param labeled_species_dict: a dictionary containing the labelled species
        """
        if self.sd_fluxes_columns.name in labeled_species_dict.keys():
            return labeled_species_dict[self.sd_fluxes_columns.name] * weight_labeled_input


    # def identified_structures(self, tvar_sim_paths_list):
    #     """
    #     Gives the number of structures identified in each result file.
        
    #     The method reads each file in the `tvar_sim_paths_list` and counts the number of structures identified
    #     in each file. The result is returned as a pandas DataFrame with the file name and the number of
    #     identified structures.
    #     """
    #     struc_identified = {}
    #     for file in tvar_sim_paths_list:
    #         file_name = file.name.split(os.extsep)[0]
    #         struc_identified.update({f"{file_name}_SD" : sum([len(struct) for struct in pd.read_csv(file, sep="\t", usecols=["Struct_identif"]).values if struct == 'yes'])}) 
    #     return struc_identified
    #     # return pd.DataFrame({"Identified structures": struc_identified})
        

class ScoreHandler:
    """ 
    This class applies rating methods and performs operations between them.
    . 
    """
    def __init__(self, dataframe):
        """
        :param dataframe: the summary dataframe (filtered or not) of the results of the various label input proportions following the simulation
        
        """
        
        self.dataframe = dataframe
        # dictionary containing the results of rating methods applied to the dataframe columns
        # Key : column name, value : dictionary containing the rating method as key and the score as value
        self.columns_scores = {}
    

    def apply_criteria(self, criteria : list, **kwargs):
        """ 
        Apply criteria to the dataframe columns via the score_oject class
        
        :param criteria: method(s) to apply to the columns
        :param kwargs: additional arguments 
        """
        for column in self.dataframe.columns:
            # Each dataframe column is converted into a score_oject object to offer flexibility in the subsequent manipulation of each score
            score_oject = Score(self.dataframe[column])
            for method in criteria:
                score_oject.compute(method, **kwargs)
                self.columns_scores.update({column: {method: score_oject()}}) if column not in self.columns_scores.keys() else self.columns_scores[column].update({method: score_oject()})

    def apply_operations(self, operation):
        """
        Apply an operation to the score_ojects of the columns
        
        :param operation: the operation to apply to the score_ojects (Addition, Multiply, Divide)
        """
        match operation: 
            case "Addition":
                for score_oject in self.columns_scores.values():
                    score_oject.update({"Addition" : functools.reduce(lambda x, y: x + y, score_oject.values())})
                return score_oject
            case "Multiply":
                for score_oject in self.columns_scores.values():
                    score_oject.update({"Multiply" : functools.reduce(lambda x, y: x * y, score_oject.values())})
                return score_oject
            case "Divide":
                for score_oject in self.columns_scores.values():
                    score_oject.update({"Divide" : functools.reduce(lambda x, y: x / y, score_oject.values())})
                return score_oject


