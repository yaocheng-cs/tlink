'''
Created on Aug 9, 2012

@author: yaocheng
'''

import os
from lxml import etree
from project_path import project_base, data_pre_2
from both import main

def main():
    input_folder = project_base + '/' + data_pre_2 + '_i'
    output_folder = project_base + '/' + data_pre_2 + '_pred'
    
    file_names = os.listdir(input_folder)
    for fn in file_names:
        if fn[0] == '.':
            continue
        doc_id = os.path.basename(fn).split('.')[0]
        parser = etree.XMLParser(recover=True)
        try:
            tree = etree.parse(os.path.join(input_folder, fn), parser)
        except:
            print 'Something wrong with opening/parsing specified input xml file'
            raise
        root = tree.getroot()
        tags = root.find('TAGS')
        
        # for evaluation purpose, remove original tlink
        tlinks = tags.findall('TLINK')
        for tl in tlinks:
            tags.remove(tl)
        
        doc = ds.id2doc[doc_id]
        counter = 0
        for tl in doc.h_tlinks:
            if tl.pred == 'NONE':
                continue
            tl_elmt = etree.Element('TLINK')
            tl_elmt.set('id', 'TL' + str(counter))
            tl_elmt.set('fromID', tl.from_trgt.name)
            tl_elmt.set('fromText', str(tl.from_trgt))
            tl_elmt.set('toID', tl.to_trgt.name)
            tl_elmt.set('toText', str(tl.to_trgt))
            tl_elmt.set('type', tl.pred)
            # the 'tail' is set so that each TLINK will start from a new line
            tl_elmt.tail = '\n'
            tags.append(tl_elmt)
            counter += 1
            
        output_path = output_folder + '/' + doc_id + '.xml'
        with open(output_path, 'w') as fp:
            fp.write(etree.tostring(root, xml_declaration=True).replace('/>', ' />'))
            
    return

if __name__ == '__main__':
    main()
        
        