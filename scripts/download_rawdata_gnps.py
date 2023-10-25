import requests
import xmltodict
import json
import sys

def downloadRawData(taskid):
    #url = 'https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=ed67aa1dddb644bdaa3660c97182eeec&block=main&file=params/'
    url = 'https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=params/' % taskid
    resp = requests.get(url)
    parm = xmltodict.parse(resp.content)

    mapping = []
    for p in parm['parameters']['parameter']:
        if p['@name']=='upload_file_mapping':
           mapping.append(p)

    for m in mapping:
        old, new = m['#text'].split('|')
        url_spec = f"https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={taskid}&block=main&file=spec/{old}"
        r = requests.get(url_spec, stream=True)
        with open(new.split('/')[-1], 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    #f.flush() commented by recommendation from

if __name__=='__main__':
    downloadRawData(sys.argv[1])
