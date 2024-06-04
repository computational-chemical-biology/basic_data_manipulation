import os
import re
import jinja2
from jinja2 import Template
import numpy as np
import pandas as pd
import sys
import subprocess
import json
from scipy import stats

if __name__=='__main__':
    N = int(sys.argv[1])
    input = sys.argv[2]
    out = sys.argv[3]
    latex_jinja_env = jinja2.Environment(
       block_start_string = '\BLOCK{',
       block_end_string = '}',
       variable_start_string = '\VAR{',
       variable_end_string = '}',
       comment_start_string = '\#{',
       comment_end_string = '}',
       line_statement_prefix = '%-',
       line_comment_prefix = '%#',
       trim_blocks = True,
       autoescape = False,
       loader = jinja2.FileSystemLoader(os.path.abspath('.'))
    )
    sample_list = []
    for idx in range(N):
        # load template from file
        template1 = latex_jinja_env.get_template(os.path.join(input, 'prova_Ia.tex'))
        template2 = latex_jinja_env.get_template(os.path.join(input, 'prova_Ia_gabarito.tex'))
        # combine template and variables
        print('Writing the template for %s...' % idx)
        media1 = round(np.random.uniform(1800, 1900, 1)[0])
        std1 = round(np.random.uniform(100, 120, 1)[0])
        n1 = round(np.random.uniform(50, 60, 1)[0])
        media2 = 0
        while media2 < media1:
            media2 = round(np.random.uniform(1800, 2000, 1)[0])
        z1 = round((media2-media1)/(std1/np.sqrt(n1)), 3)
        if z1 > 2.33:
            dec1 = '\\(z_{obs} \\in RC\\), rejeitamos \(H_0\)'
        else:
            dec1 = '\\(z_{obs} \\notin RC\\), não rejeitamos \(H_0\)'

        media21 = round(np.random.uniform(10, 20, 1)[0])
        var1 = round(np.random.uniform(2, 4, 1)[0])
        n2 = round(np.random.uniform(16, 20, 1)[0])
        media22 = 0
        while media22 < media21:
            media22 = round(np.random.uniform(11, 21, 1)[0])
        t21 = round((media22-media21)/(np.sqrt(var1/n2)), 3)
        tc21 = round(stats.t.ppf(0.975, n2-1), 3)
        if t21 > tc21:
            dec21 = '\\(t_{obs} \\in RC\\), rejeitamos \(H_0\).'
        else:
            dec21 = '\\(t_{obs} \\notin RC\\), não rejeitamos \(H_0\).'

        tc22 = round(stats.t.ppf(0.95, n2-1), 3)
        if t21 > tc22:
            dec22 = '\\(t_{obs} \\in RC\\), rejeitamos \(H_0\).'
        else:
            dec22 = '\\(t_{obs} \\notin RC\\), não rejeitamos \(H_0\).'

        media31 = round(np.random.uniform(90, 100, 1)[0])
        std2 = round(np.random.uniform(50, 60, 1)[0])
        n3 = round(np.random.uniform(100, 120, 1)[0])
        tc31 = round(stats.t.ppf(0.995, n3-1), 3)
        lim_inf1 = round(media31 - tc31*(std2/np.sqrt(n3)), 3)
        lim_sup1 = round(media31 + tc31*(std2/np.sqrt(n3)), 3)

        tc32 = round(stats.t.ppf(0.975, n3-1), 3)
        lim_inf2 = round(media31 - tc32*(std2/np.sqrt(n3)), 3)
        lim_sup2 = round(media31 + tc32*(std2/np.sqrt(n3)), 3)
       
        media41 = round(np.random.uniform(8, 9, 1)[0])
        v1, v2, v3 = np.round(np.random.uniform(6, 17, 3))
        data41 = np.array([6.7, v1, 13.4, 12.4, 14.9, v2, 
                            16.5, 13.5, v3, 16.9, 9.1, 13.0]) 
        media42 = round(data41.mean(), 3)
        std3 = round(np.random.uniform(3, 4, 1)[0])

        z31 = round((media22-media21)/(std3/np.sqrt(12)), 3)
        if z31 > 1.96 or z31 < -1.96:
            dec3 = '\\(z_{obs} \\in RC\\), rejeitamos \(H_0\)'
        else:
            dec3 = '\\(z_{obs} \\notin RC\\), não rejeitamos \(H_0\)'

        sample_dict = {'sample': idx, 'media1': media1,
                       'std1': std1,'n1': n1, 'media2': media2,
                       'z1': z1, 'dec1': dec1, 'media21': media21, 'var1': var1, 'n2':n2,
                       'media22':media22, 't21':t21, 'tc21':tc21, 'dec21':dec21, 
                       'dec22':dec22, 'tc22':tc22, 'media31':media31, 'std2':std2, 'n3':n3,
                       'tc31':tc31, 'lim_inf1':lim_inf1, 'lim_sup1':lim_sup1, 'tc32':tc32,
                        'lim_inf2': lim_inf2, 'lim_sup2': lim_sup2, 'media41': media41, 'v1':v1,
                        'v2': v2, 'v3':v3, 'media42':media42, 'std3':std3, 'z31':z31, 'dec3':dec3}

        document1 = template1.render(**sample_dict)
        document2 = template2.render(**sample_dict)

        #write document
        with open(os.path.join(out, 'final-%s.tex' % idx),'w') as output:
            output.write(document1)

        with open(os.path.join(out, 'final-%s_gabarito.tex' % idx),'w') as output:
            output.write(document2)

        print('Compiling pdf for %s...' % idx)
        subprocess.call(['pdflatex', '--interaction=nonstopmode',
                        '-output-directory=%s' % out, os.path.join(out, 'final-%s.tex' % idx)])
        subprocess.call(['pdflatex', '--interaction=nonstopmode',
                        '-output-directory=%s' % out, os.path.join(out, 'final-%s_gabarito.tex' % idx)])

        sample_list.append(sample_dict)
        toclean = os.listdir(out)
        [os.remove(os.path.join(out, x)) for x in toclean if not bool(re.match('final-.+.pdf', x))]

    with open(os.path.join(out, 'gabarito_%s_pdfs.json' % N),'w') as output:
        json.dump(sample_list, output, indent=4)