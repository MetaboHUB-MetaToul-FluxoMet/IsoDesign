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
        This method permit to count the carbon number by 
        using the labeling.
        """
        self.num_carbon = len(self.labeling)

    def __repr__(self) -> str:
        return f"Molecule name: {self.name}, Number of associated carbon(s) : {self.num_carbon}"


def intra_mol_comb(num_mol, step=10, start=0, end=100):
    """
    Function that output a list of combination for a molecule family.
    Input : number of molecule in the family, step (10 by default), start (0 by default) 
    and (100 by default)
    """
    fractions = [] #list containing list of fractions in function of the number of molecule 
    for _ in range(len(num_mol)):
        fracs=[data for data in range(start,end,step)] #list of fractions 
        fractions.append(fracs) #adding list of fraction for a molecule in the fraction list 
    comb = [i for i in list(product(*fractions)) if sum(i) == 100] #list containing all the combination inside a molecule family  
    return comb


def inter_mol_comb(mol1,mol2, step=10, start=0, end=100):
    """ 
    Function that output a list of combination between 2 or more molecule family.

    Input : mol1 (list of all the molecule for the first family), mol2 (list of all 
    the molecule for the second family), step (10 by default), start (0 by default) 
    and (100 by default).

    Use the function intra_mol_comb for each molecule family to have the list of combination 
    inside the molecule family. 
    """
    mol_1 = intra_mol_comb(mol1, start=0, end=100, step=10) #intramolecular combination for the first family 
    mol_2 = intra_mol_comb(mol2, start=0, end=100, step=10) #intramolecular combination for the second family
    inter_comb = list(product(mol_1,mol_2)) #list containing all the combination
    return inter_comb

def generate_file(mol1, mol2,labeling1, labeling2):
    """ 
    Function generating .linp files in function of all combination between 2 or more molecule family. 

    Input : mol1 (list of all the molecule for the first family), mol2 (list of all the molecule for the 
    second family), labeling1 (list of all labeling for the first molecule family), labeling2 (list of all 
    labeling for the second molecule family)
    """
    df = pd.DataFrame({'Id':None,
                            'Comment':None,
                            'Specie': [i for i in mol1+mol2],
                            'Isotopomer' : [j for j in labeling1+labeling2],
                            'Value':None}) 
    
    combi = inter_mol_comb(mol1, mol2) #list of all the combination
    for i in combi:
        tmp_df = df.copy() #creation of a temporary file
        tmp_df["Value"] = i[0] + i[1] #column "Value" take all the combinations values
        tmp_df.to_csv(f"{i}.csv", sep="\t") #generation the .linp files

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
    print(generate_file(glu_name, ace_name, glu_labeling, ace_labeling))
    # # print(mol_1)
    # Get for Acetate
    # mol_2 = comb_fraction(2,0,100,10)
    # print(mol_2)
    pass
