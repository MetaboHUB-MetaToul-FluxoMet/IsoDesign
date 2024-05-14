import pandas as pd
import os
import logging 


class Score:
    def __init__(self, data, method, **kwargs):

        self.data = data
        self.logger = logging.getLogger(__name__)


        # Dictionary containing the scoring name as the key and the function to be applied as the value 
        self.SCORING_METHODS = {
            "sum_sd" : self.apply_sum_sd, 
            "flux_sd" : self.apply_sum_nb_flux_sd,
            "number_labeled_species" : self.apply_number_labeled_species,
            "nb_identified_structure" : self.identified_structure
            }
        
        if method in list(self.SCORING_METHODS.keys()):
            self.score =  self.SCORING_METHODS[method](**kwargs) 
            self.logger.info(self.score)


    def apply_sum_sd(self, weight=1):
        """
        Sum of sd 

        :param weight: weight of the score
        """
        
        return pd.DataFrame({"Sum_sd" : (self.data.iloc[:, 4:]).sum() * weight})
    
    def apply_sum_nb_flux_sd(self, threshold, weight=1):
        """
        Sum of number of flux with sd less than a threshold

        :param threshold: the threshold value used to filter the flux values
        :param weight: weight of the score
        """

        
        return pd.DataFrame({"Flux_sd" : (self.data.iloc[:, 4:] < threshold).sum() * weight}) 

    def apply_number_labeled_species(self, labeled_species_dict):
        """ 
        Gives the number of shapes marked in each result file. 

        The number of shapes marked for each file is stored in a dictionary 
        derived from an attribute of a Process class object. 

        :param labeled_species_dict: dictionary containing file names as key and marked shapes 
                                    count as value from the Process object 
        
        """

        return pd.DataFrame({"Labeled species": labeled_species_dict})       
 
                
    # def identified_structure(self, tvar_sim_paths_list):
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

    #     return pd.DataFrame({"Identified structure": struc_identified})

    def __add__(self, other):
        """
        Define the addition operation.

        :param other: The object to add 
        """
        return pd.DataFrame(self.score.values + other.score.values,
                            index = [self.score.index],
                            columns = [f"{list(self.score.columns)}+{list(other.score.columns)}"])
        
    
    def __mul__(self, other):
        """
        Define the mltiplication operation

        :param other: The object to multiply
        """
        return pd.DataFrame(self.score.values * other.score.values,
                            index = [self.score.index],
                            columns = [f"{list(self.score.columns)}*{list(other.score.columns)}"])
    

    def __truediv__(self, other):
        """
        Define the division operation

        :param other: The object to divide
        """
        return pd.DataFrame(self.score.values / other.score.values,
                            index = [self.score.index],
                            columns = [f"{list(self.score.columns)}/{list(other.score.columns)}"])
    

# class ScoreHandler:
#     def __init__(self, score_objects : Score):
        
#         self.score_objects = score_objects
    
#     def __repr__(self) -> str:
#         return f"\n List of files for scoring :\n{self.score_objects}"
         
    