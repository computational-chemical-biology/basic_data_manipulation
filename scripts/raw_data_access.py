from pyopenms import *
import numpy as np
import matplotlib.pyplot as plt

def mzXML2mzML(filepath):
    subprocess.run(['FileConverter', '-in', filepath, '-out', filepath.replace('mzXML', 'mzML')])

def loadExp(fname):
    exp_in = MSExperiment()
    MzMLFile().load(fname, exp_in)
    return(exp_in)

def calcTIC(exp):
     tic = 0
     for spec in exp:
         if spec.getMSLevel() == 1:
             mz, i = spec.get_peaks()
             tic += sum(i)
     return tic

def getTIC(exp):
     tic = {} 
     lmz = []
     li = []
     rt = []
     for spec in exp:
         if spec.getMSLevel() == 1:
             mz, i = spec.get_peaks()
             lmz.append(mz)
             li.append(i)
             rt.append(spec.getRT())
     tic['mz'] = lmz
     tic['i'] = li
     tic['rt'] = rt 
     return tic

def getXIC(mass, retention, tic, type='BP', rttol=20, ppm=20, **kwargs):
    xic = {} 
    mztol = mass/((ppm/(10**6))+1.0)
    mzdiff = abs(mztol - mass) 
    rt = np.array(tic['rt']) 
    rtidx = np.where((rt>retention-rttol) & (rt<retention+rttol)) 
    lmz = []
    lrt = []
    li = []
    lxic = []
    for idx in rtidx[0]:
        mztemp = np.array(tic['mz'][idx]) 
        itemp = np.array(tic['i'][idx]) 
        mzidx = np.where((mztemp>mass-mzdiff) & (mztemp<mass+mzdiff)) 
        if len(mzidx[0]):
            lmz += list(mztemp[mzidx])
            li += list(itemp[mzidx])
            lrt.append(rt[idx])
            if type=='TI':
                lxic.append(sum(itemp[mzidx]))
            elif type=='BP':
                if len(itemp[mzidx]):
                    lxic.append(max(itemp[mzidx]))
                else:
                    lxic.append(0)
    xic['mz'] = lmz
    xic['rt'] = lrt
    xic['i'] = li
    xic['xic'] = lxic
    return xic

def getSingleSpectrum(mgffile, scanindex):
    spectrum = {}
    f = open(mgffile)
    lines = np.array(f.readlines())
    f.close()
    bg = np.where(lines=='BEGIN IONS\n')
    ed = np.where(lines=='END IONS\n')
    p = np.where(lines=='SCANS='+str(scanindex)+'\n')
    bgp = bg[0][np.where((bg[0]-p[0])>0)[0][0]-1]
    edp = ed[0][np.where((ed[0]-p[0])>0)[0][0]]+1
    msms1 = []
    for line in lines[bgp:edp]:
        try:
            mz, rt = line.split(' ')
            msms1.append((float(mz), float(rt)))
        except:
            pass
    spectrum[scanindex] = pd.DataFrame(msms1, columns=['Mass', 'Intensity'])
    return(spectrum)


def plotXIC(mz, rt, exp, out, title='', type='XIC', format='png'):
    tic = getTIC(exp)
    xic = getXIC(mz, rt, tic, type='TI')
    if format=='pdf':
        pdf = matplotlib.backends.backend_pdf.PdfPages(out+'.pdf') 
    if type=='BPC':
        fig = plt.figure() 
        if title !='':
            fig.suptitle(title, fontsize=12)
        ax1 = fig.add_subplot(111) 
        ax1.plot(tic['rt'], [max(x) if len(x) else 0 for x in tic['i']], lw=2) 
        if format=='png':
            fig.savefig(out+'.png')
        elif format=='pdf':
            pdf.savefig( fig )   
            pdf.close() 
        plt.close('all') 
    if type=='BPC_XIC':
        fig = plt.figure() 
        if title !='':
            fig.suptitle(title, fontsize=12)
        ax1 = fig.add_subplot(111) 
        ax1.plot(tic['rt'], [max(x) if len(x) else 0 for x in tic['i']], lw=2) 
        ax1.plot(xic['rt'], xic['xic'], lw=2, color='r') 
        if format=='png':
            fig.savefig(out+'.png')
        elif format=='pdf':
            pdf.savefig( fig )   
            pdf.close() 
        plt.close('all') 
    if type=='XIC':
        fig = plt.figure() 
        ax1 = fig.add_subplot(111) 
        fig = plt.figure()
        if title !='':
            fig.suptitle(title, fontsize=12)
        ax1 = fig.add_subplot(111) 
        ax1.plot(xic['rt'], xic['xic'], lw=4, color='r') 
        if format=='png':
            fig.savefig(out+'.png')
        elif fot=='pdf':
            pdf.savefig( fig )   
            pdf.close() 
        plt.close('all') 
    exp.reset()

def expDict(fnames, path):
    edict = {}
    for fn in fnames:
        exp = loadExp(f'{path}/{fn}')
        tic = getTIC(exp)
        edict[fn] = tic
    return edict

def overlayXIC(fnames, meta, field, edict, mz, rt, fsz, title, 
                save=False, out='', **kwargs):
    cm = plt.get_cmap('gist_rainbow')
    classes =  meta[field].unique()

    cdict = {}
    for i in range(len(classes)):
        cdict[classes[i]] = i

    for k,v in cdict.items():
        cdict[k] = cm(v/3*3.0/len(cdict))

    for fn in fnames:
        #leg = re.sub('_MS1.*', '', fn)
        #cid = leg.split('_')[2]
        #fn.replace('mzXML', 'mzML')
        tic = edict[fn] 
        xic = getXIC(mz, rt, tic, **kwargs)
        k = meta.loc[meta.filename==fn, field].values[0]
        plt.plot(xic['rt'], xic['xic'], color=cdict[k], label=k, linewidth=0.5)
        #exp.reset()

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), fontsize=fsz)
    plt.title(title, fontsize=10)
    #plt.legend(list(cdict.keys()), fontsize=fsz)
    if save:
        plt.savefig(out)
        plt.close()
    else:
        plt.show()


