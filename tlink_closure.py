'''
Created on Jun 28, 2012

@author: yaocheng
'''

import sys
import re
import os
import subprocess

SPUTLINKDIR = '/Users/yaocheng/Desktop/i2b2/sputlink'

def preprocess_tlink(orgnl_path, pcd_path):
    '''
    process the xml file and output it in a format that can be
    processed in SputLink. The output file will be placed in the
    
    Args:
        orgnl_path: the MAE xml file to be processed
        pcd_path: output xml file
    '''
    with open(orgnl_path, 'r') as tf, open(pcd_path, 'w') as nf:
        lines=tf.readlines()
        nf.write('<fragment>\n<TEXT>\n')
        count=3
        #fix of handling the first TLINK
        firstTlinkFlag=0
        for i in range(3, len(lines)):
            if not re.search("]]><",lines[i]):
                #nf.write(lines[i])
                count+=1
            else:
                nf.write("</TEXT>\n")
                break
        count+=2
        for i in range(count, len(lines)): 
            if re.search("<EVENT id",lines[i]):
                lines[i]=lines[i].replace(" type=", " eventtype=")
                pre,post=lines[i].split(" id=")
                outline=pre+" eid="+post
                outline=outline.replace(' />','></EVENT>')
                while re.search('\s[&|\'|<|>]\s', outline):
                    outline=re.sub('\s[&|\'|<|>]\s',' ', outline)
                nf.write(outline)
            elif re.search("<TIMEX3 id",lines[i]):
                lines[i]=lines[i].replace(" type=", " timextype=")
                pre,post=lines[i].split(" id=")
                outline=pre+" tid="+post
                outline=outline.replace(' />','></TIMEX3>')
                while re.search('\s[&|\'|<|>]\s', outline):
                    outline=re.sub('\s[&|\'|<|>]\s',' ', outline)
                nf.write(outline)
            elif re.search("<SECTIME",lines[i]):
                lines[i]=lines[i].replace(" type=", " sectype=")
                nf.write(lines[i])
            elif re.search("<TLINK",lines[i]):
                if firstTlinkFlag==0:
                    nf.write('<TLINK></TLINK>\n')
                    firstTlinkFlag=1
                re_exp = 'id=\"([^"]*)\"\s+fromID=\"([^"]*)\"\s+fromText=\"([^"]*)\"\s+toID=\"([^"]*)\"\s+toText=\"([^"]*)\"\s+type=\"([^"]*)\"\s+\/>'
                m = re.search(re_exp, lines[i])
                if m:
                    tlid, fromid, fromtext, toid, totext, attr_type = m.groups()
                else:
                    raise Exception("Malformed EVENT tag: %s" % (lines[i]))
                attr_type=attr_type.replace('OVERLAP','SIMULTANEOUS')
                while re.search('[&|\'|<|>]', fromtext):
                    fromtext=re.sub('[&|\'|<|>]',' ', fromtext)
                while re.search('[&|\'|<|>]', totext):
                    totext=re.sub('[&|\'|<|>]',' ', totext)
                if fromid<>'' and toid<>'' and attr_type<>'':
                    outline='<TLINK lid=\"%s\"' % tlid
                    if re.search('E',fromid):
                        outline += ' fromEID=\"%s\" fromText=\"%s\"' % (fromid,fromtext)
                    else:
                        outline += ' fromTID=\"%s\" fromText=\"%s\"' % (fromid,fromtext)
                    if re.search('E',toid):
                        outline += ' toEID=\"%s\" toText=\"%s\" type=\"%s\" ></TLINK>' % (toid, totext,attr_type)
                    else:
                        outline += ' toTID=\"%s\" toText=\"%s\" type=\"%s\" ></TLINK>' % (toid,totext,attr_type)
                    nf.write(outline+'\n')
        nf.write('</fragment>')
    return

def calculate_closure(pcd_path, closure_path, twd=SPUTLINKDIR):
    doc_n = os.path.split(pcd_path)[1]
    doc_id = doc_n.split('.')[0]
    cwd = os.getcwd()
    os.chdir(twd)
    try:
        with open(os.path.join(twd + '_temp', doc_id + '.out'), 'w') as out:
            with open(os.path.join(twd + '_temp', doc_id + '.err'), 'w') as err:
                subprocess.call(['perl', 'merge.pl', \
                                 pcd_path, closure_path], stdout=out, stderr=err)
    except IOError:
        print '"temp" folder for subprocess could not be located'
    os.chdir(cwd)
    return

def main():
    orgnl_path = sys.argv[1]
    pcd_path = sys.argv[2]
    closure_path = sys.argv[3]
    preprocess_tlink(orgnl_path, pcd_path)
    calculate_closure(pcd_path, closure_path)
    return

if __name__ == '__main__':
    main()