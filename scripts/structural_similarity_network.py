import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs
#from pyteomics import mgf 
import itertools
from multiprocessing import Pool
from functools import partial
import sys

'''usage
   structural_similarity_network.py <tsv smiles file> <smiles_label> <idfield> <agents> <chunksize>
'''

def getTanimoto(idx, spectab):
    smi1 = spectab.loc[idx[0], 'smiles']
    smi2 = spectab.loc[idx[1], 'smiles']
    try:
        m1 = Chem.MolFromSmiles(smi1)
        m2 = Chem.MolFromSmiles(smi2)
        fp1 = AllChem.GetMorganFingerprint(m1,2)
        fp2 = AllChem.GetMorganFingerprint(m2,2)
        return DataStructs.TanimotoSimilarity(fp1, fp2)
    except:
        return 0

def write_edge_list(spectab, smiles_label, idfield, agents=4,
                    chunksize=100, filename='edge_list.txt'):
    f = open(filename, 'a')
    spectab.rename(columns={smiles_label: 'smiles'}, inplace=True)

    allidx = list(range(spectab.shape[0]))
    cidx = allidx

    for i in range(0, spectab.shape[0], chunksize):
        to_query = allidx[i:i+chunksize]
        cidx = list(set(cidx)-set(to_query))
        idx = list(itertools.product(to_query, cidx))
        idx = idx+list(itertools.combinations(to_query,2))
        with Pool(processes=agents) as pool:
           result = pool.map(partial(getTanimoto, spectab=spectab), idx)
        df = pd.DataFrame(idx)
        df[2] = result
        df[0] = spectab.loc[df[0], idfield].tolist()
        df[1] = spectab.loc[df[1], idfield].tolist()
        df.to_csv(f, sep='\t', index=None, header=None)

    f.close()

if __name__ == '__main__':
    spectab = pd.read_csv(sys.argv[1], sep='\t')
    smiles_label = sys.argv[2]
    spectab.fillna('', inplace=True)
    spectab = spectab[spectab[smiles_label]!='']
    spectab.reset_index(drop=True, inplace=True)

    write_edge_list(spectab, smiles_label=smiles_label,
                    idfield=sys.argv[3], agents=int(sys.argv[4]),
                    chunksize=int(sys.argv[5]))
