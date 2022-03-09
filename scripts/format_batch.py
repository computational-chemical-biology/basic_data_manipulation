import pandas as pd
import shutil
import xmltodict
import os
import sys


def splitFiles(inputs, names_table, col_name,
               out_folder, in_xml, out_xml,
               split_seq='_,-', isInt=True):
    fls = os.listdir(inputs)
    lote01 = pd.read_csv(names_table, sep='\t')
    if split_seq:
        split_seq = split_seq.split(',')
        sid = fls.copy()
        for p in split_seq:
            sid = [x.split(p)[0] for x in sid]

    if isInt:
        for i in range(len(sid)):
            try:
                sid[i] = int(sid[i])
            except:
                sid[i] = 0

    ls1 = set(sid).intersection(set(lote01[col_name]))

    s01 = []

    for i in range(len(sid)):
        if sid[i] in ls1:
            s01.append(i)

    os.mkdir(out_folder)

    with open(in_xml, 'rb') as f:
        auxxml = xmltodict.parse(f)

    [shutil.copyfile(f'{inputs}/{fls[i]}', f'{out_folder}/{fls[i]}') for i in s01]

    auxxml['batch']['batchstep'][0]['parameter']['file'] = [os.path.abspath(f'{out_folder}/{fls[i]}') for i in s01]

    with open(out_xml, 'w+') as result_file:
        result_file.write(xmltodict.unparse(auxxml, pretty=True))

if __name__=='__main__':
    parm = sys.argv
    splitFiles(inputs=parm[1], names_table=parm[2], col_name=parm[3],
               out_folder=parm[4], in_xml=parm[5], out_xml=parm[6])
