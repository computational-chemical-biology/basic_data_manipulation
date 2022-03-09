import pandas as pd
import sys

def matchFeats(query, ref, ppm=15, rtabs=20):
    mzdiff = ref['row m/z'].apply(lambda a: ((a-query['row m/z'])/query['row m/z'])*10**6).abs() 
    rtdiff = (ref['row retention time']-query['row retention time']).abs()

    diff = (mzdiff < ppm) & (rtdiff < rtabs)

    ans = ref.loc[diff, ['row ID', 'row m/z', 'row retention time']]

    if len(ans):
        ans['q-id'] = query['row ID']
        ans['q-m/z'] = query['row m/z']
        ans['q-rt'] = query['row retention time']
        ans['ppm'] = mzdiff[diff]
        ans['rtabs'] = rtdiff[diff]
        return ans
    else:
        return pd.DataFrame()

if __name__=='__main__':
    uni01 = pd.read_csv('feats_lote01.tsv', sep='\t')
    uni02 = pd.read_csv('feats_lote02.tsv', sep='\t')
    uni03 = pd.read_csv('feats_lote03.tsv', sep='\t')
    uniall = pd.read_csv('feats_loteAll.tsv', sep='\t')

    uni01['row retention time'] = uni01['row retention time']*60
    uni02['row retention time'] = uni02['row retention time']*60
    uni03['row retention time'] = uni03['row retention time']*60
    uniall['row retention time'] = uniall['row retention time']*60

    feat01 = pd.read_csv('GNPS_FBMN_DATA_lote01.csv')
    feat02 = pd.read_csv('GNPS_FBMN_DATA_lote02.csv')
    feat03 = pd.read_csv('GNPS_FBMN_DATA_lote03.csv')
    meta01 = pd.read_csv('metadados_lote01.tsv', sep='\t')
    meta02 = pd.read_csv('metadados_lote02.tsv', sep='\t')
    meta03 = pd.read_csv('metadados_lote03.tsv', sep='\t')

    uni01.loc[uni01.pval_par.sort_values().index].head()

    mlist = []
    for i in uniall.index:
        tmp = []
        tmp.append(matchFeats(uniall.loc[i, ['row ID', 'row m/z', 'row retention time']],
                              uni01, ppm=20, rtabs=20))
        tmp.append(matchFeats(uniall.loc[i, ['row ID', 'row m/z', 'row retention time']],
                              uni02, ppm=20, rtabs=20))
        tmp.append(matchFeats(uniall.loc[i, ['row ID', 'row m/z', 'row retention time']],
                              uni03, ppm=20, rtabs=20))
        mlist.append(tmp)
    ddic = {0: uni01,
            1: uni02,
            2: uni03}

    dflist = []
    cn = ['row ID', 'pval_par',  'pcor_par',  'pval_npar',  'pcor_npar']
    for i in uniall.index:
        tmp = []
        tmp.append(pd.DataFrame([i]))
        for j in range(3):
            if len(mlist[i][j]):
                tdf = mlist[i][j]['row ID']
                tmp.append(pd.DataFrame(ddic[j].loc[ddic[j]['row ID'].isin(tdf), cn].as_matrix()))
            else:
                tdf = pd.DataFrame([np.nan]*5).T
                #tdf.columns = cn
                tmp.append(tdf)

        df = pd.concat(tmp, axis=1)
        df.columns = ['idx all', 'row ID-1', 'pval_par-1',  'pcor_par-1',  'pval_npar-1', 'pcor_npar-1',
                      'row ID-2', 'pval_par-2',  'pcor_par-2',  'pval_npar-2', 'pcor_npar-2',
                      'row ID-3', 'pval_par-3',  'pcor_par-3',  'pval_npar-3',  'pcor_npar-3']
        dflist.append(df)

    dfall = pd.concat(dflist)
    dfall.to_csv('matching_univariate.tsv', sep='\t', index=None)

    for i in dfall.index:
        if pd.isna(dfall.loc[i, 'idx all']):
            dfall.loc[i, 'idx all'] = idx
        else:
            idx = dfall.loc[i, 'idx all']

    g = dfall.groupby('idx all')
    idxs = g['pval_par-1'].apply(lambda x: pd.notna(x) & x<0.05)

    idx01 = []
    for i in dfall.index:
        if pd.isna(dfall.loc[i, 'pval_par-1']):
            continue
        elif dfall.loc[i, 'pval_par-1'] < 0.05:
            idx01.append(dfall.loc[i, 'idx all'])

    idx01 = list(set(idx01))

    present_all = dfall.loc[dfall['idx all'].isin(set(idx01).intersection(set(idx02)).intersection(set(idx03)))]
    present_all.to_csv('matching_sign_univariate.tsv', sep='\t', index=None)


