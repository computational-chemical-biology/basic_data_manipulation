import xmltodict
import os
import subprocess
import sys
import shutil

def main(args):
    with open(args[1], 'rb') as f:
        xml = xmltodict.parse(f)

    pth = os.path.abspath(args[2])
    opth = os.path.abspath(args[3])

    fls = os.listdir(args[2])
    fls = [os.path.join(pth, x) for x in fls]

    for i in range(len(xml['batch']['batchstep'])):
        if 'RawDataImportModule' in xml['batch']['batchstep'][i]['@method']:
            xml['batch']['batchstep'][0]['parameter']['file'] = fls
        if 'CSVExportModule' in xml['batch']['batchstep'][i]['@method']:
            xml['batch']['batchstep'][i]['parameter'][1]['current_file'] = os.path.join(opth, 'peak_table.csv')
        if 'SiriusExport' in xml['batch']['batchstep'][i]['@method']:
            xml['batch']['batchstep'][i]['parameter'][2]['current_file'] = os.path.join(opth, 'sirius.mgf')
            xml['batch']['batchstep'][i]['parameter'][2]['last_file'] = os.path.join(opth, 'sirius.mgf')

    oxml = os.path.join(opth, 'result.xml')
    with open(oxml, 'w+') as result_file:
        result_file.write(xmltodict.unparse(xml, pretty=True))

    mzmine = args[0]
    subprocess.call(['sh', mzmine, oxml])
    #os.remove(oxml)

if __name__ == "__main__":
    main(sys.argv[1:])
