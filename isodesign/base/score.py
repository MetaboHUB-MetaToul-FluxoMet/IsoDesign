import pandas as pd
import os
import logging
import functools 

logger = logging.getLogger(f"IsoDesign.{__name__}")  

class Score:
    """
    A class to compute the score of a series of values
    """
    def __init__(self, series):
        # The different scoring methods that can be applied. Key: method name, value: method to be applied 
        self.SCORING_METHODS = {
        "sum_sd" : self.apply_sum_sd, 
        "number_of_flux" : self.apply_sum_nb_flux_sd,  
        "labeled_input" : self.apply_number_labeled_inputs,
        }

        # Fluxes SDs according to the different label input's proportions ar contained as columns in the summary dataframe
        # The series of values to compute the score
        self.series = series
        # The calculated score of the series
        self.score = None

    def __call__(self):
        return self.score
    
    def compute(self, method, **kwargs):
        """
        Computes the score for a given method
        
        :param method: the method to apply to the series
        :param kwargs: additional arguments to pass to the method
        
        """
        match method:
            case "number_of_flux":
                self.score = self.SCORING_METHODS[method](kwargs["threshold"], kwargs["weight_flux"] if "weight_flux" in kwargs else 1)
            case "labeled_species":
                self.score = self.SCORING_METHODS[method](kwargs["labeled_species_dict"], kwargs["weight_labeled_input"] if "weight_labeled_input" in kwargs else 1)
            case "sum_sd":
                self.score = self.SCORING_METHODS[method](kwargs["weight_sum_sd"] if "weight_sum_sd" in kwargs else 1)
        logger.info(self.score)

    def apply_sum_sd(self, weight_sum_sd=1):
        """
        Returns the sum of standard deviations for a given label input

        :param weight: he weight to apply to the score
        """
        return self.series.sum() * weight_sum_sd
        
    
    def apply_sum_nb_flux_sd(self, threshold, weight_flux=1):
        """
        Returns the total number of fluxes with sds below a given threshold.

        :param threshold: the threshold value used to filter the flux values
        :param weight: he weight to apply to the score
        """

        return (self.series < threshold).sum() * weight_flux
    
    def apply_number_labeled_inputs(self, labeled_species_dict, weight_labeled_input=1):
        """
        Returns the number of labelled substrates for each labelled input.

        :param labeled_species_dict: a dictionary containing the labelled species
        """
        if self.series.name in labeled_species_dict.keys():
            return labeled_species_dict[self.series.name] * weight_labeled_input


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
    This class applies score methods, performs operations between them 
    and displays them on a given dataset. 
    """
    def __init__(self, dataframe):
        # the summary dataframe (filtered or not) of the results of the various label input proportions following the simulation
        self.dataframe = dataframe
        # dictionary containing the results of scoring methods applied to the columns (fluxes SDs based on different proportions of label inputs) of the dataframe
        # Key : column name, value : dictionary containing the score method as key and the score as value
        self.columns_scores = {}
    

    def apply_scores(self, score_method : list, **kwargs):
        """ 
        Apply a score method to the dataframe columns via the Score class
        
        :param score_method: the method to apply to the dataframe columns
        :param kwargs: additional arguments to pass to the score method
        """
        for column in self.dataframe.columns:
            # Each database column is converted into a Score object to offer flexibility in the subsequent manipulation of each score
            score = Score(self.dataframe[column])
            for method in score_method:
                score.compute(method, **kwargs)
                self.columns_scores.update({column: {method: score.score}}) if column not in self.columns_scores.keys() else self.columns_scores[column].update({method: score.score})


    def get_scores(self, columns_names=None, operation=None):
        """
        Returns as a dataframe the results of the scoring method(s) 
        applied according to the desired columns (fluxes SDs based on 
        different proportions of label inputs). 
        Operations can be applied between score results 

        :param columns_names: the columns to return the scores for
        :param operation: the operation to apply to the scores (Addition, Multiply, Divide)

        """
        if columns_names is None:
            # If no columns are specified, all columns are considered
            columns_names = self.columns_scores.keys()
        match operation:
            case "Addition":
                # The scores of the columns are added together
                # functools.reduce() function is used to apply a particular function passed in its argument to all of the list elements mentioned in the sequence passed along.
                return pd.DataFrame.from_dict({col : functools.reduce(lambda x, y: x + y, self.columns_scores[col].values()) for col in columns_names},
                                              orient='index')                            
            case "Multiply":
                # The scores of the columns are multiplied together
                return pd.DataFrame.from_dict({col : functools.reduce(lambda x, y: x * y, self.columns_scores[col].values()) for col in columns_names},
                                              orient='index')
            case "Divide":
                # The scores of the columns are divided together
                return pd.DataFrame.from_dict({col : functools.reduce(lambda x, y: x / y, self.columns_scores[col].values()) for col in columns_names},
                                              orient='index')
        # If no operation is specified, the scores are returned as they are
        return pd.DataFrame.from_dict({col: self.columns_scores[col] for col in columns_names}, 
                                     orient='index')
