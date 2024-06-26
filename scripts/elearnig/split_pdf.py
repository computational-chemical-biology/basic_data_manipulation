import os
import sys

def pdf_split(filename, numpages, out):
    totpg = os.popen(f"pdftk {filename} dump_data | grep NumberOfPages | cut -d ' ' -f 2").read().strip()
    pglist = list(range(1, int(totpg), int(numpages)))
    pglist.append(int(totpg)+1)
    l = len(pglist)
    k = 1
    out = os.path.join(out, filename.split('/')[-1])
    for i in range(0, l):
        os.system(f'pdftk {filename} cat {pglist[i]}-{pglist[i+1]-1} output {out.replace(".pdf", "")}_out{k}.pdf')
        k += 1

if __name__=="__main__":
    print(sys.argv)
    pdf_split(sys.argv[1], sys.argv[2], sys.argv[3])

