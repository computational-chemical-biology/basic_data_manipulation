from rdkit.Chem import Descriptors

import pandas as pd
from rdkit import Chem

from pyclassrich.utils import get_db
import os
import sqlalchemy

def load_sqlite(db_name):
    table_name = "compound"
    engine = sqlalchemy.create_engine("sqlite:///%s" % db_name, execution_options={"sqlite_raw_colnames": True})
    df = pd.read_sql_table(table_name, engine)
    return df

def save_sqlite(table_name, df):
    engine = sqlalchemy.create_engine('sqlite:///%s.db' % table_name, echo=False)
    df.to_sql(table_name, index=None, con=engine)

lopgfl = open('inchi2logp.txt', 'w')
df = pd.read_csv('COCONUT.psv', sep='|')


for x in df['InChI']:
   try:
        mol = Chem.MolFromInchi(x)
        logp = Descriptors.MolLogP(mol) 
        lopgfl.write(f'{x}\t{logp}\n')
   except:
        lopgfl.write(f'{x}\t{0}\n')

lopgfl.close()
logpdf = pd.read_csv('inchi2logp.txt', sep='\t', header=None)
df = pd.merge(df, logpdf, left_on='InChI', right_on=0, how='left')
df.rename(columns={1: 'logp'}, inplace=True)
df.drop(0, axis=1, inplace=True)

local_path = f'{os.path.expanduser("~")}/.local/pyclassrich/compounds.db'

db = load_sqlite(local_path)
db['logp'] = 0
db[db.ref=='COCONUT'].head()
df['id'] = range(785201,785201+df.shape[0])

df2 = pd.merge(df, db[['InChI', 'kingdom_id', 'superclass_id', 'class_id', 'subclass_id', ]], on='InChI', how='left')
df2 =  df2[~df2.id.duplicated()]
df2['id'] = df2.id+1

pd.concat([db.loc[0:785200], df2]).shape
db2 = pd.concat([db.loc[0:785200], df2])
save_sqlite("compound", db2)
