import pandas as pd
import io
import requests

if __name__=='__main__':
    taskid01 = ['6ffbbdf86c864aa6b781701c0fc6588b']
    taskid02 = ['76d8ebfe8fc44b46ba05c7e4df1e0ac1']
    taskid03 = ['cc3e4612bb8e472da33dfa7214c9481f']

    url_to_db = "http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=DB_result/" % (taskid[0])
    url_to_edges = "http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=networking_pairs_results_file_filtered/" % (taskid[0])
    dbmatch = pd.read_csv(io.StringIO(requests.get(url_to_db).text), sep='\t')
    net = pd.read_csv(io.StringIO(requests.get(url_to_edges).text), sep='\t')

    uni01 = pd.merge(uni01, dbmatch, left_on='row ID', right_on='#Scan#', how='left')
    net01 = net[net.CLUSTERID1.isin(dbmatch['#Scan#']) | net.CLUSTERID2.isin(dbmatch['#Scan#'])]

    nodes = list(set(net01.CLUSTERID1.tolist()+net01.CLUSTERID2.tolist()))
    for i in uni03.index:
        n = uni03.loc[i, 'row ID']
        if n in nodes:
            c = net03.loc[(net03.CLUSTERID1==n) | (net03.CLUSTERID2==n), 'ComponentIndex'].tolist()[0]
            print('found connection to component:%s' % c)
            if pd.isna(uni03.loc[i, '#Scan#']):
                uni03.loc[i, '#Scan#'] = 'component:%s' % c

    uni02.to_csv('feats_lote01_annotated.tsv', sep='\t', index=None)
