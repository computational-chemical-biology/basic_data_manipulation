from pyteomics import mgf
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors
import sys

# 'NIST_GC_EI_MAX_LIBRARY.mgf'

if __name__=='__main__':
    filename = sys.argv[1]
    spectra = []
    with mgf.MGF(filename) as reader:
        for spectrum in reader:
            temp = {}
            inchi = spectrum['params'].get('inchi')
            if inchi!=None:
                mol = Chem.MolFromInchi(spectrum['params'].get('inchi'))
            else:
                mol = None
            temp['FILENAME'] = filename
            temp['SEQ'] = '*..*'
            temp['COMPOUND_NAME'] = spectrum['params'].get('name')
            try:
                temp['MOLECULEMASS'] = Descriptors.MolWt(mol)
            except:
                temp['MOLECULEMASS'] = 'N/A'
            temp['INSTRUMENT'] = spectrum['params'].get('instrument')
            temp['IONSOURCE'] = spectrum['params'].get('source_instrument')
            temp['EXTRACTSCAN'] = spectrum['params'].get('scans')
            temp['SMILES'] = spectrum['params'].get('smiles')
            temp['INCHI'] = spectrum['params'].get('inchi')
            temp['INCHIAUX'] = spectrum['params'].get('inchiaux')
            temp['CHARGE'] = spectrum['params'].get('charge')
            temp['IONMODE'] = spectrum['params'].get('ionmode')
            temp['PUBMED'] = 'N/A'
            temp['ACQUISITION'] = 'Isolated'
            try:
                temp['EXACTMASS'] = Descriptors.ExactMolWt(mol)
            except:
                temp['EXACTMASS'] = 'N/A'
            temp['DATACOLLECTOR'] = 'N/A'
            temp['ADDUCT'] = 'N/A'
            temp['INTEREST'] = 'N/A'
            temp['LIBQUALITY'] = 'N/A'
            temp['GENUS'] = 'N/A'
            temp['SPECIES'] = 'N/A'
            temp['STRAIN'] = 'N/A'
            temp['CASNUMBER'] = 'N/A'
            temp['PI'] = 'N/A'
            spectra.append(temp)

    df = pd.DataFrame(spectra)
    df.to_csv(filename.replace('mgf', 'tsv'), sep='\t', index=None)
