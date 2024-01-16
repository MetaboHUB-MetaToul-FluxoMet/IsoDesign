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
        self.num_carbon = None

    def __len__(self):
        """ 
        Count the carbon number by using the labeling.
        """
        self.num_carbon = len(self.labeling)

    def __repr__(self) -> str:
        return f"Molecule name: {self.name}, Number of associated carbon(s) : {self.num_carbon}"


def intra_mol_comb(num_mol, step=10, start=0, end=100):
    """
    Building the intramolecular cominations. Default values :
        * start: 0
        * end: 100

    :param num_mol: number of molecules into the family 
    :param step: 
    
    :return: list of tuple containing all the intramolecular combinations
    """

    all_fracs = [] #list containing list of fractions in function of the number of molecule 
    for _ in range(len(num_mol)):
        fractions=[data for data in range(start,end,step)] #list of fractions 
        all_fracs.append(fractions) #adding list of fraction for a molecule in the fraction list 
    intra_combi = [pair for pair in list(product(*all_fracs)) if sum(pair) == 100] #list containing all the combination inside a molecule family  
    return intra_combi


def inter_mol_comb(fam_mol1,fam_mol2, step=10, start=0, end=100):
    """ 
    Building the intermolecular combinations. Default values :
        * start: 0
        * end: 100 
    
    :param fam_mol1: list of molecule names of the first molecule family   
    :param fam_mol2: list of molecule names of the second molecule family
    :param step: 

    :return: list containing tuple which contain tuple with all the intermolecular combinations

    Using the function intra_mol_comb for each molecule family to have the 
    list of combination inside the molecule family. 
    """
    
    combi_family_1 = intra_mol_comb(fam_mol1) #intramolecular combination for the first family 
    combi_family_2 = intra_mol_comb(fam_mol2) #intramolecular combination for the second family
    intermol_combi = list(product(combi_family_1,combi_family_2)) #list containing all the combination
    return intermol_combi

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

    df = pd.DataFrame({'Id':None,
                            'Comment':None,
                            'Specie': [i for i in fam_mol1+fam_mol2],
                            'Isotopomer' : [j for j in label_fam1+label_fam2],
                            'Value':None}) 
    
    all_combi = inter_mol_comb(fam_mol1, fam_mol2) #list of all the combination
    for pair in all_combi:
        tmp_df = df.copy() #creation of a temporary file
        tmp_df["Value"] = pair[0] + pair[1] #column "Value" take all the combinations values
        tmp_df.to_csv(f"{pair}.linp", sep="\t") #generation the .linp files

if __name__ == "__main__":
    # Get for Glucose
    #mol_1 = intra_mol_comb(["Ace_U", "Ace_1"])
    #print(mol_1)
    #mol = inter_mol_comb(["Gluc_U", "Gluc_1", "Gluc_23"], ["Ace_U", "Ace_1"], 10, 0,100)
    #print(mol)
    gluc_u = Tracer("Gluc_U", 111111)
    gluc_1 = Tracer("Gluc_1", 100000)
    ace_U = Tracer("Ace_U", 11)
    ace_1 = Tracer("Ace_1", 10)
    glu_name = [gluc_u.name, gluc_1.name] #only tracers names
    ace_name = [ace_U.name, ace_1.name]
    glu_labeling = [gluc_u.labeling, gluc_1.labeling] #only tracers labeling
    ace_labeling= [ace_U.labeling, ace_1.labeling]
    generate_file(glu_name, ace_name, glu_labeling, ace_labeling)
    # # print(mol_1)
    # Get for Acetate
    # mol_2 = comb_fraction(2,0,100,10)
    # print(mol_2)
    pass
