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


def generate_frac_comb(molecules, step=10, start=0, end=100):
    """
    Generate combinations of different molecular tracers proportions

    :param molecules: list of tracer molecules
    :param step: step for proportions to test
    :param start: lowest proportion value for tracer molecules in mix
    :param end: highest proportion value for tracer molecules in mix
    
    :return: list of tuples containing proportions of each tracer in mix (sum must be equant to end param value)
    """

    all_fracs = []
    for _ in range(len(molecules)):
        fractions = [data for data in range(start, end, step)]
        all_fracs.append(fractions)

    # list containing all the combination inside a molecule family
    mixes = [frac_list for frac_list in list(product(*all_fracs)) if sum(frac_list) == 100]
    return mixes


def generate_mixes_comb(*args):
    """ 
    Generate cominations between two molecular mixes of tracers
    
    :param args: mixes to combine together

    :return: list of all combinations of the tracer mixes
    """
    return list(product(*[generate_frac_comb(mix) for mix in args]))


def generate_file(fam_mol1, fam_mol2, label_fam1, label_fam2):
    """ 
    Generating .linp files in function of all combination between 2 molecule family. 

    :param fam_mol1: list of molecule names of the 1st molecule family   
    :param fam_mol2: list of molecule names of the 2nd molecule family
    :param label_fam1: list of all labeling for the 1st molecule family
    :param label_fam2: list of all labeling for the 2nd molecule family

    :return: generate .linp files depending on the number of combination 
            between molecules family. Files containing dataframe with tracers
            features including all the combinations on the column "Value"
    """

    df = pd.DataFrame({'Id': None,
                       'Comment': None,
                       'Specie': [i for i in fam_mol1 + fam_mol2],
                       'Isotopomer': [j for j in label_fam1 + label_fam2],
                       'Value': None})

    all_combi = generate_mixes_comb(fam_mol1, fam_mol2)  # list of all the combination
    for pair in all_combi:
        tmp_df = df.copy()  # creation of a temporary file
        tmp_df["Value"] = pair[0] + pair[1]  # column "Value" take all the combinations values
        tmp_df.to_csv(f"{pair}.linp", sep="\t")  # generation the .linp files


if __name__ == "__main__":
    # Get for Glucose
    final = generate_mixes_comb(["Ace_U", "Ace_1"], ["Gluc_U", "Gluc_1", "Gluc_23"])
    print(final)
    # print(mol_1)
    # print(mol_2)
    # #print(mol_1)
    # #mol = inter_mol_comb(["Gluc_U", "Gluc_1", "Gluc_23"], ["Ace_U", "Ace_1"], 10, 0,100)
    # #print(mol)
    # gluc_u = Tracer("Gluc_U", 111111)
    # gluc_1 = Tracer("Gluc_1", 100000)
    # ace_U = Tracer("Ace_U", 11)
    # ace_1 = Tracer("Ace_1", 10)
    # glu_name = [gluc_u.name, gluc_1.name] #only tracers names
    # ace_name = [ace_U.name, ace_1.name]
    # glu_labeling = [gluc_u.labeling, gluc_1.labeling] #only tracers labeling
    # ace_labeling= [ace_U.labeling, ace_1.labeling]
    # generate_file(glu_name, ace_name, glu_labeling, ace_labeling)
    # # # print(mol_1)
    # Get for Acetate
    # mol_2 = comb_fraction(2,0,100,10)
    # print(mol_2)
    pass
