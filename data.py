'''
Created on Jul 6, 2012

@author: yaocheng
'''

import os
import sys
import re
import cPickle
from lxml import etree
from nltk.tree import Tree

CTAKES_PREFIX = 'edu.mayo.bmi.uima.core.type.'

class Dataset(object):
    """
    A collection of documents, prepared for data pickling
    """
    
    def __init__(self, i2b2_folder_path, ctakes_folder_path, parse_folder_path, closure_folder_path=None):
        self.docs = {}
        
        self._i2b2_f = i2b2_folder_path
        self._ctakes_f = ctakes_folder_path
        self._parse_f = parse_folder_path
        self._closure_f = closure_folder_path
        
        self._register_docs()
    
    def _register_docs(self):
        counter = 0
        for p in os.listdir(self._i2b2_f):
            doc_id = os.path.basename(p).split('.')[0]
            try:
                if not self._closure_f:
                    doc = Document(doc_id, \
                                   os.path.join(self._i2b2_f, doc_id + '.xml'), \
                                   os.path.join(self._ctakes_f, doc_id + '.xml.txt.xml'), \
                                   os.path.join(self._parse_f, doc_id + '.xml.cleaned.parsed.txt'))
                else:
                    doc = Document(doc_id, \
                                   os.path.join(self._i2b2_f, doc_id + '.xml'), \
                                   os.path.join(self._ctakes_f, doc_id + '.xml.txt.xml'), \
                                   os.path.join(self._parse_f, doc_id + '.xml.cleaned.parsed.txt'), \
                                   os.path.join(self._closure_f, doc_id + '.closure.xml'))
                self.docs[doc_id] = doc
                counter += 1
            except:
                print 'Something wrong when prepare document %(doc_id)s. Skip registering...' % {'doc_id': doc_id}
        print '%(counter)s document sets are registered' % {'counter': counter}
        
    def dump(self, pickled_file_path):
        for doc in self.docs.values():
            doc.prepare_to_pickle()
        try:
            with open(pickled_file_path, 'w') as fp:
                cPickle.dump(self, fp)
        except IOError:
            print 'Can not open file: ' + pickled_file_path
        except:
            print 'Something wrong when pickling the Dataset'
            raise
        
        
class DatasetItem(object):
    
    def __init__(self, ds_id):
        self.ds_id = ds_id


class Document(DatasetItem):
    '''
    classdocs
    '''

    def __init__(self, ds_id, i2b2_xml_path, ctakes_xml_path, parse_txt_path, closure_xml_path=None):
        '''
        Constructor
        '''
        super(Document, self).__init__(ds_id)
        if closure_xml_path:
            self.use_closure = True
        else:
            self.use_closure = False
        
        if not self.use_closure:
            print 'Preparing document %(i2b2)s, %(ctakes)s, %(parse)s' % \
                {'i2b2': os.path.basename(i2b2_xml_path),
                 'ctakes': os.path.basename(ctakes_xml_path),
                 'parse': os.path.basename(parse_txt_path)}
        else:
            print 'Preparing document %(i2b2)s, %(ctakes)s, %(parse)s, %(closure)s' % \
                {'i2b2': os.path.basename(i2b2_xml_path),
                 'ctakes': os.path.basename(ctakes_xml_path),
                 'parse': os.path.basename(parse_txt_path),
                 'closure': os.path.basename(closure_xml_path)}
            
        parser = etree.XMLParser(recover=True)
        
        try:
            self.i_elmt_tree = etree.parse(i2b2_xml_path, parser)
            self.i_root = self.i_elmt_tree.getroot()
        except:
            print 'Something wrong with opening/parsing specified i2b2 xml file'
            raise
        
        try:
            self.c_elmt_tree = etree.parse(ctakes_xml_path)
            self.c_root = self.c_elmt_tree.getroot()
        except:
            print 'Something wrong with opening/parsing specified ctakes xml file'
            raise

        try:
            self.p_fp = open(parse_txt_path, 'r')
        except:
            print 'Something wrong with opening specified parse txt file'
            raise
        
        if self.use_closure:
            try:
                self.cl_elmt_tree = etree.parse(closure_xml_path, parser)
                self.cl_root = self.cl_elmt_tree.getroot()
            except:
                print 'Something wrong with opening/parsing specified tlink closure xml file'
                raise
        
        self.tokens = []
        self.sents = []
        self.events = []
        self.timex3s = []
        self.sectimes = []
        self.entities = []
        self.tlinks_within_gold = []
        self.tlinks_between_gold = []
        self.tlinks_within_closure = []
        self.tlinks_between_closure = []
        
        self.admission_event = None
        self.admission_timex3 = None
        self.discharge_event = None
        self.discharge_timex3 = None
        #self.candids_within = []
        #self.candids_between = []
    
    
    def load_basics(self):
        self._load_sent_token()
        self._load_dependency()
        self._load_sent_section()

    def load_entities(self):
        self._load_event()
        self._load_timex3()
        self._load_sectime()
        self.entities = self.events + self.timex3s
        
    def load_tlinks(self):
        self._load_tlink()
        if self.use_closure:
            self._load_cls_tlink()
        #self.tlinks = self.tlinks_within + self.tlinks_between
    
    def _find_token_elmt_with_attrib_of_val(self, attrib, val):
        buf = []
        for token_type in ['WordToken', 'PunctuationToken', 'NumToken',
                           'SymbolToken', 'ContractionToken']:
            tag = CTAKES_PREFIX + 'syntax.' + token_type
            buf += self.c_root.xpath(tag + '[@' + attrib + '="%(val)s"]' % {'val': val})
        return buf
    
    def _find_begin_end_token(self, begin, end):
        begin_t = None
        end_t = None
        for t in self.tokens:
            if t.begin == begin:
                begin_t = t
                if end_t:
                    break
            if t.end == end:
                end_t = t
                if begin_t:
                    break
        return (begin_t, end_t)
    
    def _find_enty_with_origin_id(self, origin_id):
        for enty in self.entities:
            if enty.origin_id == origin_id:
                return enty
        return None
    
    def _find_enty_with_text(self, text, case_insensitive=False):
        if case_insensitive:
            for enty in self.entities:
                if enty.text.lower() == text.lower():
                    return enty
        else:
            for enty in self.entities:
                if enty.text == text:
                    return enty
        return None
    
    def _find_enty_with_begin_end(self, begin, end):
        for enty in self.entities:
            if enty.span[0].begin == begin and enty.span[-1].end == end:
                return enty
        return None
        
    def _load_sent_token(self):
        print "Loading sentences and tokens..."
        sent_elmts = self.c_root.findall(CTAKES_PREFIX + 'textspan.Sentence')
        t_counter = 0
        for sent_elmt in sent_elmts:
            sent_begin = int(sent_elmt.get('begin'))
            sent_end = int(sent_elmt.get('end'))
            sent_num = int(sent_elmt.get('sentenceNumber'))
            cursor = sent_begin
            sent_span = []
            token_offset = 0
            while cursor < sent_end:
                buf = self._find_token_elmt_with_attrib_of_val('begin', cursor)
                if len(buf) == 0:
                    cursor = cursor + 1
                    continue
                elif len(buf) > 1:
                    print 'More than one token appear to begin at ' + str(cursor) + \
                        '\nLoading ctakes xml file terminated'
                    return
                else:
                    token_elmt = buf[0]
                    t = Token(self.ds_id + '_t_' + str(t_counter))
                    t.type = token_elmt.tag.split('.')[-1][:-5]
                    # skipping 'newline' token when counting up tid
                    t_num = int(token_elmt.get('tokenNumber')) - sent_num
                    if t_num != t_counter:
                        print 'CAUTION: t_num does not equal to counter t_counter'
                    t.offset = token_offset
                    t.begin = int(token_elmt.get('begin'))
                    t.end = int(token_elmt.get('end'))
                    t.pos = token_elmt.get('partOfSpeech')
                    t.n_form = token_elmt.get('normalizedForm')
                    #t.c_form = token_elmt.get('canonicalForm')
                    #t.cap = int(token_elmt.get('capitalization'))
                    #t.num_p = int(token_elmt.get('numPosition'))
                    self.tokens.append(t)
                sent_span.append(t)
                cursor = t.end + 1
                token_offset = token_offset + 1
                t_counter += 1
                
            s = Sentence(self.ds_id + '_s_' + str(sent_num))
            s.span = sent_span
            s.num = sent_num
            #s.begin = sent_begin
            #s.end = sent_end
            s.parse = Tree.parse(self.p_fp.next())
            for t in s.span:
                t.sent = s
            self.sents.append(s)  
        return
    
    def _get_dependent(self, head):
        dn_elmts = self.c_root.xpath(CTAKES_PREFIX + \
                                     'syntax.ConllDependencyNode[@_ref_head="%(_id)s"]' \
                                     % {'_id': head.origin_id})
        if len(dn_elmts) == 0:
            return []
        else:
            dependent = []
            for dn_elmt in dn_elmts:
                token_found = False
                begin = int(dn_elmt.get('begin'))
                end = int(dn_elmt.get('end'))
                for t in self.tokens:
                    if t.begin != begin or t.end != end:
                        continue
                    else:
                        token_found = True
                        dn = DependencyNode()
                        dn.origin_id = dn_elmt.get('_id')
                        dn.deprel = dn_elmt.get('deprel')
                        dn.ref = t
                        t.dep_node = dn
                        t.form = dn_elmt.get('form')
                        t.lemma = dn_elmt.get('lemma')
                        dn.dependent = self._get_dependent(dn)
                        for d in dn.dependent:
                            d.head = dn
                        dependent.append(dn)
                if not token_found:
                    print 'No token could be found for dependency node\n' + \
                        'Dependency loading is terminated'
                    return
            return dependent
    
    def _load_dependency(self):
        '''
        Load the dependency node corresponding to sentence - node above the root
        '''
        print "Loading dependencies..."
        sent_dn_elmts = self.c_root.xpath(CTAKES_PREFIX + 'syntax.ConllDependencyNode[@id="0"]')
        for sent_dn_elmt in sent_dn_elmts:
            sent_found = False
            begin = int(sent_dn_elmt.get('begin'))
            end = int(sent_dn_elmt.get('end'))
            for s in self.sents:
                if s.span[0].begin != begin or s.span[-1].end != end:
                    continue
                else:
                    sent_found = True
                    dn = DependencyNode()
                    dn.origin_id = sent_dn_elmt.get('_id')
                    dn.ref = s
                    s.dep_node = dn
                    dn.dependent = self._get_dependent(dn)
                    for d in dn.dependent:
                        d.head = dn
            if not sent_found:
                print 'No sentence could be found for dependency node\n' + \
                      'Dependency loading is terminated'
                return
        return
    
    def _load_sent_section(self):
        sect0_start = re.compile('^h(istory|pi){1}(.)*:$', re.IGNORECASE)
        sect1_start = re.compile('^(brief |summary of )?hospital course(.)*:$', re.IGNORECASE)
        sect = -1
        for sent in self.sents:
            if sect == -1:
                rslt = sect0_start.search(str(sent))
                if rslt:
                    sect = 0
            if sect == 0:
                rslt = sect1_start.search(str(sent))
                if rslt:
                    sect = 1
            sent.sect = sect
        return
        
    '''
    def _load_chunk(self):
        print "Loading chunks..."
        chunk_elmts = self._find_chunk_elmt()
        cid = 0
        for chunk_elmt in chunk_elmts:
            begin  = int(chunk_elmt.get('begin'))
            end = int(chunk_elmt.get('end'))
            begin_t, end_t = self._find_begin_end_token(begin, end)
            if not begin_t or not end_t or begin_t.sid != end_t.sid:
                print 'Chunk loading: token could not be found or found in different sentence'
                return
            seq = self.tokens[begin_t.tid : end_t.tid + 1]
            c = Chunk(self.ds_id + '_c_' + str(cid), begin, end, begin_t, end_t, seq)
            c.c_type = chunk_elmt.get('chunkType')
            c.cid = cid
            
            self.sents[c.sid].chks.append(c)
            self.c_chunks.append(c)
            cid += 1
        return
    '''
    
    def _load_event(self):
        print "Loading events..."
        event_elmts = self.i_root.findall('TAGS/EVENT')
        e_counter = 0
        for event_elmt in event_elmts:
            begin = int(event_elmt.get('start')) - 1
            end = int(event_elmt.get('end')) - 1
            begin_t, end_t = self._find_begin_end_token(begin, end)
            if not begin_t or not end_t or begin_t.sent != end_t.sent:
                print 'Event loading: token could not be found or found in different sentence', begin + 1, end + 1
                continue
            sent = begin_t.sent
            e = i2b2Event(self.ds_id + '_e_' + str(e_counter))
            e.origin_id = event_elmt.get('id')
            e.span = sent.span[begin_t.offset : end_t.offset + 1]
            e.text = event_elmt.get('text')
            e.mod = event_elmt.get('modality')
            e.pol = event_elmt.get('polarity')
            e.type = event_elmt.get('type')
            e.sent = sent
            sent.events.append(e)
            self.events.append(e)
            e_counter += 1
            
            if 'admission date' in str(e.sent).lower():
                self.admission_event = e
                continue
            if 'discharge date' in str(e.sent).lower():
                self.discharge_event = e
        return
    
    def _load_timex3(self):
        print "Loading time expressions..."
        timex3_elmts = self.i_root.findall('TAGS/TIMEX3')
        tx_counter = 0
        for timex3_elmt in timex3_elmts:
            begin  = int(timex3_elmt.get('start')) - 1
            end = int(timex3_elmt.get('end')) - 1
            begin_t, end_t = self._find_begin_end_token(begin, end)
            if not begin_t or not end_t or begin_t.sent != end_t.sent:
                print 'TimeX3 loading: token could not be found or found in different sentence', begin + 1, end + 1
                continue
            sent = begin_t.sent
            tx = TimeX3(self.ds_id + '_tx_' + str(tx_counter))
            tx.origin_id = timex3_elmt.get('id')
            tx.span = sent.span[begin_t.offset : end_t.offset + 1]
            tx.text = timex3_elmt.get('text')
            tx.mod = timex3_elmt.get('mod')
            tx.value = timex3_elmt.get('val')
            tx.type = timex3_elmt.get('type')
            tx.sent = sent
            sent.timex3s.append(tx)
            self.timex3s.append(tx)
            tx_counter += 1
        return
    
    def _load_sectime(self):
        print "Loading section creation times..."
        sectime_elmts = self.i_root.findall('TAGS/SECTIME')
        st_counter = 0
        for sectime_elmt in sectime_elmts:
            begin  = int(sectime_elmt.get('start')) - 1
            end = int(sectime_elmt.get('end')) - 1
            begin_t, end_t = self._find_begin_end_token(begin, end)
            if not begin_t or not end_t or begin_t.sent != end_t.sent:
                print 'SecTime loading: token could not be found or found in different sentence', begin + 1, end + 1
                continue
            sent = begin_t.sent
            st = SecTime(self.ds_id + '_st_' + str(st_counter))
            st.origin_id = sectime_elmt.get('id')
            st.span = sent.span[begin_t.offset : end_t.offset + 1]
            st.text = sectime_elmt.get('text')
            st.value = sectime_elmt.get('dvalue')
            st.type = sectime_elmt.get('type')
            st.sent = sent
            sent.sectimes.append(st)
            self.sectimes.append(st)
            st_counter += 1
            
            #enty = self._find_enty_with_begin_end(st.span[0].begin, st.span[-1].end)
            for tx in self.timex3s:
                if tx.span == st.span:
                    tx.is_sectime = st.type
                    if st.type.lower() == 'admission':
                        self.admission_timex3 = tx
                    if st.type.lower() == 'discharge':
                        self.discharge_timex3 = tx
        return
    
    def _load_tlink(self):
        print "Loading ground truth TLinks..."
        tags = self.i_root.xpath('TAGS')[0]
        tlink_elmts = tags.xpath('TLINK[@type="BEFORE"]') + \
                    tags.xpath('TLINK[@type="AFTER"]') + \
                    tags.xpath('TLINK[@type="OVERLAP"]')
        tl_counter = 0
        for tlink_elmt in tlink_elmts:
            from_origin_id = tlink_elmt.get('fromID')
            to_origin_id = tlink_elmt.get('toID')
            link_type = tlink_elmt.get('type')
            from_enty = self._find_enty_with_origin_id(from_origin_id)
            to_enty = self._find_enty_with_origin_id(to_origin_id)
            if not from_enty or not to_enty:
                print 'TLink loading: entity can not be found'
                print from_enty, from_origin_id
                print to_enty, to_origin_id
                continue
            else:
                if from_enty.span[0].begin > to_enty.span[0].begin:
                    from_enty, to_enty = to_enty, from_enty
                    link_type = link_type if link_type == 'OVERLAP' else 'BEFOREAFTER'.replace(link_type, '')
                tl = search_tlink_between_enty(from_enty, to_enty, self.tlinks_within_gold + \
                                                                    self.tlinks_between_gold)
                if not tl:
                    tl = create_tlink_between_enty(self.ds_id + '_tl_' + str(tl_counter), from_enty, to_enty, link_type, 'gold')
                    tl.origin_id = tlink_elmt.get('id')
                    if tl.sent:
                        self.tlinks_within_gold.append(tl)
                    else:
                        self.tlinks_between_gold.append(tl)
                    tl_counter += 1
        return
    
    def _load_cls_tlink(self):
        print "Loading closure TLinks..."
        tlink_elmts = self.cl_root.xpath('TLINK[@relType="BEFORE"]') + \
                    self.cl_root.xpath('TLINK[@relType="AFTER"]') + \
                    self.cl_root.xpath('TLINK[@relType="SIMULTANEOUS"]')
                    # "before" and "after" are symetrical in closure data, so no need for
                    # self.cl_root.xpath('TLINK[@relType="AFTER"]')
        ctl_counter = 0
        for tlink_elmt in tlink_elmts:
            from_origin_id = tlink_elmt.get('fromEID')
            if not from_origin_id:
                from_origin_id = tlink_elmt.get('fromTID')
            to_origin_id = tlink_elmt.get('toEID')
            if not to_origin_id:
                to_origin_id = tlink_elmt.get('toTID')
            link_type = tlink_elmt.get('relType')
            from_enty = self._find_enty_with_origin_id(from_origin_id)
            '''
            # only used to handle special cases where fromID
            # equals to "Admission" or "Discharge", instead of a valid id, such as "E0"
            if not from_enty:
                if from_origin_id in ['Admission', 'Discharge']:
                    from_text = from_origin_id
                    from_enty = self._find_enty_with_text(from_text, True)
            '''
            to_enty = self._find_enty_with_origin_id(to_origin_id)
            '''
            # only used to handle special cases where toID
            # equals to "Admission" or "Discharge", instead of a valid id, such as "E1"
            if not to_enty:
                if to_origin_id in ['Admission', 'Discharge']:
                    to_text = to_origin_id
                    to_enty = self._find_enty_with_text(to_text, True)
            '''
            if not from_enty or not to_enty:
                print 'Closure TLink loading: entity can not be found'
                print from_enty, from_origin_id
                print to_enty, to_origin_id
                continue
            else:
                if from_enty.span[0].begin > to_enty.span[0].begin:
                    from_enty, to_enty = to_enty, from_enty
                    link_type = link_type if link_type == 'SIMULTANEOUS' else 'BEFOREAFTER'.replace(link_type, '')
                tl = search_tlink_between_enty(from_enty, to_enty, self.tlinks_within_gold + \
                                                                    self.tlinks_between_gold + \
                                                                    self.tlinks_within_closure + \
                                                                    self.tlinks_between_closure)
                if not tl:
                    tl = create_tlink_between_enty(self.ds_id + '_ctl_' + str(ctl_counter), from_enty, to_enty, src='closure')
                    tl.type = 'OVERLAP' if link_type == 'SIMULTANEOUS' else link_type
                    if tl.sent:
                        self.tlinks_within_closure.append(tl)
                    else:
                        self.tlinks_between_closure.append(tl)
                    '''
                    tl = TLink(self.ds_id + '_ctl_' + str(ctl_counter))
                    tl.from_enty = from_enty
                    tl.to_enty = to_enty
                    tl.type = 'OVERLAP' if link_type == 'SIMULTANEOUS' else link_type
                    tl.sig = tl.from_enty.sig + '_' + tl.to_enty.sig
                    if tl.from_enty.sent == tl.to_enty.sent:
                        tl.sent = tl.from_enty.sent
                        tl.sent_dis = 0
                        tl.sent.tlinks_within.append(tl)
                        self.tlinks_within.append(tl)
                    else:
                        #tl.sent = (tl.from_enty.sent, tl.to_enty.sent)
                        tl.sent_dis = tl.to_enty.sent.num - tl.from_enty.sent.num
                        #tl.from_enty.sent.tlinks_between.append(tl)
                        #tl.to_enty.sent.tlinks_between.append(tl)
                        self.tlinks_between.append(tl)
                    tl.src = 'closure'
                    '''
                    ctl_counter += 1
        return
    
    def prepare_to_pickle(self):
        self.c_elmt_tree = None
        self.c_root = None
        self.i_elmt_tree = None
        self.i_root = None
        self.cl_elmt_tree = None
        self.cl_root = None
        self.p_fp = None
        
        
class Token(DatasetItem):
    
    def __init__(self, ds_id):
        super(Token, self).__init__(ds_id)
        self.origin_id = None
        self.type = None
        self.offset = None
        self.sent = None
        self.begin = None
        self.end = None
        self.pos = None
        self.form = None
        self.n_form = None
        self.lemma = None
        self.dep_node = None
    
    def __str__(self):
        return self.form
    
    def __repr__(self):
        return self.form
    
    
class Phrase(DatasetItem):
    
    def __init__(self, ds_id):
        super(Phrase, self).__init__(ds_id)
        self.span = []
        self.head = None
        
    def __str__(self):
        return ' '.join([str(t) for t in self.span])
        
        
class Sentence(DatasetItem):
    
    def __init__(self, ds_id):
        super(Sentence, self).__init__(ds_id)
        self.origin_id = None
        self.span = []
        self.num = None
        self.sect = None
        self.dep_node = None
        self.events = []
        self.timex3s = []
        self.sectimes = []
        self.tlinks_within = []
        #self.candids_within = []
        self.parse = None
        
    def __str__(self):
        return ' '.join([str(t) for t in self.span])
    
    def __repr__(self):
        return 'Sentence_obj'
    
    
class DependencyNode(object):
    '''
    DependencyNode doesn't use DataSetObject as base class
    It's one-to-one mapped to sentence or token
    The purpose of DependencyNode is to capture "dependency relationship", not an "entity"
    '''
    def __init__(self):
        self.origin_id = None
        self.ref = None
        self.head = None
        self.dependent = []
        self.deprel = None
    
    def __str__(self):
        return str(self.ref)
    
    def __repr__(self):
        return repr(self.ref)
    
    
class DependencyPath(object):
    '''
    A representation of the dependency path between two dependency nodes
    CAUTION: two nodes have to be in the same sentence to have a dependency path
    '''
    
    def __init__(self, from_path, to_path):
        self.from_path = from_path
        self.to_path = to_path
    
    def __str__(self):
        from_p = []
        for dn in self.from_path:
            from_p.append(dn)
            if hasattr(dn, 'deprel'):
                from_p.append('<' + dn.deprel + '>')
            else:
                from_p.append('<>')
        to_p = []
        for dn in self.to_path:
            to_p.append(dn)
            if hasattr(dn, 'deprel'):
                to_p.append('<' + dn.deprel + '>')
            else:
                from_p.append('<>')
        return str(from_p[:-1]) + '\n' + str(to_p[:-1])
    
    def __repr__(self):
        return self.__str__()
        
        
class i2b2Event(Phrase):
    
    def __init__(self, ds_id):
        super(i2b2Event, self).__init__(ds_id)
        self.origin_id = None
        self.sig = 'Event'
        self.text = None
        self.mod = None
        self.pol = None
        self.type = None
        self.sent = None
        
    def __str__(self):
        return self.text
        
        
class TimeX3(Phrase):
    
    def __init__(self, ds_id):
        super(TimeX3, self).__init__(ds_id)
        self.origin_id = None
        self.sig = 'TimeX3'
        self.text = None
        self.mod = None
        self.value = None
        self.type = None
        self.is_sectime = False
        self.sent = None
        
    def __str__(self):
        return self.text
        
        
class SecTime(Phrase):
    
    def __init__(self, ds_id):
        super(SecTime, self).__init__(ds_id)
        self.origin_id = None
        self.sig = 'SecTime'
        self.text = None
        self.value = None
        self.type = None
        self.sent = None
        
    def __str__(self):
        return self.text
    
        
class TLink(DatasetItem):
    
    def __init__(self, ds_id):
        super(TLink, self).__init__(ds_id)
        self.origin_id = None
        self.from_enty = None
        self.to_enty = None
        self.type = None
        self.sig = None
        self.sent_dis = None
        self.sent = None
        self.src = None
        #self.flip = False
        #self.dep_path = None
        #self.left = []
        #self.mid = []
        #self.right = []
        
        
    def __str__(self):
        return str(self.from_enty) + '(' + self.from_enty.type + ')' + ' ' + \
            self.type + ' ' + \
            str(self.to_enty) + '(' + self.to_enty.type + ')'

        
def display_tlink(tl):
    if tl is None:
        return str(tl)
    print_str = ''
    if tl.sent:
        begin_offsets = [tl.from_enty.span[0].offset,
                         tl.to_enty.span[0].offset]
        end_offsets = [tl.from_enty.span[-1].offset,
                       tl.to_enty.span[-1].offset]
        t_str_list = [str(t) for t in tl.sent.span]
        for offset in begin_offsets:
            t_str_list[offset] = '[' + t_str_list[offset]
        for offset in end_offsets:
            t_str_list[offset] = t_str_list[offset] + ']'
        print_str = ' '.join(t_str_list)
    else:
        t_str_list = [str(t) for t in tl.from_enty.sent.span]
        t_str_list[tl.from_enty.span[0].offset] = '[' + t_str_list[tl.from_enty.span[0].offset]
        t_str_list[tl.from_enty.span[-1].offset] = t_str_list[tl.from_enty.span[-1].offset] + ']'
        print_str = ' '.join(t_str_list)
        t_str_list = [str(t) for t in tl.to_enty.sent.span]
        t_str_list[tl.to_enty.span[0].offset] = '[' + t_str_list[tl.to_enty.span[0].offset]
        t_str_list[tl.to_enty.span[-1].offset] = t_str_list[tl.to_enty.span[-1].offset] + ']'
        print_str = print_str + '\n' + ' '.join(t_str_list)
    print_str = print_str + '\n' + str(tl)
    return print_str
    

def search_tlink_between_enty(from_enty, to_enty, tls):
    for tl in tls:
        if tl.from_enty == from_enty and tl.to_enty == to_enty:
            return tl
    return None


def create_tlink_between_enty(candid_id, from_enty, to_enty, link_type='UNKNOWN', src='UNKNOW'):
    tl = TLink(candid_id)
    tl.from_enty = from_enty
    tl.to_enty = to_enty
    tl.type = link_type
    tl.sig = tl.from_enty.sig + '_' + tl.to_enty.sig
    if from_enty.sent == to_enty.sent:
        tl.sent = from_enty.sent
        tl.sent_dis = 0
    else:
        tl.sent_dis = to_enty.sent.num - from_enty.sent.num
    tl.src = src
    return tl


def get_phrase_head(ph):
    '''
    Assumption: based on ctakes' dependency information, a span of tokens 
                should have one (and only one) token as the "head" of the span
    If assumption holds, return the head token; otherwise, return right-most token
    '''
    try:
        span = ph.span
    except TypeError:
        print 'Has to have "span" to have a head'
        return
    if len(span) == 1:
        #print 'Head found'
        return span[0]
    dn_span = [t.dep_node for t in span]
    head = []
    for dn in dn_span:
        if dn.head not in dn_span:
            head.append(dn)
    if len(head) == 1:
        #print 'Head found'
        return head[0].ref
    else:
        #print 'Multiple or Zero head sequence: ' + str(ph)
        #print 'Defaulting to right most token: ' + str(span[-1])
        return span[-1]
    
    
def get_tlink_context(tl):
    if not tl.sent:
        print 'TLink context only make sense for within sentence TLink'
        return
    left = tl.sent.span[:tl.from_enty.span[0].offset]
    if tl.from_enty.span[-1].offset + 1 < tl.to_enty.span[0].offset:
        mid = tl.sent.span[tl.from_enty.span[-1].offset + 1 : tl.to_enty.span[0].offset]
    else:
        mid = []
    right = tl.sent.span[tl.to_enty.span[-1].offset + 1:]
    return [left, mid, right]


def get_tlink_dep_path(tl):
    if not tl.sent:
        print 'TLink between sentences do not have a dependency path'
        return
    from_head = get_phrase_head(tl.from_enty)
    to_head = get_phrase_head(tl.to_enty)
    if from_head == to_head:
        #print 'Same head for both entities. No dependency path in between'
        #return
        return DependencyPath([from_head.dep_node], [to_head.dep_node])
    from_path = []
    nxt = from_head.dep_node
    while nxt:
        from_path.append(nxt)
        nxt = nxt.head
    to_path = []
    nxt = to_head.dep_node
    while nxt:
        to_path.append(nxt)
        nxt = nxt.head
    empty = from_path == [] or to_path == []
    # presumbly, empty will always be False here, since both path will at least contain the sentence node
    while not empty:
        try:
            if from_path[-1] == to_path[-1]:
                last = from_path.pop(-1)
                del to_path[-1]
            else:
                break
        except IndexError:
            empty = True
    # if empty == True, one path is popped-out, it means the corresponding head is the "head" of the other head
    from_path.append(last)
    to_path.append(last)
    return DependencyPath(from_path, to_path)

    
def main():
    from project_path import project_base, data_pre_1
    
    data_pre = data_pre_1

    try:
        with open(os.path.join(project_base, data_pre + '_dmp'), 'r') as fp:
            print 'un-pickling...'
            ds = cPickle.load(fp)
            from ie.relation import get_path_enclosed_tree
            for doc in ds.docs.values():
                for tl in doc.tlinks_within_gold + doc.tlinks_within_closure:
                    tl.pet = get_path_enclosed_tree(tl.from_enty.span[0].offset, tl.to_enty.span[-1].offset, tl.sent.parse)
            return ds
    except IOError:
        sys.stdout = open(os.path.join(project_base, data_pre + '_loading_log'), 'w')

        ds = Dataset(os.path.join(project_base, data_pre) + '_i',
                     os.path.join(project_base, data_pre) + '_c',
                     os.path.join(project_base, data_pre) + '_p',
                     os.path.join(project_base, data_pre) + '_cls')

        print 'loading...'
        for item in ds.docs.items():
            print item[0]
            doc = item[1]
            doc.load_basics()
            doc.load_entities()
            doc.load_tlinks()
        ds.dump(os.path.join(project_base, data_pre + '_dmp'))

if __name__ == '__main__':
    main()
            