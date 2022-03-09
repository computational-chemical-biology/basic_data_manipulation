from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import pandas as pd
from raw_data_access import *

if __name__=='__main__':
    conv = 'docker run -it --rm -e WINEDEBUG=-all -v $PWD:/data chambm/pwiz-skyline-i-agree-to-the-vendor-licenses wine msconvert /data/{0} --mzML'
    [os.system(conv.format(x)) for x in meta03.filename[1:]]

    chunks = list(range(0, uni03.shape[0], 16))
    with PdfPages('lote03_sig_panel.pdf') as pdf:
        for c in range(len(chunks)-1):
            ind = uni03.index[chunks[c]:chunks[c+1]]
            fig = plt.figure(figsize = (5,5))
            for i in range(len(ind)):
                j = ind[i]
                plt.subplot(4, 4, i+1)
                plt.tight_layout()
                plt.rcParams.update({'font.size': 4})
                #plt.plot([1, 2, 3], [1, 2, 3])
                overlayXIC(fnames, meta03, 'classe_mortalidade', edict,  mz=uni03.loc[j,'row m/z'],
                           rt=uni03.loc[j, 'row retention time'], fsz=1,
                           title=uni03.loc[j, 'row ID'], type='TI',
                           ppm=100, rtabs=40)

            pdf.savefig(fig)
            fig.clear()
            plt.close()

