import pandas as pd

df = pd.read_csv('Dados_trat_estatístico.tsv', sep='\t',decimal=',')
hlp_hff = df.loc[:4].T
hlp_hff.drop(['HLP-GE', 'Linhagem celular 1: HFF-1', 'Unnamed: 2', 'Unnamed: 15'], inplace=True)
hlp_hff.drop(0, axis=1, inplace=True)
hlp_hff = pd.melt(hlp_hff, id_vars=[1], value_vars=[2, 3, 4])
hlp_hff.drop('variable', axis=1, inplace=True)
hlp_hff.rename(columns={1:'ug/mL', 'value':'viabilidade'}, inplace=True)
hlp_hff['metodo'] = 'hlp_ge'
hlp_hff['linhagem'] = 'hff1'
hlp_hff['ug/mL']= hlp_hff['ug/mL'].astype(float)
hlp_hff.sort_values('ug/mL', inplace=True)

hlp_skmel28 = df.loc[5:10].T
hlp_skmel28.drop(['HLP-GE', 'Linhagem celular 1: HFF-1', 'Unnamed: 2', 'Unnamed: 15'], inplace=True)
hlp_skmel28.drop([5, 6], axis=1, inplace=True)
hlp_skmel28 = pd.melt(hlp_skmel28, id_vars=[7], value_vars=[8, 9, 10])
hlp_skmel28.drop('variable', axis=1, inplace=True)
hlp_skmel28.rename(columns={7:'ug/mL', 'value':'viabilidade'}, inplace=True)
hlp_skmel28['metodo'] = 'hlp_ge'
hlp_skmel28['linhagem'] = 'skmel28'
hlp_skmel28['ug/mL']= hlp_skmel28['ug/mL'].astype(float)
hlp_skmel28.sort_values('ug/mL', inplace=True)

ge_hff = df.loc[11:16].T
ge_hff.drop(['HLP-GE', 'Linhagem celular 1: HFF-1', 'Unnamed: 2', 'Unnamed: 15'], inplace=True)
ge_hff.drop([11, 12], axis=1, inplace=True)
ge_hff = pd.melt(ge_hff, id_vars=[13], value_vars=[14, 15, 16])
ge_hff.drop('variable', axis=1, inplace=True)
ge_hff.rename(columns={13:'ug/mL', 'value':'viabilidade'}, inplace=True)
ge_hff['metodo'] = 'ge'
ge_hff['linhagem'] = 'hff1'
ge_hff['ug/mL']= ge_hff['ug/mL'].astype(float)
ge_hff.sort_values('ug/mL', inplace=True)

ge_skmel28 = df.loc[17:].T
ge_skmel28.drop(['HLP-GE', 'Linhagem celular 1: HFF-1', 'Unnamed: 2', 'Unnamed: 15'], inplace=True)
ge_skmel28.drop([17, 18], axis=1, inplace=True)
ge_skmel28 = pd.melt(ge_skmel28, id_vars=[19], value_vars=[20, 21, 22])
ge_skmel28.drop('variable', axis=1, inplace=True)
ge_skmel28.rename(columns={19:'ug/mL', 'value':'viabilidade'}, inplace=True)
ge_skmel28['metodo'] = 'ge'
ge_skmel28['linhagem'] = 'skmel28'
ge_skmel28['ug/mL']= ge_skmel28['ug/mL'].astype(float)
ge_skmel28.sort_values('ug/mL', inplace=True)

df_format = pd.concat([hlp_hff, hlp_skmel28, ge_hff, ge_skmel28])
df_format.viabilidade = df_format.viabilidade.astype(str).str.replace(',', '.').astype(float)
df_format.to_csv('yasmin_rlongformat.tsv', sep='\t', index=None)
