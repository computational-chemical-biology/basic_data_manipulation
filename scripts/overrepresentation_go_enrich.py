# Based on tutorial:
#  https://github.com/tanghaibao/goatools/blob/main/notebooks/Enrichment_analyses_human_phenotype_ontology.ipynb
import pandas as pd
import numpy as np
from goatools.obo_parser import GODag
from goatools.base import download_go_basic_obo
from goatools.go_enrichment import GOEnrichmentStudy
import sys

# uniprot provides GO terms associated to protein ids
#https://www.uniprot.org/uniprotkb?fields=accession%2Creviewed%2Cid%2Cprotein_name%2Cgene_names%2Corganism_name%2Clength%2Cgene_oln%2Cgene_orf%2Cgene_primary%2Cgene_synonym%2Ccc_pathway%2Cec%2Crhea%2Cgo_p%2Cgo_c%2Cgo%2Cgo_f%2Cgo_id&query=Fusarium+oxysporum+NRRL+32931&view=table

def enrichGO(diff_express_table, population_ann):
    #df = pd.read_excel('dados_go.xlsx')
    df = diff_express_table

    obo_fname = download_go_basic_obo()
    obodag = GODag("go-basic.obo")

    #tab = pd.read_table('uniprotkb_Fusarium_oxysporum_NRRL_32931_2024_03_05.tsv', sep='\t')
    tab = population_ann
    gotab = tab[['Entry', 'Gene Ontology IDs']]
    gotab['Gene Ontology IDs'] = gotab['Gene Ontology IDs'].str.replace(' ','')
    gotab.fillna('', inplace=True)

    population_ids = set(gotab['Entry'])
    id2gos = {}
    for i in gotab.index:
        if gotab.iloc[i, 1]=='':
            population_ids = population_ids-{gotab.iloc[i, 0]}
        else:
            s = set(gotab.iloc[i, 1].split(';'))
            id2gos[gotab.iloc[i, 0]] = s

    goeaobj = GOEnrichmentStudy(
        population_ids,
        id2gos,
        obodag,
        methods=['bonferroni', 'fdr_bh'],
        pvalcalc='fisher_scipy_stats')

    # Remove!
    #(df['logfc_a3']==np.inf).sum()
    #df['logfc_a3'].abs()>0.5

    # select from multiple ids 
    #df.loc[df['logfc_a3'].abs()>0.5, 'Protein IDs'].apply(lambda a: a.split(';')[0])
    study_ids = set(df.loc[df['logfc_a3'].abs()>0.5, 'Protein IDs'].apply(lambda a: a.split(';')[0]))
    results = goeaobj.run_study_nts(study_ids)

    print('namespace       term_id  e/p pval_uncorr Benjamimi/Hochberg Bonferroni  study_ratio population_ratio')
    print('--------------- -------- --- ----------- ------------------ ----------  ----------- ----------------')
    pat = '{NS} {GO} {e}    {PVAL:8.2e}           {BH:8.2e}   {BONF:8.2e} {RS:>12} {RP:>12}'
    for ntd in sorted(results, key=lambda nt: [nt.p_uncorrected, nt.GO]):
        if ntd.p_fdr_bh < 0.05:
            print(pat.format(
                NS=ntd.NS,
                GO=ntd.GO,
                e=ntd.enrichment,
                RS='{}/{}'.format(*ntd.ratio_in_study),
                RP='{}/{}'.format(*ntd.ratio_in_pop),
                PVAL=ntd.p_uncorrected,
                BONF=ntd.p_bonferroni,
                BH=ntd.p_fdr_bh))
    print('e: enriched')
    print('p: purified')

if __name__=='__main__':
    df = pd.read_excel(sys.argv[1])
    tab = pd.read_table(sys.argv[2], sep='\t')
    enrichGO(df, tab)
