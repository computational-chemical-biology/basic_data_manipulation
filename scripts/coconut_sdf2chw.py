from rdkit import Chem
from rdkit.Chem import PandasTools
import pandas as pd
import numpy as np
import sys

def coconut2chw(sdf_filename):
    suppl = Chem.SDMolSupplier(sdf_filename)
    coco = []
    for mol in suppl:
        if type(mol) == Chem.rdchem.Mol:
            coco.append(mol.GetPropsAsDict())

    coconut = pd.DataFrame(coco)
    coconut["InChIKey1"] = coconut.standard_inchi_key.apply(lambda a: a.split('-')[0])
    coconut["InChIKey2"] = coconut.standard_inchi_key.apply(lambda a: a.split('-')[1])
    coconut['kingdom_name'] = ''

    coconut = coconut[['exact_molecular_weight', 'standard_inchi', 'canonical_smiles',
                       'identifier', 'InChIKey2', 'InChIKey1', 'molecular_formula',
                       'kingdom_name', 'chemical_super_class','chemical_class', 'chemical_sub_class']]
    cn = ["MonoisotopicMass", "InChI", "SMILES", "Identifier", "InChIKey2", "InChIKey1",
          "MolecularFormula", 'kingdom_name', 'superclass_name', 'class_name', 'subclass_name']
    coconut.columns = cn
    coconut.to_csv(sdf_filename.replace('sdf', 'psv'), sep='|', index=None)

if __name__ == '__main__':
    coconut2chw(sys.argv[1])
