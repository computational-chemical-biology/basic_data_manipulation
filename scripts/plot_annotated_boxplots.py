#https://levelup.gitconnected.com/statistics-on-seaborn-plots-with-statannotations-2bfce0394c00
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats
from statannotations.Annotator import Annotator
from matplotlib.backends.backend_pdf import PdfPages

def get_log_ax(orient="v"): 
    if orient == "v": 
        figsize = (12, 6) 
        set_scale = "set_yscale" 
    else: 
        figsize = (10, 8) 
        set_scale = "set_xscale" 
    fig, ax = plt.subplots(1, 1, figsize=figsize) 
    fig.patch.set_alpha(1) 
    getattr(ax, set_scale)("log") 
    return ax 

if __name__=='__main__':
    data = {0: [feat01, meta01],
            1: [feat02, meta02],
            2: [feat03, meta03]}

    for k in range(3):
        feattmp = data[k][0].copy()
        feattmp = feattmp[feattmp.columns[feattmp.columns.str.contains(' Peak area')]].T
        feattmp += 1
        #feattmp = feattmp.apply(lambda a: a/a.sum(), axis=1)
        feattmp.reset_index(inplace=True)
        feattmp['index'] = feattmp['index'].str.replace(' Peak area', '')

        with PdfPages('lote%s.pdf' % k) as pdf:
            for i in present_all.index:
                if pd.isna(present_all.loc[i, f'row ID-{k+1}']):
                    continue
                ind = np.where(data[k][0]['row ID']==present_all.loc[i, f'row ID-{k+1}'])[0][0]
                tmp = pd.merge(data[k][1], feattmp[['index', ind]], left_on='filename', right_on='index')
                #tmp[ind] = np.log(tmp[ind])

                #print(normaltest(tmp.loc[tmp.classe_mortalidade=='C', ind]))
                #print(normaltest(tmp.loc[tmp.classe_mortalidade=='A', ind]))
                #print(normaltest(tmp.loc[tmp.classe_mortalidade=='B', ind]))

                pairs = list(itertools.combinations(['A', 'B', 'C'], 2))

                plotting_parameters = {
                    'data': tmp,
                     'x': 'classe_mortalidade',
                     'y': ind,
                     'order': ['A', 'B', 'C']
                }

                #tmp[['classe_mortalidade', i]].groupby('classe_mortalidade').mean()
                pvalues = []
                for p in pairs:
                    pvalues.append(stats.ttest_ind(tmp.loc[tmp.classe_mortalidade==p[0], ind],
                                                   tmp.loc[tmp.classe_mortalidade==p[1], ind]).pvalue)

                formatted_pvalues = [f"p={p:.2e}" for p in pvalues]
                ax = get_log_ax()
                sns.boxplot(**plotting_parameters).set_title('mz:{:.2f} rt:{:.2f}'.format(*data[k][0].loc[ind, ['row m/z', 'row retention time']].tolist()))
                sns.stripplot(**plotting_parameters)
                annotator = Annotator(ax, pairs, **plotting_parameters)
                annotator.set_pvalues(pvalues)
                #annotator.set_custom_annotations(formatted_pvalues)
                annotator.annotate()
                #plt.savefig("plot1A.png", bbox_inches='tight')
                pdf.savefig()
                plt.close()

