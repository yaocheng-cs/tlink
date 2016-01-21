'''
Created on Jan 29, 2013

@author: yaocheng
'''

from itertools import combinations
from data import search_tlink_between_enty, create_tlink_between_enty

accepted_state = [('BEFORE', 'BEFORE', 'BEFORE'),
                  ('BEFORE', 'OVERLAP', 'BEFORE'),
                  ('OVERLAP', 'BEFORE', 'BEFORE'),
                  ('OVERLAP', 'OVERLAP', 'OVERLAP'),
                  ('OVERLAP', 'AFTER', 'AFTER'),
                  ('AFTER', 'OVERLAP', 'AFTER'),
                  ('AFTER', 'AFTER', 'AFTER')]

conflict_state = [('BEFORE', 'BEFORE', 'OVERLAP'),
                  ('BEFORE', 'BEFORE', 'AFTER'),
                  ('BEFORE', 'OVERLAP', 'OVERLAP'),
                  ('BEFORE', 'OVERLAP', 'AFTER'),
                  ('OVERLAP', 'BEFORE', 'OVERLAP'),
                  ('OVERLAP', 'BEFORE', 'AFTER'),
                  ('OVERLAP', 'OVERLAP', 'BEFORE'),
                  ('OVERLAP', 'OVERLAP', 'AFTER'),
                  ('OVERLAP', 'AFTER', 'BEFORE'),
                  ('OVERLAP', 'AFTER', 'OVERLAP'),
                  ('AFTER', 'OVERLAP', 'BEFORE'),
                  ('AFTER', 'OVERLAP', 'OVERLAP'),
                  ('AFTER', 'AFTER', 'BEFORE'),
                  ('AFTER', 'AFTER', 'OVERLAP')]

unknown_state =  [('BEFORE', 'AFTER', 'BEFORE'),
                  ('BEFORE', 'AFTER', 'OVERLAP'),
                  ('BEFORE', 'AFTER', 'AFTER'),
                  ('AFTER', 'BEFORE', 'BEFORE'),
                  ('AFTER', 'BEFORE', 'OVERLAP'),
                  ('AFTER', 'BEFORE', 'AFTER')
                  #('BEFORE', 'OVERLAP', 'OVERLAP'),
                  #('OVERLAP', 'BEFORE', 'OVERLAP'),
                  #('OVERLAP', 'OVERLAP', 'BEFORE'),
                  #('OVERLAP', 'OVERLAP', 'OVERLAP'),
                  #('OVERLAP', 'OVERLAP', 'AFTER'),
                  #('OVERLAP', 'AFTER', 'OVERLAP'),
                  #('AFTER', 'OVERLAP', 'OVERLAP')
                  ]

# probability of each label in training set
prior1 = {'BEFORE': 0.2676006384110658, 'OVERLAP': 0.5107288526334457, 'AFTER': 0.22167050895548857}

# probability of each label in correct initial prediction
# meaning that an "overlap" prediction is more trust worthy than a "after" prediction
prior2 = {'BEFORE': 0.23189563365282215, 'OVERLAP': 0.5862619808306709, 'AFTER': 0.18184238551650692}


def get_kth_large_key(d, k=1):
    t = sorted(d.items(), key=lambda x: x[1])
    return t[-k][0]

def opposite_label(label):
    if label != 'OVERLAP':
        return 'BEFOREAFTER'.replace(label, '')
    else:
        return label
    
def get_conflict_info(entits, tlinks, sort_key, stat_func):
    has_conflict = False
    num_conflict = 0
    sorted_entits = sorted(entits, key=sort_key)
    for t3 in tlinks:
        t3.votes = {'BEFORE': 0, 'OVERLAP': 0, 'AFTER': 0}
        t3.vote_probs = {'BEFORE': 0, 'OVERLAP': 0, 'AFTER': 0}
        bridge_entits = sorted_entits[:]
        if t3.from_enty == t3.to_enty:
            bridge_entits.remove(t3.from_enty)
            print 'from_enty and to_enty are the same'
        else:
            bridge_entits.remove(t3.from_enty)
            bridge_entits.remove(t3.to_enty)
        #if len(bridge_entits) > 0:
        #    weight = 1.0 / len(bridge_entits)
        for enty in bridge_entits:
            if sorted_entits.index(enty) < sorted_entits.index(t3.from_enty):
                t1 = search_tlink_between_enty(enty, t3.from_enty, tlinks)
                t2 = search_tlink_between_enty(enty, t3.to_enty, tlinks)
                if t1 and t2:
                    state = (opposite_label(stat_func(t1)), stat_func(t2), stat_func(t3))
                else:
                    continue
            elif sorted_entits.index(enty) > sorted_entits.index(t3.to_enty):
                t1 = search_tlink_between_enty(t3.from_enty, enty, tlinks)
                t2 = search_tlink_between_enty(t3.to_enty, enty, tlinks)
                if t1 and t2:
                    state = (stat_func(t1), opposite_label(stat_func(t2)), stat_func(t3))
                else:
                    continue
            else:
                #same_char = False
                t1 = search_tlink_between_enty(t3.from_enty, enty, tlinks)
                '''
                if t1:
                    t1_stat = stat_func(t1)
                else: # to handel two phrases starting at the same character
                    t1 = search_tlink_between_enty(enty, t3.from_enty, tlinks)
                    if t1:
                        t1_stat = opposite_label(stat_func(t1))
                        same_char = True
                    else:
                        continue
                '''
                t2 = search_tlink_between_enty(enty, t3.to_enty, tlinks)
                '''
                if t2:
                    t2_stat = stat_func(t2)
                else: # to handel two phrases starting at the same character
                    t2 = search_tlink_between_enty(t3.to_enty, enty, tlinks)
                    if t2:
                        t2_stat = opposite_label(stat_func(t2))
                        same_char = True
                    else:
                        continue
                '''
                #if same_char:
                #    print 'same character', t3.from_enty, enty, t3.to_enty
                #state = (t1_stat, t2_stat, stat_func(t3))
                state = (stat_func(t1), stat_func(t2), stat_func(t3))
            #print state
            #prior = prior2
            if state in accepted_state:
                t3.votes[state[2]] += 1
                #t3.vote_probs[state[2]] += t1.probs[state[0]] * prior[state[0]] * t2.probs[state[1]] * prior[state[1]]
                #t3.vote_probs[state[2]] += t1.probs[state[0]] * t2.probs[state[1]]
            if state in conflict_state[0:6]:
                t3.votes['BEFORE'] += 1
                #t3.vote_probs['BEFORE'] += t1.probs[state[0]] * prior[state[0]] * t2.probs[state[1]] * prior[state[1]]
                #t3.vote_probs['BEFORE'] += t1.probs[state[0]] * t2.probs[state[1]]
            if state in conflict_state[6:12]:
                t3.votes['AFTER'] += 1
                #t3.vote_probs['AFTER'] += t1.probs[state[0]] * prior[state[0]] * t2.probs[state[1]] * prior[state[1]]
                #t3.vote_probs['AFTER'] += t1.probs[state[0]] * t2.probs[state[1]]
            #if state in conflict_state[6:8]:
            #    t3.votes['OVERLAP'] += 1
                #t3.vote_probs['OVERLAP'] += t1.probs[state[0]] * prior[state[0]] * t2.probs[state[1]] * prior[state[1]]
                #t3.vote_probs['OVERLAP'] += t1.probs[state[0]] * t2.probs[state[1]]
            
        #for key in ['BEFORE', 'OVERLAP', 'AFTER']:
        #    if t3.votes[key] > 0:
        #        t3.vote_probs[key] = t3.vote_probs[key] / t3.votes[key]
        if sum(t3.votes.values()) > t3.votes[stat_func(t3)]:
            num_conflict += 1
    if num_conflict > 0:
        has_conflict = True
    return has_conflict, num_conflict
    
def get_conflict_info2(entits, tlinks, sort_key, stat_func):
    sorted_entits = sorted(entits, key=sort_key)
    accepted = []
    conflict = []
    unknown = []
    incomplete = []
    for tpl in combinations(sorted_entits, 3):
        t1 = search_tlink_between_enty(tpl[0], tpl[1], tlinks)
        t2 = search_tlink_between_enty(tpl[1], tpl[2], tlinks)
        t3 = search_tlink_between_enty(tpl[0], tpl[2], tlinks)
        if t1 and t2 and t3:
            if (stat_func(t1), stat_func(t2), stat_func(t3)) in accepted_state:
                accepted.append((t1, t2, t3))
            if (stat_func(t1), stat_func(t2), stat_func(t3)) in conflict_state:
                conflict.append((t1, t2, t3))
            if (stat_func(t1), stat_func(t2), stat_func(t3)) in unknown_state:
                unknown.append((t1, t2, t3))
        else:
            incomplete.append((t1, t2, t3))
        
        #t3.votes = {'BEFORE': 0, 'OVERLAP': 0, 'AFTER': 0}
        #t3.vote_probs = {'BEFORE': 0, 'OVERLAP': 0, 'AFTER': 0}
        
    return accepted, conflict, unknown, incomplete

def resolve_conflict_within(s):
    sorted_entits = sorted(s.events + s.timex3s, key=lambda x: x.span[0].begin)
    l = len(sorted_entits)
    if l <= 2:
        return
    for i in range(l - 2):
        for j in range(i + 2, l):
            a = sorted_entits[i]
            b = sorted_entits[j - 1]
            c = sorted_entits[j]
            t1 = search_tlink_between_enty(a, b, s.candids_within)
            t2 = search_tlink_between_enty(b, c, s.candids_within)
            t3 = search_tlink_between_enty(a, c, s.candids_within)
            if t1.pred == 'BEFORE' and t2.pred == 'BEFORE' and t3.pred == 'OVERLAP':
                #t3.pred = 'BEFORE'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'BEFORE' and t2.pred == 'BEFORE' and t3.pred == 'AFTER':
                #t3.pred = 'BEFORE'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'BEFORE' and t2.pred == 'OVERLAP' and t3.pred == 'OVERLAP':
                #t3.pred = 'BEFORE'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'BEFORE' and t2.pred == 'OVERLAP' and t3.pred == 'AFTER':
                #t3.pred = 'BEFORE'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'OVERLAP' and t2.pred == 'BEFORE' and t3.pred == 'OVERLAP':
                #t3.pred = 'BEFORE'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'OVERLAP' and t2.pred == 'BEFORE' and t3.pred == 'AFTER':
                #t3.pred = 'BEFORE'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'OVERLAP' and t2.pred == 'OVERLAP' and t3.pred == 'BEFORE':
                #t3.pred = 'OVERLAP'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'OVERLAP' and t2.pred == 'OVERLAP' and t3.pred == 'AFTER':
                #t3.pred = 'OVERLAP'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'OVERLAP' and t2.pred == 'AFTER' and t3.pred == 'BEFORE':
                #t3.pred = 'AFTER'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'OVERLAP' and t2.pred == 'AFTER' and t3.pred == 'OVERLAP':
                #t3.pred = 'AFTER'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'AFTER' and t2.pred == 'OVERLAP' and t3.pred == 'BEFORE':
                #t3.pred = 'AFTER'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'AFTER' and t2.pred == 'OVERLAP' and t3.pred == 'OVERLAP':
                #t3.pred = 'AFTER'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'AFTER' and t2.pred == 'AFTER' and t3.pred == 'BEFORE':
                #t3.pred = 'AFTER'
                t3.pred = get_kth_large_key(t3.probs, 2)
                continue
            if t1.pred == 'AFTER' and t2.pred == 'AFTER' and t3.pred == 'OVERLAP':
                #t3.pred = 'AFTER'
                t3.pred = get_kth_large_key(t3.probs, 2)
    '''
    for tl in s.candids_within:
        try:
            tl.pred = tl.temp
        except AttributeError:
            continue
    '''
    return


def resolve_conflict_within2(s):
    max_diff = 0
    min_diff = 1
    tl = None
    vote = None
    tls = []
    has_conflict = False
    for c in s.candids_within:
        '''
        if sum(c.votes.values()) > c.votes[c.pred]:
            vote = get_kth_large_key(c.probs, 2)
            #second_prob = get_kth_large_key(c.probs, 2)
            #if c.vote_probs[vote] + c.probs[vote] > c.vote_probs[c.pred] + c.probs[c.pred]:
            if c.vote_probs[vote] > c.vote_probs[c.pred]:
                c.pred = vote
        
        #vote = get_kth_large_key(c.votes)
        if sum(c.votes.values()) > c.votes[c.pred]:
            v = get_kth_large_key(c.probs, 2)
            diff = c.votes[v]- c.votes[c.pred]
            if diff > max_diff:
                max_diff = diff 
                tl = c
                vote = v
        '''
        #if sum(c.votes.values()) > c.votes[c.pred]:
        #    has_conflict = True
        first = get_kth_large_key(c.probs)
        second = get_kth_large_key(c.probs, 2)
        diff = c.probs[first] - c.probs[second]
        if diff < min_diff:
            min_diff = diff
            tl = c
            vote = second
    if tl and vote:
        tl.pred = vote
        
        
def verify(candid, gold):
    matched = []
    unmatched = []
    unwanted = []
    missed = []
    for c in candid:
        g = search_tlink_between_enty(c.from_enty, c.to_enty, gold)
        if g:
            if c.pred == g.type:
                matched.append(c)
            else:
                c.real = g.type
                unmatched.append(c)
        else:
            unwanted.append(c)
    for g in gold:
        c = search_tlink_between_enty(g.from_enty, g.to_enty, candid)
        if not c:
            missed.append(g)
    return matched, unmatched, unwanted, missed

'''
if sum(c.votes.values()) > c.votes[c.pred]:
        stat = 'conflict'
    else:
        stat = 'accepted'
    print 'match label:', stat, g.src, len(g.sent.events) + len(g.sent.timex3s)
    print 'm----------:', g.type, c.pred, c.votes
    print c.ds_id, display_tlink(g), '\n'
'''
        
        
def expand(s):
    inferable_pair = [tpl[0:2] for tpl in accepted_state]
    uncertain_pair = [tpl[0:2] for tpl in unknown_state]
    infered = []
    sorted_entits = sorted(s.events + s.timex3s, key=lambda x: x.span[0].begin)
    l = len(sorted_entits)
    for r in range(2, l):
        for fi in range(0, l - r):
            from_enty = sorted_entits[fi]
            ti = fi + r
            to_enty = sorted_entits[ti]
            tl3 = create_tlink_between_enty('dummy_id', from_enty, to_enty, src='expand')
            tl3.votes = {'BEFORE': 0, 'OVERLAP': 0, 'AFTER': 0}
            for d in range(1, r):
                mi = fi + d
                mid_enty = sorted_entits[mi]
                tl1 = search_tlink_between_enty(from_enty, mid_enty, s.candids_within)
                tl2 = search_tlink_between_enty(mid_enty, to_enty, s.candids_within)
                if tl1 and tl2:
                    if (tl1.pred, tl2.pred) in inferable_pair[0:3]:
                        tl3.votes['BEFORE'] += 1
                    if (tl1.pred, tl2.pred) in inferable_pair[3:6]:
                        tl3.votes['AFTER'] += 1
                    if (tl1.pred, tl2.pred) in uncertain_pair:
                        tl3.votes['OVERLAP'] += 1
                else:
                    print 'some bridge tlink is not ready'
            if sum(tl3.votes.values()) > 0:
                tl3.pred = get_kth_large_key(tl3.votes)
                infered.append(tl3)
                s.candids_within.append(tl3)
