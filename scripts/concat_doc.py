import os
import re
import sys

if __name__=='__main__':
    d = sys.argv[1]
    print('Entering directory: %s' % d)
    os.chdir(d)
    fls = os.listdir()
    ids = [x.split('_')[0] for x in fls]
    ids = list(set(ids))
    for idx in ids:
        print('Concatenating doc %s' % idx)
        tmp = [x for x in fls if x.split('_')[0] in idx]
        tmp_id = [int(re.sub('.+_(\d+).pdf', '\\1', x)) for x in tmp]
        sfls = [x for _, x in sorted(zip(tmp_id, tmp))]
        cmd = 'pdftk %s cat output %s' % (' '.join(sfls), '%s.pdf' % idx)
        os.system(cmd)
