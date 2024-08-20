import logging
import functools 

logger = logging.getLogger(f"IsoDesign.{__name__}")  

class Score:
    """
    Class containing the implementation of the rating criteria 
    """
    def __init__(self, label_input):
        """
        :param label_input: series containing fluxes SDs for a given label inputs
        """

        # The different rating crieria that can be applied. Key: criterion name, value: method to apply  
        self.SCORING_METHODS = {
        "sum_sd" : self.apply_sum_sd, 
        "number_of_flux" : self.apply_sum_nb_flux_sd,  
        "number_of_labeled_inputs" : self.apply_number_labeled_inputs,
        }

        self.label_input = label_input 
        # The score obtained after applying the criteria
        self.score = None

    def __call__(self):
        """
        Returns the score obtained after applying the criteria
        """
        return self.score
    
    def compute(self, criteria, **kwargs):
        """
        Computes the score and stores it in self.score according to the given criteria.  
        
        :param criteria: the criteria to apply 
        :param kwargs: additional arguments to pass to the selected criteria. If the weight is 
        not provided in kwargs for the selected criteria, the default value is 1.
        
        """
        match criteria:
            # Apply the method associated with the criteria and store the result in self.score
            case "number_of_flux":
                self.score = self.SCORING_METHODS[criteria](kwargs["threshold"], kwargs["weight_flux"] if "weight_flux" in kwargs else 1)
            case "labeled_input":
                self.score = self.SCORING_METHODS[criteria](kwargs["labeled_input_dict"], kwargs["weight_labeled_input"] if "weight_labeled_input" in kwargs else 1)
            case "sum_sd":
                self.score = self.SCORING_METHODS[criteria](kwargs["weight_sum_sd"] if "weight_sum_sd" in kwargs else 1)
       

    def apply_sum_sd(self, weight_sum_sd=1):
        """
        Returns the sum of standard deviations for a given label input

        :param weight: he weight to apply to the score
        """
        return self.label_input.sum() * weight_sum_sd
        
    
    def apply_sum_nb_flux_sd(self, threshold, weight_flux=1):
        """
        Returns the total number of fluxes with sds below a given threshold.

        :param threshold: the threshold value used to filter the flux values
        :param weight: he weight to apply to the score
        """

        return (self.label_input < threshold).sum() * weight_flux
    
    def apply_number_labeled_inputs(self, labeled_input_dict, weight_labeled_input=1):
        """
        Returns the number of labelled substrates for each labelled input.

        :param labeled_input_dict: a dictionary containing the labelled species
        """
        if self.label_input.name in labeled_input_dict.keys():
            return labeled_input_dict[self.label_input.name] * weight_labeled_input



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
        Apply criteria to the dataframe columns via the score_object class
        
        :param criteria: method(s) to apply to the columns
        :param kwargs: additional arguments 
        """
        for column in self.dataframe.columns:
            # Each dataframe column is converted into a score_object object to offer flexibility in the subsequent manipulation of each score
            score_object = Score(self.dataframe[column])
            for method in criteria:
                score_object.compute(method, **kwargs)
                self.columns_scores.update({column: {method: score_object()}}) if column not in self.columns_scores.keys() else self.columns_scores[column].update({method: score_object()})

    def apply_operations(self, operation):
        """
        Apply an operation to the score_objects of the columns
        
        :param operation: the operation to apply to the score_objects (Addition, Multiply, Divide)
        """
        operations = {
            "Addition": lambda x, y: x + y,
            "Multiply": lambda x, y: x * y,
            "Divide": lambda x, y: x / y
        }

        for score_object in self.columns_scores.values():
            score_object.update({operation: functools.reduce(operations[operation], score_object.values())})

        return score_object

