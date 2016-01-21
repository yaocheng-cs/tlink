'''
Created on Jan 15, 2013

@author: yaocheng
'''

from itertools import combinations, product

from data import display_tlink, search_tlink_between_enty, create_tlink_between_enty, get_phrase_head
from conflict import get_kth_large_key

def create_candid_within(doc):
    candids = []
    for s in doc.sents:
        s.candids_within = []
        # generate within sentence candidate
        sorted_entits = sorted(s.events + s.timex3s, key=lambda x: x.span[0].begin)
        for pair in combinations(sorted_entits, 2):
            tl = create_tlink_between_enty('dummy_id', pair[0], pair[1], src='candid')
            s.candids_within.append(tl)
            candids.append(tl)
        #for i in range(len(sorted_entits) - 1):
        #    tl = create_tlink_between_enty('dummy_id', sorted_entits[i], sorted_entits[i + 1], src='candid')
        #    candid.append(tl)
    return candids

def create_candid_within2(doc):
    candids = []
    for s in doc.sents:
        s.candids_within = []
        # generate within sentence candidate
        sorted_entits = sorted(s.events + s.timex3s, key=lambda x: x.span[0].begin)
        for i in range(len(sorted_entits) - 1):
            tl = create_tlink_between_enty('dummy_id', sorted_entits[i], sorted_entits[i + 1], src='candid')
            s.candids_within.append(tl)
            candids.append(tl)
        #for i in range(len(sorted_entits) - 1):
        #    tl = create_tlink_between_enty('dummy_id', sorted_entits[i], sorted_entits[i + 1], src='candid')
        #    candid.append(tl)
    return candids

def create_candid_within3(doc):
    candids = []
    for s in doc.sents:
        s.candids_within = []
        sorted_entits = sorted(s.events + s.timex3s, key=lambda x: x.span[0].begin)
        '''
        s.freq_tl = []
        s.freq_tx = []
        for tx in sorted(s.timex3s, key=lambda x: x.span[0].begin):
            if tx.type == 'FREQUENCY':
                s.freq_tx.append(tx)
        for tx in s.freq_tx:
            i = sorted_entits.index(tx)
            for d in range(1, len(sorted_entits)):
                if i - d >= 0:
                    e = sorted_entits[i - d]
                    if e.sig == 'Event':
                        tl = create_tlink_between_enty('dummy_id', e, tx, src='candid')
                        s.freq_tl.append(tl)
                        #s.candids_within.append(tl)
                        #candids.append(tl)
            sorted_entits.remove(tx)
        '''
        # generate within sentence candidate
        for pair in combinations(sorted_entits, 2):
            tl = create_tlink_between_enty('dummy_id', pair[0], pair[1], src='candid')
            s.candids_within.append(tl)
            candids.append(tl)
    return candids

def create_candid_duration2date(doc):
    """
    if a TimeX3 in the sentence is of type "duration", try to link it to a nearby type "date" TimeX3
    if there is already another "date" in the same sentence, then skip this step
    """
    candid = []
    for s in doc.sents:
        date = [tx for tx in s.timex3s if tx.type == 'DATE']
        duration = [tx for tx in s.timex3s if tx.type == 'DURATION']
        if not len(date) == 0 and len(duration) > 0:
            print len(duration), 'duraion in sentence'
            for i in range(1, 8):
                pre_sent_num = s.num - i
                if pre_sent_num >= 0:
                    d = [tx for tx in doc.sents[pre_sent_num].timex3s if tx.type == 'DATE']
                    if d != []:
                        for tx in duration:
                            tl = create_tlink_between_enty('dummy_id', d[0], tx, src='candid')
                            candid.append(tl)
                        break
                post_sent_num = s.num + i
                if post_sent_num < len(doc.sents):
                    d = [tx for tx in doc.sents[post_sent_num].timex3s if tx.type == 'DATE']
                    if d != []:
                        for tx in duration:
                            tl = create_tlink_between_enty('dummy_id', tx, d[0], src='candid')
                            candid.append(tl)
                        break
    return candid

def enumerate_possible_between(doc):
    sent_src = doc.sents[:]
    for i in [doc.admission_event, doc.admission_timex3,
              doc.discharge_event, doc.discharge_timex3]:
        if i:
            sent_src.remove(i.sent)               
    ptls = []
    ptl_counter = 0
    for i in range(len(sent_src) - 1):
        fs = sent_src[i]
        fs_entits = fs.events + fs.timex3s
        for ts in sent_src[i + 1:]:
            ts_entits = ts.events + ts.timex3s
            for pair in product(fs_entits, ts_entits):
                tl = create_tlink_between_enty(doc.ds_id + '_ptl_' + str(ptl_counter), pair[0], pair[1])
                ptls.append(tl)
                ptl_counter += 1
    return ptls

def create_candid_event2sectime(doc):
    event_src = doc.events[:]
    if doc.admission_event:
        event_src.remove(doc.admission_event)
    if doc.discharge_event:
        event_src.remove(doc.discharge_event)
    candid = []
    for e in event_src:
        if e.sent.sect == 0:
            if doc.admission_timex3:
                tl = create_tlink_between_enty('dummy_id', doc.admission_timex3, e, src='candid') 
            else:
                tl = create_tlink_between_enty('dummy_id', doc.admission_event, e, src='candid')
            if e.text.lower() == 'admission':
                tl.pred = 'OVERLAP'
            else:
                tl.pred = 'AFTER'
            candid.append(tl)
        if e.sent.sect == 1:
            if doc.discharge_timex3:
                tl = create_tlink_between_enty('dummy_id', doc.discharge_timex3, e, src='candid')
            else:
                tl = create_tlink_between_enty('dummy_id', doc.discharge_event, e, src='candid')
            if 'discharge' in e.text.lower():
                tl.pred = 'OVERLAP'
            else:
                tl.pred = 'AFTER'
            candid.append(tl)
    if doc.admission_event and doc.admission_timex3:
        tl = create_tlink_between_enty('dummy_id', doc.admission_event, doc.admission_timex3, src='candid')
        tl.pred = 'OVERLAP'
        candid.append(tl)
    if doc.discharge_event and doc.discharge_timex3:
        tl = create_tlink_between_enty('dummy_id', doc.discharge_event, doc.discharge_timex3, src='candid')
        tl.pred = 'OVERLAP'
        candid.append(tl)
    return candid

def create_candid_coref(doc):
    sent_src = doc.sents[:]
    candid = []
    for i in range(len(sent_src) - 1):
        fs = sent_src[i]
        fs_entits = fs.events
        for ts in sent_src[i + 1:]:
            ts_entits = ts.events
            for pair in product(fs_entits, ts_entits):
                if get_phrase_head(pair[0]).lemma == get_phrase_head(pair[1]).lemma:
                    tl = create_tlink_between_enty('dummy_id', pair[0], pair[1])
                    tl.pred = 'OVERLAP'
                    candid.append(tl)
    return candid

def update_candid_id(candids, doc_id, starting_counter=0):
    cdtl_counter = starting_counter
    for c in candids:
        c.ds_id = doc_id + '_cdtl_' + str(cdtl_counter)
        cdtl_counter += 1
    return cdtl_counter
