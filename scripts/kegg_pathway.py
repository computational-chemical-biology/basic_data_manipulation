import pandas as pd
import requests
import io

import Bio
from Bio.KEGG.REST import *
from Bio.KEGG.KGML import KGML_parser
from Bio.Graphics.KGML_vis import KGMLCanvas
from Bio.Graphics.ColorSpiral import ColorSpiral
from IPython.display import Image, HTML


def getMolLibSearch(taskid):
    '''MOLECULAR-LIBRARYSEARCH-V2
    example 860c4bbf2db74f839a661f2b8d58de90
    '''
    url_to_db = "http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=DB_result/" % taskid
    dbmatch = pd.read_csv(io.StringIO(requests.get(url_to_db).text), sep='\t')
    return dbmatch

def getKeggPathways():
    pth = pd.read_csv('http://rest.kegg.jp/list/pathway', header=None, sep='\t')
    return pth

def inchikey2keggid(kegg_ref, inchikeys):
    '''Examples
     ~/python_libraries/pyclassrich/notebooks/kegg_database.tsv
     dbmatch.InChIKey
     '''
    kegg = pd.read_csv(kegg_ref, sep='\t')
    cpdlist = []
    for x in kegg.loc[kegg.InChIKey.isin(inchikeys), 'KEGGID']:
        try:
            cpdlist.append(pd.read_csv('http://rest.kegg.jp/link/pathway/%s' % x, header=None, sep='\t'))
        except:
            print('No pathway for %s.' % x)
    return cpdlist

def draw_kegg_map(map_id):
    """ Render a local PDF of a KEGG map with the passed map ID
    """
    # Get the background image first
    pathway = KGML_parser.read(kegg_get(map_id, "kgml"))
    canvas = KGMLCanvas(pathway, import_imagemap=True)
    img_filename = "%s.pdf" % map_id
    canvas.draw(img_filename)

def colorCompounds(pathname, cpdlist, size=20):
    pathway = KGML_parser.read(kegg_get(pathname, "kgml"))
    for element in pathway.compounds:
        for graphic in element.graphics:
            if graphic.name in cpdlist:
                graphic.bgcolor = '#ff0000'
                graphic.width = size
                graphic.height = size
    canvas = KGMLCanvas(pathway, import_imagemap=True)
    canvas.draw("%s.pdf" % pathname)

#element = pathway.orthologs[0].graphics[0]
#attrs = [element.name, element.x, element.y, element.coords, element.type,
#         element.width, element.height, element.fgcolor, element.bgcolor,
#                  element.bounds, element.centre]

if __name__=='__main__':
    parm = sys.argv
    dbmatch = getMolLibSearch(param[1])
    cpdlist = inchikey2keggid(param[2], dbmatch.InChIKey)
    cpd = pd.concat(cpdlist)
    pth = getKeggPathways()
    cpd = pd.merge(cpd, pth, left_on=1, right_on=0)
    print(cpd.iloc[:,4].value_counts())
    selpath= cpd[1].value_counts()[cpd[1].value_counts()>2].index
    #draw_kegg_map('ko00260')
    for s in selpath[2:]:
        try:
            clist = cpd.loc[cpd[1]==s,cpd.columns[1]].str.replace('cpd:', '').tolist()
            colorCompounds(s.replace('path:map', 'ko'), clist)
        except:
            print('Problems in %s' % s.replace('path:map', 'ko'))
            pass


