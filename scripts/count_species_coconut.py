from rdkit import Chem
# NPMINE: in house package to be published
from npmine.postprocessing import sci_name_dict2dataframe
# gnfinder file
# gnfinder find -c -l eng -s 4,12 articles.tsv > articles.txt
import json
import sys

def getTaxa(sdf):
    taxa = []
    suppl = Chem.SDMolSupplier(sdf)
    for mol in suppl:
        if mol==None:
            continue
        np = mol.GetPropsAsDict()
        if "textTaxa" in np.keys() and "notax" not in np["textTaxa"] and len(np["textTaxa"])>0:
            taxa.append(np["textTaxa"])


    staxa = []
    for t in taxa:
        staxa.extend(re.sub('^\[|\]$', '', t).split(','))

    staxa = list(set(staxa))
    staxa = [re.sub('^ | $', '', x) for x in staxa]
    return staxa

def loadGnfinder(txt):
    with open(txt) as f:
        gn = json.load(f)
    return gn

if __name__=='__main__':
    filename = sys.argv[1]
    if '.sdf' in filename:
        print('Reading sdf file...')
        staxa = getTaxa(filename)

        print('Found %s taxa (mostly species) in coconut' % len(set(staxa)))
        print('%s contains Unknown in the name' % len([x for x in staxa if 'Unknown' in x]))
        print('Species genera %s' % len(set([x.split(' ')[0] for x in staxa])))
    elif '.txt' in filename:
        print('Reading gnfinder result file...')
        gn = loadGnfinder(filename)
        nms = sci_name_dict2dataframe(gn, 'source')
        print('Number of species detected by gnfinder %s' % len(nms.verbatim.unique()))

