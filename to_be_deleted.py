'''
Created on Jun 21, 2012

@author: yaocheng
'''

import sys
from lxml import etree
from nltk import Tree

UIMA_PREFIX = 'uima.tcas.'
CTAKES_PREFIX = 'edu.mayo.bmi.uima.core.type.'
MITRE_PREFIX = 'org.mitre.medfacts.type.'

def find_sentence_begin_at(pos, root):
    buf = root.xpath(CTAKES_PREFIX + 
                     'textspan.Sentence[@begin=%(pos)s]' \
                     % {'pos': pos})
    try:
        return buf[0]
    except IndexError:
        print 'cannot find sentence begins at %(pos)s' % {'pos': pos}
        return

def find_token_begin_at(pos, root):
    buf = []
    for t in ['Word', 'Punctuation', 'Num', 'Symbol', 'Contraction']:
        buf.extend(root.xpath(CTAKES_PREFIX + 
                              'syntax.%(t_type)sToken[@begin=%(pos)s]' \
                              % {'t_type': t, 'pos': pos}))
    try:
        return buf[0]
    except IndexError:
        print 'cannot find token begins at %(pos)s' % {'pos': pos}
        return

def find_token_end_at(pos, root):
    buf = []
    for t in ['Word', 'Punctuation', 'Num', 'Symbol', 'Contraction']:
        buf.extend(root.xpath(CTAKES_PREFIX + 
                              'syntax.%(t_type)sToken[@end=%(pos)s]' \
                              % {'t_type': t, 'pos': pos}))
    try:
        return buf[0]
    except IndexError:
        print 'cannot find token ends at %(pos)s' % {'pos': pos}
        return

def main():
    with open(sys.argv[1], 'r') as src, open(sys.argv[2], 'w') as des:
        tree = etree.parse(src)
        root = tree.getroot()
        e_doc = root.find(UIMA_PREFIX + 'DocumentAnnotation')
        doc_end = int(e_doc.get('end'))
        # set cursor as the "beginning character index", which is 0, of the document,
        # to search for the first sentence
        cursor = 0
        i2b2_sid = 0
        while cursor < doc_end:
            
            e_sent = find_sentence_begin_at(cursor, root)
            if not e_sent:
                cursor = cursor + 1
                if cursor >= doc_end:
                    break
                e_sent = find_sentence_begin_at(cursor, root)
                
            e_sent.set('i2b2_sid', str(i2b2_sid))
            sent_end = int(e_sent.get('end'))
            i2b2_tid = 0
            while cursor < sent_end:
                
                e_token = find_token_begin_at(cursor, root)
                if not e_token:
                    cursor = cursor + 1
                    if cursor >= sent_end:
                        break
                    e_token = find_token_begin_at(cursor, root)
                #print e_token.attrib['normalizedForm']
                
                e_token.set('i2b2_sid', str(i2b2_sid))
                e_token.set('i2b2_tid', str(i2b2_tid))
                token_end = int(e_token.get('end'))
                cursor = token_end + 1
                i2b2_tid = i2b2_tid + 1
            i2b2_sid = i2b2_sid + 1
            
        group1 =         ['syntax.INTJ', 
                          'syntax.LST', 
                          'syntax.NP', 
                          'syntax.O', 
                          'syntax.PP', 
                          'syntax.PRT', 
                          'syntax.SBAR', 
                          'syntax.UCP', 
                          'syntax.VP', 
                          'syntax.ADJP', 
                          'syntax.ADVP', 
                          'syntax.CONJP', 
                          'syntax.ConllDependencyNode', 
                          'syntax.TerminalTreebankNode', 
                          'syntax.TopTreebankNode', 
                          'textsem.MeasurementAnnotation', 
                          'textsem.Modifier', 
                          'textsem.PersonTitleAnnotation', 
                          'textsem.RangeAnnotation', 
                          'textsem.RomanNumeralAnnotation', 
                          'textsem.TimeAnnotation', 
                          'textsem.TimeMention', 
                          'textsem.ContextAnnotation', 
                          'textsem.DateAnnotation', 
                          'textsem.EntityMention', 
                          'textsem.MedicationEventMention', 
                          'textsem.FractionAnnotation', 
                          'textsem.Predicate', 
                          'textsem.SemanticArgument', 
                          'textspan.LookupWindowAnnotation']
        
        group2 = ['Assertion', 'Concept']
        
        annt_types = [CTAKES_PREFIX + t1 for t1 in group1]
        annt_types.extend([MITRE_PREFIX + t2 for t2 in group2])
        
        for t in annt_types: 
            for e_annt in root.findall(t):
                begin = e_annt.get('begin')
                end = e_annt.get('end')
                begin_token = find_token_begin_at(begin, root)
                end_token = find_token_end_at(end, root)
                if begin_token.get('i2b2_sid') != end_token.get('i2b2_sid'):
                    print 'sentence IDs do not match'
                else:
                    if int(begin_token.get('i2b2_tid')) > int(end_token.get('i2b2_tid')):
                        print 'begin token has a bigger ID then end token'
                    else:
                        e_annt.set('i2b2_sid', begin_token.get('i2b2_sid'))
                        e_annt.set('i2b2_tid_begin', begin_token.get('i2b2_tid'))
                        e_annt.set('i2b2_tid_end', end_token.get('i2b2_tid'))
        
        tree.write(des)
        
        
    return

def get_dependency_tree(lxml_tree):
    lxml_root = lxml_tree.getroot()
    dep_sents = lxml_root.xpath(CTAKES_PREFIX + 'syntax.ConllDependencyNode[@id=0]')
    dep_trees = []
    for s in dep_sents:
        _id = s.attrib['_id']
        s_head = lxml_root.xpath(CTAKES_PREFIX + 'syntax.ConllDependencyNode[@_ref_head=%(_id)s]' % {'_id': _id})
        dep_tree = Tree(s_head.attrib['postag'], get_dependents(s_head, lxml_root))
        dep_trees.append(dep_tree)
    return dep_trees

def get_dependents(lxml_elmt, lxml_root):
    _id = lxml_elmt.attrib['_id']
    form = lxml_elmt.attrib['form']
    e_id = lxml_elmt.attrib['id']
    buf = lxml_root.xpath(CTAKES_PREFIX + 'syntax.ConllDependencyNode[@_ref_head=%(_id)s]' % {'_id': _id})
    if len(buf) == 0:
        return [form]
    else:
        buf_id = [e.attrib['id'] for e in buf]
        index = 0
        while int(buf_id[index]) <= int(e_id):
            index = index + 1
        return [get_dependents[e] for e in buf].insert(form)
    return

def get_common_head(dep_nodes):
    if len(dep_nodes) == 1:
        return dep_nodes[0]
    if len(dep_nodes) == 0:
        return None
    
    paths = []
    for dn in dep_nodes:
        path = []
        nxt = dn
        while nxt:
            path.append(nxt)
            nxt = nxt.head
        paths.append(path)
        
    old = None
    empty = False
    for p in paths:
        empty = empty or p == []
    while not empty:
        new = []
        try:
            for p in paths:
                new.append(p.pop(-1))
        except IndexError:
            empty = True
            continue
        if len(set(new)) == 1:
            old = new[0]
        else:
            break
    return old

def _find_chunk_elmt(self):
    buf = []
    for chunk_type in ['INTJ', 'LST', 'NP', 'O', 'PP', 'PRT', 'SBAR',
                       'UCP', 'VP', 'ADJP', 'ADVP', 'CONJP']:
        tag = self.CTAKES_PREFIX + 'syntax.' + chunk_type
        buf += self.c_root.findall(tag)
    return buf

if __name__ == '__main__':
    main()