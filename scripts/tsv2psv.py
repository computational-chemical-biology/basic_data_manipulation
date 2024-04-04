import pandas as pd
import sys

def tsv2psv(data_frame):
    df = pd.read_csv(data_frame, sep='\t')
    df.to_csv(data_frame.replace('.tsv', '.psv'), sep='|', index=None)

if __name__=='__main__':
    tsv2psv(sys.argv[1])
