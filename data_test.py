'''
Created on Jan 18, 2013

@author: yaocheng
'''

import os
import sys
import cPickle

from data import Dataset, Document, Sentence, Token, i2b2Event, TimeX3, SecTime, TLink, DependencyNode
from data import display_tlink
from conflict import get_conflict_info2, get_kth_large_key
from project_path import project_base, data_pre_1, data_pre_2

def test():
    data_pre = data_pre_2
    
    try:
        with open(os.path.join(project_base, data_pre + '_dmp'), 'r') as fp:
            print 'un-pickling...'
            ds = cPickle.load(fp)
    except IOError:
        print 'something wrong with the pickle file path'
        
    
    sys.stdout = open(os.path.join(project_base, data_pre + '_stat'), 'w')
    
    num_s = 0
    num_e = 0
    num_tx = 0
    num_st = 0
    num_within_gold = 0
    num_between_gold = 0
    num_within_cls = 0
    num_between_cls = 0
    max_num_enty = 0
    num_accepted = 0
    num_conflict = 0
    num_unknown = 0
    num_incomplete = 0
    
    for d in ds.docs.values():
        print 'document: ' + d.ds_id
        num_s += len(d.sents)
        num_e += len(d.events)
        num_tx += len(d.timex3s)
        num_st += len(d.sectimes)
        num_within_gold += len(d.tlinks_within_gold)
        num_between_gold += len(d.tlinks_between_gold)
        num_within_cls += len(d.tlinks_within_closure)
        num_between_cls += len(d.tlinks_between_closure)
        print '\t'.join([str(i) for i in [len(d.tokens), len(d.sents), 
                                          len(d.events), len(d.timex3s), len(d.sectimes), 
                                          len(d.tlinks_within_gold), len(d.tlinks_between_gold), 
                                          len(d.tlinks_within_closure), len(d.tlinks_between_closure)]])
        for tl in d.tlinks_within_gold + d.tlinks_within_closure:
            #try:
            #    tl.sent.tls.append(tl)
            #except AttributeError:
            #    tl.sent.tls = [tl]
            tl.sent.tlinks_within.append(tl)
        for s in d.sents:
            if len(s.events) + len(s.timex3s) > max_num_enty:
                max_num_enty = len(s.events) + len(s.timex3s)
            a, c, u, i = get_conflict_info2(s.events + s.timex3s, s.tlinks_within, lambda x: x.span[0].begin, lambda x: x.type)
            print 'num of circle:', len(a) + len(c) + len(u) + len(i)
            num_accepted += len(a)
            num_conflict += len(c)
            num_unknown += len(u)
            num_incomplete += len(i)
            
            for tpl in i:
                sent_printed = False
                for tl in tpl:
                    if tl:
                        print tl.sent
                        sent_printed = True
                        break
                if not sent_printed:
                    print 'no tlink in this incomplete circle\n'
                for tl in tpl:
                    print tl
                print ''
            
            print 'finish a sentence\n'
                        
            '''
            for tl in s.tlinks_within:
                try:
                    if sum(tl.votes.values()) > tl.votes[tl.type]:
                        print 'conflict', tl.src, tl.sig, tl.votes
                    else:
                        print 'accepted', tl.src, tl.sig, tl.votes
                    print display_tlink(tl) + '\n'
                except AttributeError:
                    print 'tlink has no votes\n'
                    continue
            '''
        """
        for s in d.sents:
            st.write(str(s.sect))
        st.write('\n')
        if d.admission_event:
            st.write(str(d.admission_event.sent))
        else:
            st.write('+++++++')
        st.write('\n')
        if d.discharge_event:
            st.write(str(d.discharge_event.sent))
        else:
            st.write('+++++++')
        st.write('\n')
        if d.admission_timex3:
            st.write(str(d.admission_timex3.sent))
        else:
            st.write('+++++++')
        st.write('\n')
        if d.discharge_timex3:
            st.write(str(d.discharge_timex3.sent))
        else:
            st.write('+++++++')
        st.write('\n')
        for tl in d.tlinks_within_gold:
            st.write(tl.src + ' ' + tl.sig + '\n')
            st.write(display_tlink(tl) + '\n\n')
        for tl in d.tlinks_between_gold:
            st.write(tl.src + ' ' + str(tl.sent_dis) + ' ' + tl.sig + '\n')
            st.write(display_tlink(tl) + '\n\n')
        """
    print 'max_num_enty:', max_num_enty
    print 'conflict_info:', num_accepted, num_conflict, num_unknown, num_incomplete
    print '\t'.join([str(i) for i in [num_s, num_e, num_tx, num_st, num_within_gold, num_between_gold, num_within_cls, num_between_cls]])
        
    '''
    sys.stdout = open(os.path.join(project_base, data_pre + '_log'), 'w')
    
    dis = {}
    rel_sect = [0, 0, 0, 0]
    
    for d in ds.docs.values():
        print 'document:', d.ds_id, '\n'
        for tl in d.tlinks_between_gold:
            if tl.from_enty in d.timex3s and tl.to_enty in d.timex3s:
                if tl.from_enty.is_sectime or tl.to_enty.is_sectime:
                    rel_sect[0] += 1
                    continue
                else:
                    try:
                        dis[tl.sent_dis] += 1
                    except KeyError:
                        dis[tl.sent_dis] = 1
                    print 'branch 1', 'same_sect', tl.from_enty.sent.sect - tl.to_enty.sent.sect, tl.from_enty.type, tl.to_enty.type, 'dis', tl.sent_dis
                    print display_tlink(tl), '\n'
                    continue
            if tl.from_enty in d.timex3s:
                if tl.from_enty.is_sectime:
                    rel_sect[1] += 1
                    continue
                else:
                    try:
                        dis[tl.sent_dis] += 1
                    except KeyError:
                        dis[tl.sent_dis] = 1
                    print 'branch 2', 'same_sect', tl.from_enty.sent.sect - tl.to_enty.sent.sect, tl.from_enty.type, tl.to_enty.type, 'dis', tl.sent_dis
                    print display_tlink(tl), '\n'
                    continue
            if tl.to_enty in d.timex3s:
                if tl.to_enty.is_sectime:
                    rel_sect[2] += 1
                    continue
                else:
                    try:
                        dis[tl.sent_dis] += 1
                    except KeyError:
                        dis[tl.sent_dis] = 1
                    print 'branch 3', 'same_sect', tl.from_enty.sent.sect - tl.to_enty.sent.sect, tl.from_enty.type, tl.to_enty.type, 'dis', tl.sent_dis
                    print display_tlink(tl), '\n'
                    continue
            #if tl.from_enty.text.lower() in ['admission', 'discharge'] or tl.to_enty.text.lower() in ['admission', 'discharge']:
            if tl.from_enty in [d.admission_event, d.discharge_event] or tl.to_enty in [d.admission_event, d.discharge_event]:
                rel_sect[3] += 1
                #print 'branch sec_event', 'same_sect', tl.from_enty.sent.sect - tl.to_enty.sent.sect, tl.from_enty.type, tl.to_enty.type, 'dis', tl.sent_dis
                #print display_tlink(tl)
                continue
            try:
                dis[tl.sent_dis] += 1
            except KeyError:
                dis[tl.sent_dis] = 1
            print 'branch 4', 'from', tl.from_enty.sent.sect, 'to', tl.to_enty.sent.sect, tl.from_enty.type, tl.to_enty.type, 'dis', tl.sent_dis
            print display_tlink(tl), '\n'
            
    print dis
    print sum(dis.values())
    print sum([dis[1], dis[2], dis[3], dis[4], dis[5], dis[6], dis[7]])
    print sum([dis[1], dis[2], dis[3]])
    print rel_sect
    '''
        
    return
    
if __name__ == '__main__':
    main()