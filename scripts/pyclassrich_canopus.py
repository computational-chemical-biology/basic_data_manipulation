from pyclassrich.gnps import Proteosafe
import matplotlib.pyplot as plt

from pyclassrich.models import class_enrichment, impact_plot, ont_graph, get_ont_graph
from pyclassrich.utils import *
import pandas as pd
import json

from pyclassrich.stats import *

params = {
    "mzmine": False,
    "mzmine_batch": False,
    "desc": 'description',
    "gnps_taskid": '',
    "gnps_workflow": '',
    "gnps_nap": False,
    "nap_taskid": '',
    "classify": True,
    "normalization": {
        "perform": True,
        "type": 'TIC'
    },
    "enrich": True,
    "comparison": {
        "classes": '',
        "field": '',
        "test": 'ttest',
        "vthr": 0.5
    },
    "summarize": True,
    "pcoa": True,
    "pcoa_metric": 'canberra',
    "pcoa_norm": True,
    "pcoa_scale": True,
    "email": 'email@gmail.com',
    "chw": '',
    "type": 'canopus',
    "canopus_file": ''
}
gnps = Proteosafe('7679c548a8d94307beec24167ed6b9ea', 'FBMN-gnps2')
gnps.get_gnps()
feat = gnps.feat
meta = gnps.meta
meta.filename = meta.filename.str.replace(' Peak area', '')
tabgnps = pd.merge(gnps.gnps, gnps.dbmatch,  left_on='cluster index', right_on='#Scan#', how='left')
#annotated = classifyChemWalker('ff32d.tsv', 'COCONUT', tabgnps)

annotated = tabgnps[['cluster index', 'SpectrumID', 'Smiles', 'INCHI',  'InChIKey', 'superclass','class', 'subclass']]
annotated = annotated.rename(columns={'cluster index': 'cluster.index',  'superclass':'superclass_name', 'class':'class_name', 'subclass':'subclass_name', 'InChIKey':'InchiKey'})

annotated['Identifier'] = annotated['InChI'] = annotated['superclass_id'] = annotated['class_id'] = annotated['subclass_id'] = annotated['conflict'] = annotated['ginchikey'] = annotated['InChI'] = annotated['kingdom_name'] = ''
annotated['Score'] = 0

 
annotated = annotated[['cluster.index', 'SpectrumID', 'Smiles', 'INCHI', 'Identifier', 'Score',
                      'InChI', 'kingdom_name', 'superclass_name', 'class_name',
                      'subclass_name', 'superclass_id', 'class_id', 'subclass_id', 'conflict',
                      'ginchikey', 'InchiKey']]

tabgnps = tabgnps.rename(columns={'cluster index': 'cluster.index', 'parent mass':'parent.mass', 'SpectrumID':'LibraryID'})

params['comparison']['classes'] = '3,5' 
params['comparison']['field'] = 'ATTRIBUTE_Fragment'
params['comparison']['test'] = 'ttest'

df = univariate(annotated, tabgnps,
                params, feat, meta)

if params['type']=='chemwalker':
    chemrich = df.copy().loc[~df['cluster.index'].isnull(),
                             ['Identifier', 'class_name', 'InChI',
                              'pval', 'fchange']]

    chemrich.columns = ['Compound_Name', 'Class', 'InChI', 'pvalue', 'foldchange']
    clusterdf = class_enrichment(chemrich, cfield='Class', nfield='Compound_Name')
elif params['type']=='canopus':
    #canopus = pd.read_csv(params['canopus_file'], sep='\t')
    #canopus['cluster index'] = canopus['id'].apply(lambda a: a.split('_')[3])
    #canopus['cluster index'] = canopus['cluster index'].astype(int)
    canopus = pd.read_csv('canopus_formula_summary.tsv', sep='\t')
    canopus = canopus.rename(columns={'mappingFeatureId': 'cluster index'})
    uni = pd.merge(df,
                   canopus[['cluster index', 'ClassyFire#most specific class']],
                   left_on='row ID', right_on='cluster index',
                   how='left')

    uni.drop(['class_name'], axis=1, inplace=True)
    uni.rename(columns={'ClassyFire#most specific class': 'class_name'}, inplace=True)
    uni['class_name'] = uni['class_name'].fillna('')

    chemrich = uni.copy().loc[~uni['cluster.index'].isnull(),
                             ['Identifier', 'class_name', 'InChI',
                              'pval', 'fchange']]

    chemrich.columns = ['Compound_Name', 'Class', 'InChI', 'pvalue', 'foldchange']

    clusterdf = class_enrichment(chemrich, cfield='Class', nfield='Compound_Name')
else:
    raise ValueError("Unknown annotation type.")


