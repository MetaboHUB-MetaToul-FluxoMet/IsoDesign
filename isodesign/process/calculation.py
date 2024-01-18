""" Module for calculation """

from itertools import product
import pandas as pd


class Tracer:
    """ 
    This class is for the initiation of tracers.
    """

    def __init__(self, name, labeling):
        self.name = name
        self.labeling = labeling
        self.num_carbon = len(self.labeling)

    def __len__(self):
        """ 
        Count the carbon number by using the labeling.
        """
        return self.num_carbon

    def __repr__(self) -> str:
        return f"Molecule name: {self.name}, Number of associated carbon(s) : {self.num_carbon}"


def _generate_frac_comb(molecules, step=10):
    """
    Generate combinations of different molecular tracers proportions

    :param molecules: list of tracer molecules
    :param step: step for proportions to test
    
    :return: list of tuples containing proportions of each tracer in mix (sum must be equant to end param value)
    """

    all_fracs = []
    for _ in range(len(molecules)):
        fractions = [data for data in range(0, 100+step, step)]
        all_fracs.append(fractions)
            
    # list containing all the combination inside a molecule family
    mixes = [frac_list for frac_list in list(product(*all_fracs)) if sum(frac_list) == 100]
    return mixes
    
def generate_mixes_comb(*args):
    """ 
    Generate cominations between two molecular mixes of tracers
    
    :param args:list of mixes to combine together

    :return: list of all combinations of the tracer mixes
    """       
    if len(args) == 1:
        return _generate_frac_comb(args[0])
    return list(product(*[_generate_frac_comb(mix) for mix in args]))


def generate_file(tracer1, tracer2=None):
    """ 
    Generating .linp files in function of all combination for one or two mixe(s)

    :param tracer1: list of tracer molecules
    :param tracer2: list of tracer molecules

    :return: Generate .linp files depending on the number of combination
            Files containing dataframe with tracers features including the combinations
            for all tracer mixes
    """
    df = pd.DataFrame({'Id': None,
                       'Comment': None,
                       'Specie': [],
                       'Isotopomer': [],
                       'Value': []} )
   
    tmp_df = df.copy()

    labels = [] #list containing all the labeling 
    names = [] #list containing all the tracer names

    for trac1 in tracer1:
        labels.append(trac1.labeling)
        names.append(trac1.name)
    
    all_combi = generate_mixes_comb(tracer1) #list of tuple with all combinations for one mix

    if tracer2:
        for trac2 in tracer2:
            labels.append(trac2.labeling)
            names.append(trac2.name)
        all_combi = generate_mixes_comb(tracer1, tracer2) #list of tuple of tuple with all combinations for two mixes
        
    tmp_df["Isotopomer"] = [labeling for labeling in labels]
    tmp_df["Specie"] = [name for name in names] 

    for pair in all_combi:
        if tracer2 :
            tmp_df["Value"] = pair[0]+pair[1]
            tmp_df2=tmp_df.drop(tmp_df[tmp_df.Value == 0].index) #remove all row equals to 0 
            tmp_df2.to_csv(f"{pair}.linp", sep="\t")
        if not tracer2:
            tmp_df["Value"] = pair
            tmp_df2=tmp_df.drop(tmp_df[tmp_df.Value == 0].index)
            tmp_df2.to_csv(f"{pair}.linp", sep="\t")
    
    
if __name__ == "__main__":
    # Get for Glucose
    # final = generate_mixes_comb(["Ace_U", "Ace_1"], ["Gluc_U", "Gluc_1", "Gluc_23"])
    # print(final)
    # print(mol_1)
    # print(mol_2)
    # #print(mol_1)
    # #mol = inter_mol_comb(["Gluc_U", "Gluc_1", "Gluc_23"], ["Ace_U", "Ace_1"], 10, 0,100)
    # #print(mol)
    gluc_u = Tracer("Gluc_U", "111111")
    gluc_1 = Tracer("Gluc_1", "100000")
    gluc_23 = Tracer("Gluc_23", "011000")
    ace_u = Tracer("Ace_U", "11")
    ace_1 = Tracer("Ace_1", "10")
    #print(generate_mixes_comb([gluc_u.name,gluc_1.name, gluc_23.name], [ace_u.name, ace_1.name]))
    #print(generate_mixes_comb([gluc_u.name, gluc_1.name], [ace_u.name, ace_1.name]))
    # ace_U = Tracer("Ace_U", 11)
    # ace_1 = Tracer("Ace_1", 10)
    print(generate_file([gluc_u, gluc_1],[ace_u,ace_1]))
    # Get for Acetate
    # mol_2 = comb_fraction(2,0,100,10)
    # print(mol_2)
    pass
