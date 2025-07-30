import requests
import xmltodict
import json
import sys
import xmltodict
import json

taskid = 'b6d863f7266f4bb7a0918e576abe64fb'
url = 'https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task=%s&block=main&file=params/' % taskid
resp = requests.get(url)
parm = xmltodict.parse(resp.content)
mapping = []
for p in parm['parameters']['parameter']:
    if p['@name']=='upload_file_mapping':
       mapping.append(p)

for m in mapping:
    if 'speclibs' in m['#text']:
        old, new = m['#text'].split('|')
        url_spec = f"https://gnps.ucsd.edu/ProteoSAFe/DownloadResultFile?task={taskid}&block=main&file=lib/{old}"
        try:
            r = requests.get(url_spec, stream=True)
        except:
            continue
        if r.status_code == 200:
            with open(new.split('/')[-1], 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
