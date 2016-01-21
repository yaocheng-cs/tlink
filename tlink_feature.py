'''
Created on Aug 1, 2012

@author: yaocheng
'''

from mallet import Instance
from data import get_phrase_head, get_tlink_dep_path, get_tlink_context

# version 0

def _tense(head):
    if head.pos[0:2] != 'VB':
        return 'nonverb'
    else:
        if head.pos == 'VBD':
            return 'past'
        if head.pos == 'VBG':
            try:
                pre_t = head.sent.span[head.offset - 1]
                if pre_t.form.lower() in ['is', 'am', 'are', "'s", "'m", "'re", '&apos;s', '&apos;m', '&apos;re'] or \
                    pre_t.form.lower()[-2:] in ["'s", "'m"] or pre_t.form.lower()[-3:] in ["'re"]:
                    #return 'present_participle'
                    return 'present'
                else:
                    #return 'gerund'
                    return 'unknown'
            except IndexError:
                #return 'gerund'
                return 'unknown'
        if head.pos == 'VBN':
            #return 'past_participle'
            return 'past'
        if head.pos in ['VBP', 'VBZ']:
            return 'present'
        # the case when head is in base form, head.pos == 'VB'
        try:
            pre_t = head.sent.span[head.offset - 1]
            if pre_t.form.lower() in ['will', 'would', "'ll", "'d", '&apos;ll', '&apos;d'] or \
                pre_t.form.lower()[-2:] in ["'d"] or pre_t.form.lower()[-3:] in ["'ll"]:
                return 'future'
            elif pre_t.form.lower() in ['did', 'could']:
                return 'past'
            else:
                return 'unknown'
        except IndexError:
            return 'unknown'

def from_tense(tl):
    head = get_phrase_head(tl.from_enty)
    if head:
        return _tense(head)

def to_tense(tl):
    head = get_phrase_head(tl.to_enty)
    if head:
        return _tense(head)
        
def tense_pair(tl):
    if from_tense(tl) and to_tense(tl):
        return from_tense(tl) + '_' + to_tense(tl)

"""
def short_mid(tlink):
    if tlink.sent_dis > 0:
        return None
    mid = tlink.mid
    if len(mid) <= 3 and len(mid) > 0:
        dnls = [t.dep_node.lemma for t in mid]
        if ',' not in dnls and ';' not in dnls and ':' not in dnls:
            return dnls
        
def short_mid_POS(tlink):
    if tlink.sent_dis > 0:
        return None
    mid = tlink.mid
    if len(mid) <= 3 and len(mid) == 0:
        dnps = [t.dep_node.pos for t in mid]
        if ',' not in dnps and ';' not in dnps and ':' not in dnps:
            return dnps
    
def mid_t_w_pos(tlink):
    if tlink.sent_dis > 0:
        return None
    buf = []
    for t in tlink.mid:
        dn = t.dep_node
        if dn.pos in ['IN', 'TO', 'CC', 'POS', 'RP'] or t.pos[0:2] in ['VB', 'RB', 'WP', 'WR']:
            buf.append(dn.lemma)
    return buf

def one_t_mid(tlink):
    if tlink.sent_dis > 0:
        return None
    if len(tlink.mid) == 1:
        return tlink.mid[0].dep_node.lemma
    else:
        return None
    
def one_t_mid_POS(tlink):
    if tlink.sent_dis > 0:
        return None
    if len(tlink.mid) == 1:
        return tlink.mid[0].dep_node.pos
    else:
        return None
    
def short_mid_POS_concat(tlink):
    dnps = short_mid_POS(tlink)
    if dnps:
        return '_'.join(dnps)
    
def mid_vb(tlink):
    buf = []
    for t in tlink.mid:
        dn = t.dep_node
        if dn.pos[0:2] == 'VB': #and dn.lemma not in ['have', 'be']:
            buf.append(dn.lemma)
    return buf

def mid_adv(tlink):
    if tlink.sent_dis > 0:
        return None
    buf = []
    for t in tlink.mid:
        dn = t.dep_node
        if dn.pos[0:2] == 'RB':
            buf.append(dn.lemma)
    return buf


def mid_wh(tlink):
    if tlink.sent_dis > 0:
        return None
    buf = []
    for t in tlink.mid:
        dn = t.dep_node
        if dn.pos[0:2] in ['WP', 'WR']:
            buf.append(dn.lemma)
    return buf

def mid_prep(tlink):
    if tlink.sent_dis > 0:
        return None
    buf = []
    for t in tlink.mid:
        dn = t.dep_node
        if dn.pos in ['IN', 'TO']:
            buf.append(dn.lemma)
    return buf

def mid_conj(tlink):
    if tlink.sent_dis > 0:
        return None
    buf = []
    for t in tlink.mid:
        dn = t.dep_node
        if dn.pos in ['CC']:
            buf.append(dn.lemma)
    return buf

def from_t_path(tlink):
    if not tlink.dep_path:
        return None
    path = tlink.dep_path.from_path
    buf = []
    for dn in path:
        if dn.pos:
            if dn.pos in ['IN', 'TO', 'CC', 'POS', 'RP'] or dn.pos[0:2] in ['VB', 'RB', 'WP', 'WR']:
                buf.append(dn.lemma)
    return buf

def from_t_path_concat(tlink):
    buf = from_t_path(tlink)
    if buf:
        return '_'.join(buf)

def to_t_path(tlink):
    if not tlink.dep_path:
        return None
    path = tlink.dep_path.to_path
    buf = []
    for dn in path:
        if dn.pos:
            if dn.pos in ['IN', 'TO', 'CC', 'POS', 'RP'] or dn.pos[0:2] in ['VB', 'RB', 'WP', 'WR']:
                buf.append(dn.lemma)
    return buf

def to_t_path_concat(tlink):
    buf = to_t_path(tlink)
    if buf:
        return '_'.join(buf)
    
def from_deprel_path(tlink):
    if tlink.sent_dis > 0:
        return None
    if not tlink.dep_path:
        return None
    path = tlink.dep_path.from_path
    buf = []
    for dn in path[:-1]:
        buf.append(dn.deprel)
    return buf

def from_deprel_path_concat(tlink):
    buf = from_deprel_path(tlink)
    if buf:
        return '_'.join(buf)

def to_deprel_path(tlink):
    if tlink.sent_dis > 0:
        return None
    if not tlink.dep_path:
        return None
    path = tlink.dep_path.to_path
    buf = []
    for dn in path[:-1]:
        buf.append(dn.deprel)
    return buf

def to_deprel_path_concat(tlink):
    buf = to_deprel_path(tlink)
    if buf:
        return '_'.join(buf)
    
def root_equal(tlink):
    if tlink.sent_dis > 0:
        return None
    cr = com_root(tlink)
    if cr:
        if cr == tlink.dep_path.from_path[0].lemma:
            return 'fromhead'
        if cr == tlink.dep_path.to_path[0].lemma:
            return 'tohead'
    return None
    

    
    
    
    


    
    
"""


def from_type(tl):
    return tl.from_enty.type

def to_type(tl):
    return tl.to_enty.type

def from_pos(tl):
    head = get_phrase_head(tl.from_enty)
    return head.pos

def to_pos(tl):
    head = get_phrase_head(tl.to_enty)
    return head.pos

def sent_dis(tl):
    return tl.sent_dis

def same_sect(tl):
    if tl.from_enty.sent.sect == tl.to_enty.sent.sect:
        return 'true'
    
def sig(tl):
    return tl.sig

def from_sig(tl):
    return tl.from_enty.sig

def to_sig(tl):
    return tl.to_enty.sig

def token_dis(tl):
    return tl.to_enty.span[0].offset - tl.from_enty.span[-1].offset - 1

def short_mid_concat(tl):
    if token_dis(tl) <= 3:
        mid = get_tlink_context(tl)[1]
        return '_'.join([t.lemma for t in mid])

def from_head(tl):
    head = get_phrase_head(tl.from_enty)
    return head.lemma

def to_head(tl):
    head = get_phrase_head(tl.to_enty)
    return head.lemma

def from_vrel_to(tl):
    fh = get_phrase_head(tl.from_enty)
    th = get_phrase_head(tl.to_enty)
    if fh.dep_node.head == th.dep_node and th.pos[:2] == 'VB':
        #return 'true'
        return th.lemma
    
def to_vrel_from(tl):
    fh = get_phrase_head(tl.from_enty)
    th = get_phrase_head(tl.to_enty)
    if th.dep_node.head == fh.dep_node and fh.pos[:2] == 'VB':
        #return 'true'
        return fh.lemma

def from_head_vb(tl):
    fh = get_phrase_head(tl.from_enty)
    if fh.pos[:2] == 'VB':
        return fh.lemma
        #return 'true'
    
def to_head_vb(tl):
    th = get_phrase_head(tl.to_enty)
    if th.pos[:2] == 'VB':
        return th.lemma
        #return 'true'
    
def ident_head(tl):
    fh = get_phrase_head(tl.from_enty)
    th = get_phrase_head(tl.to_enty)
    if fh.lemma == th.lemma:
        return 'true'
        #return fh.lemma

def vb_mid(tl):
    mid = get_tlink_context(tl)[1]
    if len(mid) == 1 and mid[0].pos[:2] == 'VB':
        #return mid[0].lemma
        return 'true'

def adv_mid(tl):
    mid = get_tlink_context(tl)[1]
    if len(mid) == 1 and mid[0].pos[:2] == 'RB':
        #return mid[0].lemma
        return 'true'
    
def conj_mid(tl):
    mid = get_tlink_context(tl)[1]
    if len(mid) == 1 and mid[0].pos[:2] == 'CC':
        #return mid[0].lemma
        return 'true'
    
def prep_mid(tl):
    mid = get_tlink_context(tl)[1]
    if len(mid) == 1 and mid[0].pos[:2] in ['IN', 'TO']:
        #return mid[0].lemma
        return 'true'
    
def wh_mid(tl):
    mid = get_tlink_context(tl)[1]
    if len(mid) == 1 and mid[0].pos[:2] in ['WD', 'WP', 'WR']:
        #return mid[0].lemma
        return 'true'
    
def mid_vb_pos(tl):
    mid = get_tlink_context(tl)[1]
    buf = []
    for t in mid:
        if t.pos[:2] == 'VB':
            buf.append(t.pos)
    return buf

def mid_vb(tl):
    mid = get_tlink_context(tl)[1]
    buf = []
    for t in mid:
        if t.pos[:2] == 'VB':
            buf.append(t.lemma)
    return buf
    
def mid_rbr(tl):
    mid = get_tlink_context(tl)[1]
    buf = []
    for t in mid:
        if t.pos == 'RBR':
            buf.append(t.lemma)
    return buf

def mid_rbs(tl):
    mid = get_tlink_context(tl)[1]
    buf = []
    for t in mid:
        if t.pos == 'RBS':
            buf.append(t.lemma)
    return buf

def mid_jjr(tl):
    mid = get_tlink_context(tl)[1]
    buf = []
    for t in mid:
        if t.pos == 'JJR':
            buf.append(t.lemma)
    return buf

def mid_jjs(tl):
    mid = get_tlink_context(tl)[1]
    buf = []
    for t in mid:
        if t.pos == 'JJS':
            buf.append(t.lemma)
    return buf

def mid_in(tl):
    mid = get_tlink_context(tl)[1]
    buf = []
    for t in mid:
        if t.pos == 'IN':
            buf.append(t.lemma)
    return buf

def mid_to(tl):
    mid = get_tlink_context(tl)[1]
    buf = []
    for t in mid:
        if t.pos == 'TO':
            buf.append(t.lemma)
    return buf
    
def mid_cc(tl):
    mid = get_tlink_context(tl)[1]
    buf = []
    for t in mid:
        if t.pos == 'CC':
            buf.append(t.lemma)
    return buf

def mid_wp(tl):
    mid = get_tlink_context(tl)[1]
    buf = []
    for t in mid:
        if t.pos[:2] == 'WP':
            buf.append(t.lemma)
    return buf

def mid_wrb(tl):
    mid = get_tlink_context(tl)[1]
    buf = []
    for t in mid:
        if t.pos == 'WRB':
            buf.append(t.lemma)
    return buf

def from_head_to(tl):
    dp = get_tlink_dep_path(tl)
    if len(dp.from_path) == 1:
        return 'true'
    
def to_head_from(tl):
    dp = get_tlink_dep_path(tl)
    if len(dp.to_path) == 1:
        return 'true'
    
def some_head_both(tl):
    dp = get_tlink_dep_path(tl)
    if len(dp.from_path) != 1 and len(dp.to_path) != 1:
        return 'true'
    
def consecutive_enty(tl):
    # there are annotation errors where from_enty and to_enty are referring to the same entity
    try:
        entits = tl.sent.events + tl.sent.timex3s
        entits.remove(tl.from_enty)
        entits.remove(tl.to_enty)
        for enty in entits:
            if enty.span[0].offset > tl.from_enty.span[-1].offset and enty.span[-1].offset < tl.to_enty.span[0].offset:
                return
        return 'true'
    except ValueError:
        print tl.ds_id, tl.from_enty, tl.to_enty

def adjacent_enty(tl):
    if tl.from_enty.span[-1].offset == tl.to_enty.span[0].offset - 1:
        return 'true'
    
def prep_obj_from(tl):
    left = get_tlink_context(tl)[0]
    if len(left) > 0:
        if left[-1].pos == 'IN':
            #return 'true'
            return left[-1].lemma

def prep_obj_to(tl):
    mid = get_tlink_context(tl)[1]
    if len(mid) > 0:
        if mid[-1].pos == 'IN':
            #return 'true'
            return mid[-1].lemma
        
def to_obj_from(tl):
    left = get_tlink_context(tl)[0]
    if len(left) > 0:
        if left[-1].pos == 'TO':
            return 'true'
        
def to_obj_to(tl):
    mid = get_tlink_context(tl)[1]
    if len(mid) > 0:
        if mid[-1].pos == 'TO':
            return 'true'

def root(tl):
    dp = get_tlink_dep_path(tl)
    try:
        return dp.from_path[-1].ref.lemma
    except AttributeError:
        return

def root_pos(tl):
    dp = get_tlink_dep_path(tl)
    try:
        return dp.from_path[-1].ref.pos
    except AttributeError:
        return
    
def fp_vb(tl):
    fp = get_tlink_dep_path(tl).from_path
    if len(fp) < 3:
        return
    buf = []
    for t in [dn.ref for dn in fp[1:-1]]:
        if t.pos[:2] == 'VB':
            buf.append(t.lemma)
    return buf

def fp_in(tl):
    fp = get_tlink_dep_path(tl).from_path
    if len(fp) < 3:
        return
    buf = []
    for t in [dn.ref for dn in fp[1:-1]]:
        if t.pos == 'IN':
            buf.append(t.lemma)
    return buf

def fp_rb(tl):
    fp = get_tlink_dep_path(tl).from_path
    if len(fp) < 3:
        return
    buf = []
    for t in [dn.ref for dn in fp[1:-1]]:
        if t.pos[:2] == 'RB':
            buf.append(t.lemma)
    return buf

def fp_nn(tl):
    fp = get_tlink_dep_path(tl).from_path
    if len(fp) < 3:
        return
    buf = []
    for t in [dn.ref for dn in fp[1:-1]]:
        if t.pos[:2] == 'NN':
            buf.append(t.lemma)
    return buf

def fp_cc(tl):
    fp = get_tlink_dep_path(tl).from_path
    if len(fp) < 3:
        return
    buf = []
    for t in [dn.ref for dn in fp[1:-1]]:
        if t.pos == 'CC':
            buf.append(t.lemma)
    return buf

def tp_vb(tl):
    tp = get_tlink_dep_path(tl).to_path
    if len(tp) < 3:
        return
    buf = []
    for t in [dn.ref for dn in tp[1:-1]]:
        if t.pos[:2] == 'VB':
            buf.append(t.lemma)
    return buf

def tp_in(tl):
    tp = get_tlink_dep_path(tl).to_path
    if len(tp) < 3:
        return
    buf = []
    for t in [dn.ref for dn in tp[1:-1]]:
        if t.pos == 'IN':
            buf.append(t.lemma)
    return buf

def tp_rb(tl):
    tp = get_tlink_dep_path(tl).to_path
    if len(tp) < 3:
        return
    buf = []
    for t in [dn.ref for dn in tp[1:-1]]:
        if t.pos[:2] == 'RB':
            buf.append(t.lemma)
    return buf

def tp_nn(tl):
    tp = get_tlink_dep_path(tl).to_path
    if len(tp) < 3:
        return
    buf = []
    for t in [dn.ref for dn in tp[1:-1]]:
        if t.pos[:2] == 'NN':
            buf.append(t.lemma)
    return buf

def tp_cc(tl):
    tp = get_tlink_dep_path(tl).to_path
    if len(tp) < 3:
        return
    buf = []
    for t in [dn.ref for dn in tp[1:-1]]:
        if t.pos == 'CC':
            buf.append(t.lemma)
    return buf

def left_token(tl):
    left = get_tlink_context(tl)[0]
    try:
        if left[-1].type == 'WordToken':
            return left[-1].lemma
    except IndexError:
        return
    
def left_token_pos(tl):
    left = get_tlink_context(tl)[0]
    try:
        if left[-1].type == 'WordToken':
            return left[-1].pos
    except IndexError:
        return

def right_token(tl):
    right = get_tlink_context(tl)[2]
    try:
        if right[0].type == 'WordToken':
            return right[0].lemma
    except IndexError:
        return
    
def right_token_pos(tl):
    right = get_tlink_context(tl)[2]
    try:
        if right[0].type == 'WordToken':
            return right[0].pos
    except IndexError:
        return
    
def sect(tl):
    return tl.sent.sect

def match_enty(tl):
    if tl.from_enty.text.lower() == tl.to_enty.text.lower():
        return 'true'
    
def from_loc(tl):
    if tl.from_enty.type == 'CLINICAL_DEPT':
        return 'true'
    
def to_loc(tl):
    if tl.to_enty.type == 'CLINICAL_DEPT':
        return 'true'
    
def from_prefix(tl):
    for p in ['pre', 'post', 'inter']:
        if p in tl.from_enty.text.lower():
            return p

def to_prefix(tl):
    for p in ['pre', 'post', 'inter']:
        if p in tl.to_enty.text.lower():
            return p
        
def left_prefix(tl):
    left = get_tlink_context(tl)[0]
    left = ' '.join([t.form.lower() for t in left])
    for p in ['pre', 'post', 'inter']:
        if p in left:
            return p
        
def mid_prefix(tl):
    mid = get_tlink_context(tl)[1]
    mid = ' '.join([t.form.lower() for t in mid])
    for p in ['pre', 'post', 'inter']:
        if p in mid:
            return p
        
def right_prefix(tl):
    right = get_tlink_context(tl)[2]
    right = ' '.join([t.form.lower() for t in right])
    for p in ['pre', 'post', 'inter']:
        if p in right:
            return p

between_tlink_feats = [from_type,
                       to_type,
                       from_pos,
                       to_pos,
                       sent_dis,
                       same_sect]

#vb_mid, adv_mid, wh_mid, prep_mid, conj_mid,
#sig,


positional_feats = [token_dis,
                    adjacent_enty, consecutive_enty,
                    sect]

dependency_feats = [from_vrel_to, to_vrel_from,
                    from_head_to, to_head_from, some_head_both,
                    root, root_pos,
                    fp_vb, fp_in, fp_rb, fp_nn, fp_cc, tp_vb, tp_in, tp_rb, tp_nn, tp_cc]

contextual_feats = [short_mid_concat,
                    left_token, left_token_pos, right_token, right_token_pos,
                    mid_vb_pos, mid_vb, mid_rbr, mid_rbs, mid_jjr, mid_jjs, mid_in, mid_to, mid_cc, mid_wp, mid_wrb,
                    left_prefix, mid_prefix, right_prefix,
                    prep_obj_from, prep_obj_to, to_obj_from, to_obj_to]

tense_feats      = [from_tense, to_tense, tense_pair]

other_feats      = [from_type, to_type,
                    from_pos, to_pos,
                    from_sig, to_sig,
                    from_head, to_head, from_head_vb, to_head_vb,
                    ident_head, match_enty,
                    from_loc, to_loc,
                    from_prefix, to_prefix]
