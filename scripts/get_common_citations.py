import requests
import json
import sys

# 10.1038/s41592-020-0933-6
# 10.1093/nar/gky310
def commonCitation(doi1, doi2):
    txt = requests.get('https://opencitations.net/index/coci/api/v1/citations/%s' % doi1).text
    fbmn = json.loads(txt)
    fbmn = [x['citing'] for x in fbmn]

    txt = requests.get('https://opencitations.net/index/coci/api/v1/citations/%s' % doi2).text
    met = json.loads(txt)
    met = [x['citing'] for x in met]
    return set(fbmn).intersection(set(met))

if __name__=='__main__':
    print(commonCitation(sys.argv[1], sys.argv[1]))
