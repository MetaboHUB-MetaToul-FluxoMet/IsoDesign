from itertools import product

class Tracer:
    def __init__(self, name_mol, labeling):
        self.name_mol = name_mol
        self.labeling = labeling
        self.num_carbon = None

    def __len__(self):
        self.num_carbon = len(self.labeling)

    def __repr__(self) -> str:
        return f"Molecule name: {self.name_mol}, Number of associated carbon(s) : {self.num_carbon}"


def intra_mol_comb(num_mol, start, end, step):
    fractions = []
    for _ in range(len(num_mol)):
        fracs=[data for data in range(start,end,step)]
        fractions.append(fracs)
    comb = [i for i in list(product(*fractions)) if sum(i) == 100]
    return comb

# def intra_mol_comb(mol, start, end, step):
#     return comb_fraction(len(mol), start, end, step)

def inter_mol_comb(mol1,mol2, start, end, step):
    mol_1 = intra_mol_comb(mol1, start, end, step)
    mol_2 = intra_mol_comb(mol2, start, end, step) 
    inter_comb = list(product(mol_1,mol_2))
    return inter_comb


if __name__ == "__main__":
    # Get for Glucose
    # mol_1 = intra_mol_comb(["Ace_U", "Ace_1"],0,100,10)
    # print(mol_1)
    mol = inter_mol_comb(["Gluc_U", "Gluc_1", "Gluc_23"], ["Ace_U", "Ace_1"], 0, 100, 10)
    print(mol[:3])
    # print(mol_1)
    # Get for Acetate
    # mol_2 = comb_fraction(2,0,100,10)
    # print(mol_2)
    pass
