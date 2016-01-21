'''
Created on Jan 23, 2013

@author: yaocheng
'''

import os
import sys
import cPickle

from data import Dataset, Document, Sentence, Token, i2b2Event, TimeX3, SecTime, TLink, DependencyNode
from tlink_candidate import create_candid_within3, update_candid_id
from tlink_feature import positional_feats, contextual_feats, dependency_feats, tense_feats, other_feats
from mallet import Config
from mallet_ML import train_on_data, apply_to_data
from tlink_conflict import get_conflict_info2, verify, get_kth_large_key, accepted_state, unknown_state
from project_path import project_base, mallet_bin, project_temp, data_pre_1, data_pre_2

#within_tlink_feats = positional_feats + contextual_feats + dependency_feats + tense_feats + other_feats
within_tlink_feats = contextual_feats + dependency_feats + tense_feats + other_feats

def main():
    data_pre = data_pre_1
    try:
        with open(os.path.join(project_base, data_pre + '_dmp'), 'r') as fp:
            print 'un-pickling...'
            ds = cPickle.load(fp)
    except IOError:
        print 'something wrong with the pickle file path'
        
    within_tls = []
    for doc in ds.docs.values():
        within_tls.extend(doc.tlinks_within_gold)
        within_tls.extend(doc.tlinks_within_closure)
    cfg = Config(mallet_bin, project_temp, data_pre + '_within')
    train_cfg = train_on_data(within_tls, lambda x: x.ds_id, lambda x: x.type, within_tlink_feats, 'MaxEnt', cfg)
    
    data_pre = data_pre_2
    try:
        with open(os.path.join(project_base, data_pre + '_dmp'), 'r') as fp:
            print 'un-pickling...'
            ds = cPickle.load(fp)
    except IOError:
        print 'something wrong with the pickle file path'
        
    all_a = []
    all_c = []
    all_u = []
    all_i = []
    
    all_m = []
    all_um = []
    all_uw = []
    all_mi = []
    
    all_within = []
    all_candid = []
    
    for doc in ds.docs.values():
        within = doc.tlinks_within_gold + doc.tlinks_within_closure
        for tl in within:
            tl.sent.tlinks_within.append(tl)
        all_within.extend(within)
        candid = create_candid_within3(doc)
        update_candid_id(candid, doc.ds_id)
        all_candid.extend(candid)
        cfg = Config(mallet_bin, project_temp, data_pre + '_within_' + doc.ds_id)
        ti = apply_to_data(candid, lambda x: x.ds_id, within_tlink_feats, train_cfg.model_path, cfg)
        
        for c in candid:
            c.pred = ti.ID2pred[c.ds_id]
            c.probs = ti.ID2probs[c.ds_id]
            
        #for s in doc.sents:
        #    expand(s)
        
        for s in doc.sents:
            #print s.ds_id
            '''
            if s.freq_tx != []:
                print 'freq_tx:', s.freq_tx
            for tl in s.freq_tl:
                tl.pred = 'OVERLAP'
            tx3s_copy = s.timex3s[:]
            for tx in s.freq_tx:
                tx3s_copy.remove(tx)
            a, c, u, i = get_conflict_info2(s.events + tx3s_copy, s.candids_within, lambda x: x.span[0].begin, lambda x: x.pred)
            '''
            a, c, u, i = get_conflict_info2(s.events + s.timex3s, s.candids_within, lambda x: x.span[0].begin, lambda x: x.pred)
            all_a.extend(a)
            all_c.extend(c)
            all_u.extend(u)
            all_i.extend(i)
            
        print 'document:', doc.ds_id, '\n'
        for s in doc.sents:
            #print s.ds_id
            #m, um, uw, mi = verify(s.candids_within + s.freq_tl, s.tlinks_within)
            m, um, uw, mi = verify(s.candids_within, s.tlinks_within)
            all_m.extend(m)
            all_um.extend(um)
            all_uw.extend(uw)
            all_mi.extend(mi)
            
            '''
            resolve_conflict_within2(s)
            print 'after resolution:', doc.ds_id, '\n'
            
            rslt = verify(s.candids_within, s.tlinks_within)
            print s.ds_id, rslt, '\n'
            pair1 = [x + y for (x, y) in zip(pair1, rslt[0])]
            label1 = [x + y for (x, y) in zip(label1, rslt[1])]
            '''
            
    all_rslt = [all_a, all_c, all_u, all_i, all_m, all_um, all_uw, all_mi, all_within, all_candid]
    
    try:
        with open(os.path.join(project_base, data_pre_2 + '_within_result_dmp'), 'w') as fp:
            cPickle.dump(all_rslt, fp)
    except:
        print 'something wrong when dumping'
            
def main2():
    try:
        with open(os.path.join(project_base,  data_pre_2 + '_within_result_dmp'), 'r') as fp:
            all_rslt = cPickle.load(fp)
    except:
        print 'something wrong when loading'
        
    sys.stdout = open(os.path.join(project_base, data_pre_1 + '_' + data_pre_2 + '_within_log'), 'w')
    
    all_a, all_c, all_u, all_i, all_m, all_um, all_uw, all_mi, all_within, all_candid = all_rslt
    print len(all_a), len(all_c), len(all_u), len(all_i)
    
    print ''
    
    #print 'matched'
    #for c in all_m:
        #print c.probs[c.pred]
    #print 'unmatched'
    #for c in all_um:
    #    second = get_kth_large_key(c.probs, 2)
    #    print c.probs[second]
    
    c0, c1, c2, c3 = get_tri_w_tls(all_c, all_um)
    #print len(c0), len(c1), len(c2), len(c3)
    print len(c0)
    a0, a1, a2, a3 = get_tri_w_tls(c0, all_m)
    print len(a0), len(a1), len(a2), len(a3)
    print len(c1)
    a0, a1, a2, a3 = get_tri_w_tls(c1, all_m)
    print len(a0), len(a1), len(a2), len(a3)
    print len(c2)
    a0, a1, a2, a3 = get_tri_w_tls(c2, all_m)
    print len(a0), len(a1), len(a2), len(a3)
    print len(c3)
    a0, a1, a2, a3 = get_tri_w_tls(c3, all_m)
    print len(a0), len(a1), len(a2), len(a3)
    
    print ''
    
    print len(get_uniq_tl_from_tri(all_c, all_um))
    
    print ''
    
    a0, a1, a2, a3 = get_tri_w_tls(all_a, all_um)
    print len(a0), len(a1), len(a2), len(a3)
    
    print ''
    
    print len(get_uniq_tl_from_tri(all_a, all_um))
    
    print ''
    
    a0, a1, a2, a3 = get_tri_w_tls(all_u, all_um)
    print len(a0), len(a1), len(a2), len(a3)
    
    print ''
    
    print len(get_uniq_tl_from_tri(all_u, all_um))
    
    print ''
    
    print len(all_m), len(all_um), len(all_uw), len(all_mi)
    
    p34, p45, p56, p67, p78, p89, p90 = get_pred_prob_bin(all_m)
    print [len(b) for b in [p34, p45, p56, p67, p78, p89, p90]]
    
    p34, p45, p56, p67, p78, p89, p90 = get_pred_prob_bin(all_um)
    print [len(b) for b in [p34, p45, p56, p67, p78, p89, p90]]
    
    p34, p45, p56, p67, p78, p89, p90 = get_pred_prob_bin(all_uw)
    print [len(b) for b in [p34, p45, p56, p67, p78, p89, p90]]
    
    for tl in get_uniq_tl_from_tri(all_c):
        tl.votes = {'BEFORE': 0, 'OVERLAP':0, 'AFTER':0}
        tl.vote_probs = {'BEFORE': 0, 'OVERLAP':0, 'AFTER':0}
        tl.change = 0
        tl.keep = 0
    change = []
    mic = []
    umic = []
    uwic = []
    accepted_state.extend(unknown_state)
    for tpl in all_c:
        t1 = tpl[0]
        t2 = tpl[1]
        t3 = tpl[2]
        p1 = t1.probs[t1.pred]
        p2 = t2.probs[t2.pred]
        p3 = t3.probs[t3.pred]
        d3 = t1.probs[t1.pred] * t2.probs[t2.pred] - t3.probs[t3.pred]
        d1 = t2.probs[t2.pred] * t3.probs[t3.pred] - t1.probs[t1.pred]  
        d2 = t3.probs[t3.pred] * t1.probs[t1.pred] - t2.probs[t2.pred]
        
        mx = max(d1, d2, d3)
        #if mx > 0.21:
        if mx == d1:
            #ch = t1
            #i = [tpl[1:3] for tpl in accepted_state].index((t2.pred, t3.pred))
            #ch.res = accepted_state[i][0]
            if p1 < 0.6:
                t1.change += 1
            else:
                t1.keep += 1
            t2.keep += 1
            t3.keep += 1
        if mx == d2:
            #ch = t2
            #i = [tpl[::2] for tpl in accepted_state].index((t1.pred, t3.pred))
            #ch.res = accepted_state[i][1]
            if p2 < 0.6:
                t2.change += 1
            else:
                t2.keep += 1
            t3.keep += 1
            t1.keep += 1
        if mx == d3:
            #ch = t3
            #i = [tpl[0:2] for tpl in accepted_state].index((t1.pred, t2.pred))
            #ch.res = accepted_state[i][2]
            if p3 < 0.6:
                t3.change += 1
            else:
                t3.keep += 1
            t1.keep += 1
            t2.keep += 1
        #ch.res = get_kth_large_key(ch.probs, 2)
        #change.append(ch)
    for tl in get_uniq_tl_from_tri(all_c):
        if tl.change > tl.keep:
            tl.res = get_kth_large_key(tl.probs, 2)
            change.append(tl)
        '''
        if max(d1, d2, d3) == d2 and d2 > 0:
            #i = [tpl[::2] for tpl in accepted_state].index((t1.pred, t3.pred))
            #t2.res = accepted_state[i][1]
            if t2 in all_m:
                mic.append(t2)
            if t2 in all_um:
                umic.append(t2)
            if t2 in all_uw:
                uwic.append(t2)
            t2.res = get_kth_large_key(t2.probs, 2)
            change.append(t2)
            continue
        if max(d1, d2, d3) == d3 and d3 > 0:
            #i = [tpl[0:2] for tpl in accepted_state].index((t1.pred, t2.pred))
            #t3.res = accepted_state[i][2]
            if t3 in all_m:
                mic.append(t3)
            if t3 in all_um:
                umic.append(t3)
            if t3 in all_uw:
                uwic.append(t3)
            t3.res = get_kth_large_key(t3.probs, 2)
            change.append(t3)
        
        if min(p1, p2, p3) == p1:
            t1.res = get_kth_large_key(t1.probs, 2)
            change.append(t1)
            continue
        if min(p1, p2, p3) == p2:
            t2.res = get_kth_large_key(t2.probs, 2)
            change.append(t2)
            continue
        if min(p1, p2, p3) == p3:
            t3.res = get_kth_large_key(t3.probs, 2)
            change.append(t3)
        '''
    for tl in change:
        tl.pred = tl.res
        if tl in all_m:
            mic.append(tl)
        if tl in all_um:
            umic.append(tl)
        if tl in all_uw:
            uwic.append(tl)
            
    print len(change), len(mic), len(umic), len(uwic)
    print len(set(change)), len(set(mic)), len(set(umic)), len(set(uwic))
            
    m, um, uw, mi = verify(all_candid, all_within)
    print len(m), len(um), len(uw), len(mi)
    
    
def get_uniq_tl_from_tri(tris, tls=None):
    uniq = set()
    for tri in tris:
        uniq.update(tri)
    if not tls:
        buf = list(uniq)
    else:
        buf = []
        for tl in uniq:
            if tl in tls:
                buf.append(tl)
    return buf

def get_tri_w_tls(tris, tls):
    c0 = []
    c1 = []
    c2 = []
    c3 = []
    for tpl in tris:
        num = 0
        for tl in tpl:
            if tl in tls:
                num += 1
        if num == 0:
            c0.append(tpl)
        if num == 1:
            c1.append(tpl)
        if num == 2:
            c2.append(tpl)
        if num == 3:
            c3.append(tpl)
    return c0, c1, c2, c3
    
def get_pred_prob_bin(tls):
    p34 = []
    p45 = []
    p56 = []
    p67 = []
    p78 = []
    p89 = []
    p90 = []
    for tl in tls:
        if tl.probs[tl.pred] >= 0.3 and tl.probs[tl.pred] < 0.4:
            p34.append(tl)
        if tl.probs[tl.pred] >= 0.4 and tl.probs[tl.pred] < 0.5:
            p45.append(tl)
        if tl.probs[tl.pred] >= 0.5 and tl.probs[tl.pred] < 0.6:
            p56.append(tl)
        if tl.probs[tl.pred] >= 0.6 and tl.probs[tl.pred] < 0.7:
            p67.append(tl)
        if tl.probs[tl.pred] >= 0.7 and tl.probs[tl.pred] < 0.8:
            p78.append(tl)
        if tl.probs[tl.pred] >= 0.8 and tl.probs[tl.pred] < 0.9:
            p89.append(tl)
        if tl.probs[tl.pred] >= 0.9 and tl.probs[tl.pred] < 1.0:
            p90.append(tl)
    return p34, p45, p56, p67, p78, p89, p90
                
        
if __name__ == '__main__':
    main2() 