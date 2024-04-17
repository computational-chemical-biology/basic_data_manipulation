import sys
import re

def removeMultBlank(infname, outfname):
    fl = []
    with open(infname) as infile:
        for line in infile:
            fl.append(line)

    fl = [re.sub('\s{2,}', ' ', x) for x in fl]
    with open(outfname, 'w') as outfile:
        for line in fl:
            outfile.write(line)

if __name__=='__main__':
    removeMultBlank(sys.argv[1], sys.argv[2])
