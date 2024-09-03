import pandas as pd
import json

def getPathwayByGene(geneID, orgID='afm'):
    try:
        pth = pd.read_csv(f'https://rest.kegg.jp/link/pathway/{orgID}:{geneID}', 
                          sep='\t', header=None)
    except:
        return {}
    return {geneID : pth[1].tolist()}

def getCompoundsbyPathway(pathID, orgID='afm'):
    pathID = pathID.replace(f'path:{orgID}', 'map')
    try:
        cpds = pd.read_csv(f'https://rest.kegg.jp/link/compound/{pathID}', 
                          sep='\t', header=None)
    except:
        return {}
    return {pathID : cpds[1].tolist()}

def dict2tab(d):
    l = []
    for k,v in d.items():
        l.append(pd.DataFrame([[k]*len(v), v]).T)
    return pd.concat(l)

def id2name(kID):
    names = pd.read_csv(f'https://rest.kegg.jp/list/{kID}', 
                          sep='\t', header=None)
    return names

if __name__=='__main__':
    d1 = pd.read_excel('remetablitossecundrios/control_3519_3297_Psig.xlsx')
    d2 = pd.read_excel('remetablitossecundrios/control_3546_3297_Psig.xlsx')
    d3 = pd.read_excel('remetablitossecundrios/control_3546_3519_Psig.xlsx')
    genes = d1.gene.tolist()+d2.gene.tolist()+d3.gene.tolist()
    genes = list(set(genes))
    d = {}

    for i,g in enumerate(genes):
        print(f'Retrieving gene {g}, item {i} from 2116...')
        d.update(getPathwayByGene(g))

    with open('afm_path_by_gene.json', 'w') as f:
        json.dump(d, f, indent=True)

    p = {}

    for k,v in d.items():
        print(f'Retrieving compounds for gene {k} in', len(d)-i, 'genes...')
        for pt in v:
            p.update(getCompoundsbyPathway(pt))
        i += 1

    #%history -g -f  gene2pth.py
    with open('afm_compound_by_path.json', 'w') as f:
        json.dump(p, f, indent=True)

    g2pth = dict2tab(d)
    pth2cpd = dict2tab(p)
    pth2cpd[0] = pth2cpd[0].str.replace('map', 'path:afm')
    allinfo = pd.merge(g2pth, pth2cpd, left_on=1, right_on=0)
    allinfo.to_csv('afm_genes2pathways2compounds.tsv', sep='\t', index=None)

    chemwalker = pd.read_csv('goldman_full_output_file_inchikey.tsv', sep='\t')
    kegg = pd.read_csv('kegg_db/python_libraries/pyclassrich/notebooks/kegg_database.tsv', sep='\t')
    all_annot = pd.merge(kegg[['KEGGID', 'InChIKey']], chemwalker[['cluster index', 'InChIKey']], on='InChIKey')
    chemwalker = chemwalker.groupby('cluster index').first()
    chemwalker.reset_index(inplace=True)
    all_annot = pd.merge(kegg[['KEGGID', 'InChIKey']], chemwalker[['cluster index', 'InChIKey']], on='InChIKey')
    match_annot = pd.merge(allinfo, all_annot, left_on='1_y', right_on='KEGGID')

    nms = [id2name(x).replace('path:afm', 'map') for x in match_annot[1].unique()]
    pnms = pd.concat(nms)

    knms = [id2name(x) for x in match_annot['KEGGID'].unique()]
    knms = pd.concat(knms)

    gnms = [id2name(f'afm:{x}') for x in match_annot['0_x'].unique()]

    gnms[0] = gnms[0].str.replace('afm:', '')
    match_annot['gene_names']  = match_annot['0_x'].map(dict(zip(gnms[0],gnms[1])))

    knms[0] = 'cpd:'+knms[0]
    match_annot['compound_names']  = match_annot['KEGGID'].map(dict(zip(knms[0],knms[1])))

    pnms[0] = 'path:'+pnms[0]
    match_annot['pathway_names']  = match_annot[1].map(dict(zip(pnms[0],pnms[1])))
    match_annot.to_csv('gene2pathway2compound.tsv', sep='\t', index=None)



