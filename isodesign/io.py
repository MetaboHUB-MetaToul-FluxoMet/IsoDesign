"""
Module contenant la classe qui va gérer les entrées et sorties du logiciel.
Les différents paramètres de chaque run vont aussi être initialisés et stockées dans cette classe.

Les tâches à effectuer:
    - Création d'une classe pour contenir les méthodes et attributs associés à la gestion de données et de paramètres
    - Création d'une méthode pour importer un fichier .netw et stocker dans un attribut (ignorer les lignes commençant
    par un #)
    - Création d'une méthode pour importer un fichier .tvar et stocker dans un attribut
    - Création d'une méthode pour importer un fichier .mflux et stocker dans un attribut (ignorer les lignes commençant
    par un #)
    - Créer une méthode __repr__ qui montre les différentes données importées (qui ne renvoie pas d'erreur si un des
    trois fichiers n'a pas été importé)
    - Créer une méthode qui permet d'initialiser un objet 'molécule' ou 'traceur' (qui dit objet dit classe... ;) )
    contenant un noms de molécule et un nombre de carbonnes associés à cette molécules. Trouver un moyen de stocker ces
    objets dans notre classe. Cette classe doit aussi avoir une fonction __len__ pour retourner la longueur de la
    chaine de carbonnes et une fonction __repr__ pour montrer joliment le contenu de l'objet initialisé.

N'hésite pas à ecrire un petit test au fur et a mesure que tu codes.

"""

import pandas as pd 
from pathlib import Path

class IoGestion:
    def __init__(self):
        self.netw = None
        self.tvar = None
        self.mflux = None

    def read_file(self, data : str):
        try:
            if isinstance(data, str):
                data_path = Path(data).resolve()
                if data_path.exists(): 
                    if data_path.suffix in [".netw"]:
                        self.netw = pd.read_csv(data, sep='\t', skiprows=[0], header=None)
                    elif data_path.suffix in [".tvar"]:
                        self.tvar = pd.read_csv(data, sep='\t')
                    elif data_path.suffix in [".mflux"]:
                        self.mflux = pd.read_csv(data, sep='\t', skiprows=[0])
                    else:
                        raise TypeError (f"{data_path} is not in the good format\n Only .netw, .tvar, .mflux formats are accepted")
                else:
                    raise ValueError(f"{data_path} doesn't exist.")
            else:
                raise TypeError(f"An input file is not in right type.")
        except (TypeError, ValueError) as e:
            print(f"An error occurred: {e}")    


    def __repr__(self) -> str:
            return f"Imported data\n\n tvar file \n {self.tvar} \n\n mflux file \n {self.mflux} \n\n netw file \n {self.netw}"
    
class InitMol:
    def __init__(self, name_mol, num_carbon):
        self.name_mol = name_mol
        self.num_carbon = num_carbon

    def __len__(self):
        return self.num_carbon
    
    def __repr__(self) -> str:
        return f"Molecule name: {self.name_mol}, Number of associated carbon(s) : {self.num_carbon}"
    
    
if __name__ == "__main__":
    # Mettre ici tes tests
    donnee = IoGestion()
    donnee.read_file("U:/Projet/IsoDesign/isodesign/test-data/design_test.netw")
    donnee.read_file("U:/Projet/IsoDesign/isodesign/test-data/design_test.mflux")
    donnee.read_file("U:/Projet/IsoDesign/isodesign/test-data/design_test.tvar")
    print(repr(donnee))
    pass
