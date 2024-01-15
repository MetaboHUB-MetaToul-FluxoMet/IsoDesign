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


def comb_fraction(num_mol, start, end, step):
    fractions = []
    for _ in range(num_mol):
        fracs=[data for data in range(start,end,step)]
        fractions.append(fracs)
    comb = [i for i in list(product(*fractions)) if sum(i) == 100]
    return comb

if __name__ == "__main__":
    # Get for Glucose
    mol_1= comb_fraction(3,0,100,10)
    print(mol_1)
    # Get for Acetate
    
    #mol2 = list_mol(["Gluc_U", "Ace_1"])
    pass
