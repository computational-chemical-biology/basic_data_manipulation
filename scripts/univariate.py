import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
import sys

def multi_class(data, cn, fnames, method):
    if len(data.groupby(cn)) <= 2:
        raise Exception('ANOVA requires a secondary index with three or more values')
    if method=='anova':
        func = stats.f_oneway
    elif method=='kruskal':
        func = stats.kruskal
    vstats = []
    for col in fnames:
        cls = []
        for k, v in data[[cn,col]].groupby(cn):
            cls.append(v[col])
        try:
            s = func(*cls)
        except:
            s = (0,1)
        vstats.append(s)
    return pd.DataFrame(vstats)


def univariate(feat, meta, field, classes, norm=True):
    feat = feat[['row ID', 'row m/z', 'row retention time']+feat.columns[feat.columns.str.contains('Peak area')].tolist()]

    feat.columns = feat.columns.str.replace(' Peak area', '')

    sampleid = pd.DataFrame(feat.columns[3:].tolist(),
                            columns=['sampleid'])

    fnames = feat['row ID'].tolist()
    feat2 = pd.concat([sampleid,
                       feat[feat.columns[3:]].T.reset_index(drop=True)],
                       axis=1)
    feat2.columns = ['sampleid']+fnames
    #feat2 = feat2[feat2['sampleid'].str.contains('Peak area')]
    #feat2['sampleid'] = feat2['sampleid'].str.replace('(.+)\\.mzX?ML .+', '\\1')
    mnfeat = feat2[feat2.columns[1:]][feat2[feat2.columns[1:]]!=0].min().min()
    # Make it optional?
    feat2.replace(0, mnfeat*(2/3), inplace=True)

    if norm:
        feat2[feat2.columns[1:]] = feat2[feat2.columns[1:]].apply(lambda a: a/sum(a), axis=1)

    #meta['filename'] = meta['filename'].str.replace("\\.mzXML|\\.mzML", "")
    feat2 = pd.merge(meta, feat2, left_on='filename',
                     right_on='sampleid')

    #field = 'classe_mortalidade'
    #classes = 'A,B,C'
    cs = classes.split(',')

    if len(cs)<3:
        cn = field
        idx0 = feat2.index[np.where(feat2[cn]==cs[0])]
        idx1 = feat2.index[np.where(feat2[cn]==cs[1])]
        ttest = feat2[fnames].apply(lambda a: list(stats.ttest_ind(a[idx0], a[idx1], equal_var = False))).T
        ttest = pd.DataFrame(ttest.tolist())
        ttest.columns = ['statistic', 'pvalue']
        pvals_par = ttest['pvalue']
        pcor_par = multipletests(pvals_par, method='fdr_bh')[1]
#    elif test=='wilcox':
        tkruskal = feat2[fnames].apply(lambda a: list(stats.kruskal(a[idx0], a[idx1]))).T
        tkruskal = pd.DataFrame(tkruskal.tolist())
        tkruskal.columns = ['statistic', 'pvalue']
        pvals_npar = tkruskal['pvalue']
        pcor_npar = multipletests(pvals_npar, method='fdr_bh')[1]
    elif len(cs)>2:
        cn = field
        feat3 = feat2[feat2[cn].isin(cs)]
        tanova = multi_class(feat3, cn, fnames, 'anova')
        pvals_par = tanova['pvalue']
        pcor_par = multipletests(pvals_par, method='fdr_bh')[1]
    #elif test=='kruskal':
        tkruskal = multi_class(feat3, cn, fnames, 'kruskal')
        pvals_npar = tkruskal['pvalue']
        pcor_npar = multipletests(pvals_npar, method='fdr_bh')[1]

    # Warning merge changes the order of
    # features ids
    ctabsel = feat[['row ID',  'row m/z',
                    'row retention time']].copy()
    ctabsel['pval_par'] = pvals_par
    ctabsel['pcor_par'] = pcor_par
    ctabsel['pval_npar'] = pvals_npar
    ctabsel['pcor_npar'] = pcor_npar
    return ctabsel

if __name__=='__main__':
    feat = pd.read_csv(sys.argv[1])
    meta = pd.read_csv(sys.argv[2], sep='\t')
    field = sys.argv[3]
    print(f'Selected field is {field}')
    classes = sys.argv[4]
    print(f'Selected classes are {classes}')
    ctabsel = univariate(feat, meta, field, classes)
    ctabsel.to_csv(sys.argv[5], index=None, sep='\t')
