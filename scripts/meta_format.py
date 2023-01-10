import os
import pandas as pd
import numpy as np
import qiime2
from qiime2 import Artifact
from qiime2.plugins import metadata, feature_table, diversity, emperor
from q2_emperor import plot, procrustes_plot, biplot, generic_plot
from scipy.spatial.distance import squareform, pdist
import skbio

import sys

def formatMetadata(data_path, meta_path, isInt=True):
    data =  pd.read_csv(data_path)
    meta1 = pd.read_csv(meta_path, sep='\t', decimal=',')

    fls = data.columns[data.columns.str.contains('Peak area')]
    fls = fls.str.replace(' Peak area', '').tolist()
    split_seq='_,-'
    split_seq = split_seq.split(',')
    sid = fls.copy()
    for p in split_seq:
        sid = [x.split(p)[0] for x in sid]

    if isInt:
        for i in range(len(sid)):
            try:
                sid[i] = int(sid[i])
            except:
                sid[i] = 0

    idx = []
    p = len(meta1)
    for x in sid:
        if len(np.where(meta1.BRB==x)[0]):
            idx.append(np.where(meta1.BRB==x)[0][0])
        else:
            idx.append(p)
            meta1.loc[p] = [np.nan]*meta1.shape[1]
            p += 1
    meta1.loc[idx, 'filename'] = fls
    meta1 = meta1[['filename']+meta1.columns.tolist()[:11]]
    meta1 = meta1.rename(columns={'Unnamed: 7':'classe_mortalidade'})
    #meta1.fillna('', inplace=True)
    return meta1


def qiime2PCoA(sample_metadata, df, out_dir, norm=True,
               scale=False, metric='canberra'):
    sample_metadata.rename(index=str, columns={"filename": "#SampleID"}, inplace=True)
    sample_metadata.columns = sample_metadata.columns.str.replace('\s', '_')

    sample_metadata.index = sample_metadata['#SampleID']
    sample_metadata.drop(['#SampleID'], axis=1, inplace=True)
    qsample_metadata = qiime2.metadata.Metadata(sample_metadata)

    df2 = df[df.columns[df.columns.str.contains(' Peak area')]]
    df2.columns = [re.sub('(.+\.mzX?ML) .+', '\\1', a) for a in df2.columns]
    df2.index = df['row ID'].astype(str)
    df2 = df2.T

    if norm:
        df2 = df2.apply(lambda a: a/sum(a), axis=1)

    if scale:
        df2 = (df2-df2.mean())/df2.std()

    dm1 = squareform(pdist(df2, metric=metric))
    dm1 = skbio.DistanceMatrix(dm1, ids=df2.index.tolist())
    dm1 = Artifact.import_data("DistanceMatrix", dm1)
    pcoa = diversity.methods.pcoa(dm1)
    emperor_plot = emperor.visualizers.plot(pcoa.pcoa,
                                            qsample_metadata)

    if '.qzv' in out_dir:
        emperor_plot.visualization.save(out_dir)
    else:
        emperor_plot.visualization.export_data(out_dir)
    return pcoa

if __name__=='__main__':
    data = pd.read_csv(sys.argv[1])
    meta1 = pd.read_csv(sys.argv[2], sep='\t')
    qiime2PCoA(meta1, data, out_dir=sys.argv[3], norm=False, scale=False, metric='canberra')
