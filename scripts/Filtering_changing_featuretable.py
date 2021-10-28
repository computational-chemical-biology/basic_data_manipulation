import io
import requests
import pandas as pd
import sys



def taskid_table(taskid, mode):
    """
    Takes strings parameters (taskid and mode) and generate two tables.

    First table features the triplicates groups and metabolites. If the quant from mzmine is non-zero in
    two of three triplicates then its value is set to True but if it is non-zero in just one and zero in
    two replicates its value will be False.

    For example if you have group triplicate A, that have the samples with abundances for an specific
    metabolite like this [0,0,1], the value for this metabolite in this groups will be False. Otherwise,
    if the abundances are like [1,1,0], its value will be True.

    Second table is as the input feature table (with features and samples), but the samples values of
    the triplicates groups for an metabolite that are False will be set to 0. While if the values are
    True, they'll remain the same in the table.

    These tables can be filtered to only contain the metabolites that are non-zero from at least two
    replicates in all triplicates groups. It means that all metabolites that have any False value in any
    group will be dropped. You can also filter the tables to have only an especific triplicate group and
    the metabolites that are True for this group.
    Or you can generate tables without the filter to have all values and groups.

    Parameters:
    taskid (str): taskid provided by user

    mode (str): With this parameter you choose if you will filter the generated tables. Options are:
    
        'all_with_filter' : you filter these tables so they will have all triplicate groups (all samples)
        and only metabolites that the quant from mzmine is non-zero in two of three triplicates for all
        replicates groups.

        any triplicate group name : If you only want a specific group of triplicates in the table,
        you can use the name of this group as this parameter like for example 'A' and the generated table
        will contain this group and the metabolites which are non-zero in two of the three triplicates
        for this group.

        'all_no_filter' : both tables generated with all metabolites and triplicates will be generated
        without filter, having all values.
    """

    base_url = 'http://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task='
    url_to_metadata = f'{base_url}{taskid}&block=main&file=metadata_table/'
    url_to_features = f'{base_url}{taskid}&block=main&file=quantification_table/'
    meta = pd.read_csv(io.StringIO(requests.get(url_to_metadata).text), sep='\t')
    feat = pd.read_csv(io.StringIO(requests.get(url_to_features, verify=False).text))
    feat.columns = feat.columns.str.replace(' Peak area', '')
    list_triplicates = list(meta['ATTRIBUTE_triplicate'].unique())  
    newdfdict = {}
    dictsamples = {}

    for key in list_triplicates:
        selected_files = meta.loc[meta['ATTRIBUTE_triplicate'] == key, 'filename'].values.tolist()  
        dictsamples[key] = selected_files  
        newdfdict[key] = feat[selected_files].apply(lambda a: (a > 0).sum() > 1, axis=1)

    df = pd.DataFrame.from_dict(newdfdict)
    feat2 = feat[feat.columns[:-1]]

    for a in df.columns:
        for i in feat.index:
            if df.at[i, a] == False:
                selected_files = dictsamples[a]
                for b in selected_files:
                    if feat2.at[i, b] != 0:
                        feat2.at[i, b] = 0

    df['row ID'] = feat[['row ID']]
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df1 = df[cols]

    feat2.columns = feat2.columns.map(lambda x: x + ' Peak area' if x not in ['row ID', 'row m/z', 'row retention time'] else x)
    
    # filter starts below, you can remove the conditional structure and copy/paste
    # the last elif if don't want any filter in the table (but because this is a parameter
    # you'll need to exclude it from the function)
    if mode == 'all_with_filter':
        df2 = df1[(df1 > 0).all(axis=1)]
        feat2 = feat2[feat2['row ID'].isin(df2['row ID'].values.tolist())]
        df2.to_csv('only_True_for_all_triplicate_groups.tsv', sep='\t', index=False)
        feat2.to_csv('only_True_for_all_triplicate_groups_samples_table.tsv', sep='\t', index=False)
    elif mode in list_triplicates:
        df1 = df1[['row ID', mode]]
        df2 = df1[['row ID', mode]][df1[mode] > 0]
        collumns_names_peakarea = [sub + ' Peak area' for sub in dictsamples[mode]]
        col_list = ['row ID', 'row m/z', 'row retention time'] + collumns_names_peakarea
        feat2 = feat2[col_list][feat2['row ID'].isin(df2['row ID'].values.tolist())]
        df1.to_csv(f'only_{mode}.tsv', sep='\t', index=False)
        feat2.to_csv(f'only_{mode}_samples.tsv', sep='\t', index=False)
    elif mode == 'all_no_filter':
        df1.to_csv('all_features_triplicatesgroups.tsv', sep='\t', index=False)
        feat2.to_csv('all_features_samples.tsv', sep='\t', index=False)

if __name__ == '__main__':
    taskid_table(sys.argv[1], sys.argv[2])