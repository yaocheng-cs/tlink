'''
Created on Jul 31, 2012

@author: yaocheng
'''

import sys
import math

def matrix_report(tls):
    count = {'BEFORE_BEFORE': 0,
             'BEFORE_AFTER': 0,
             'BEFORE_OVERLAP': 0,
             'BEFORE_NONE': 0,
             'AFTER_BEFORE': 0,
             'AFTER_AFTER': 0,
             'AFTER_OVERLAP': 0,
             'AFTER_NONE': 0,
             'OVERLAP_BEFORE': 0,
             'OVERLAP_AFTER': 0,
             'OVERLAP_OVERLAP': 0,
             'OVERLAP_NONE': 0,
             'NONE_BEFORE': 0,
             'NONE_AFTER': 0,
             'NONE_OVERLAP': 0,
             'NONE_NONE': 0}
    for tl in tls:
        count[tl.tl_type + '_' + tl.pred] += 1
        
    print '\t'.join(['', 'BEFORE', 'AFTER', 'OVERLAP', 'NONE'])
    print '\t'.join(['BEFORE', str(count['BEFORE_BEFORE']), str(count['BEFORE_AFTER']), str(count['BEFORE_OVERLAP']), str(count['BEFORE_NONE'])])
    print '\t'.join(['AFTER', str(count['AFTER_BEFORE']), str(count['AFTER_AFTER']), str(count['AFTER_OVERLAP']), str(count['AFTER_NONE'])])
    print '\t'.join(['OVERLAP', str(count['OVERLAP_BEFORE']), str(count['OVERLAP_AFTER']), str(count['OVERLAP_OVERLAP']), str(count['OVERLAP_NONE'])])
    print '\t'.join(['NONE', str(count['NONE_BEFORE']), str(count['NONE_AFTER']), str(count['NONE_OVERLAP']), str(count['NONE_NONE'])])
    print 'Total number of tlinks:', sum(count.values())
    print 'Accuracy:', (count['BEFORE_BEFORE'] + count['AFTER_AFTER'] + count['OVERLAP_OVERLAP'] + count['NONE_NONE']) * 1.0 /sum(count.values())
    
    return

def error_report(comment0, comment1, fgroup):
    prefix = '_'.join(['both', comment0, comment1, '_'.join([str(i) for i in fgroup])])#, str(int(time()))])
    print prefix
    
    
    omit = fgroup
    fs = {}
    for i in range(1, len(feature_group) - 1):
        if i in omit:
            continue
        else:
            fs.update(feature_group[i])
    
    '''
    print 'Training...'
    
    ds = load_data_set(xml_full_c, xml_full_i, xml_full_i_cls, xml_full_dmp)
    insts = []
    for tl in ds.tlinks:
        if tl.tl_type != 'NONE':
            insts.append(TLinkInstance(tl, fs, False))
    
    print len(insts)
    
    train_cfg = Config(mallet_bin, xml_full_output, prefix)
    train = Training(train_cfg, insts)
    train.write_mallet()
    train.write_vector()
    train.train('MaxEnt')
    '''
    
    print 'Testing...'
    
    ds = load_data_set(xml_eval_c, xml_eval_i, None, xml_eval_dmp)
    insts = []
    for tl in ds.tlinks:
        if tl.src == 'gold':
            insts.append(TLinkInstance(tl, fs, False))
    
    print len(insts)
    
    test_cfg = Config(mallet_bin, xml_eval_output, prefix)
    test = Testing(test_cfg, insts)
    test.write_mallet()
    #test.write_vector()
    test.set_model(xml_full_output + '/' + prefix + '.model')
    test.test()
    
    bak = sys.stdout
    sys.stdout = open(xml_eval_output + '/' + prefix + '.txt', 'w')
    
    ti = TestingInspector(test)
    
    m = {}
    for key in ti.label_pair2i_id.keys():
        m[key] = len(ti.label_pair2i_id[key])
        print key, m[key]
        
    p_before = 1.0 * m['BEFORE_BEFORE'] / (m['BEFORE_BEFORE'] + m['BEFORE_AFTER'] + m['BEFORE_OVERLAP'])
    r_before = 1.0 * m['BEFORE_BEFORE'] / (m['BEFORE_BEFORE'] + m['AFTER_BEFORE'] + m['OVERLAP_BEFORE'])
    f1_before = 2 * p_before * r_before / (p_before + r_before)
    p_after = 1.0 * m['AFTER_AFTER'] / (m['AFTER_BEFORE'] + m['AFTER_AFTER'] + m['AFTER_OVERLAP'])
    r_after = 1.0 * m['AFTER_AFTER'] / (m['BEFORE_AFTER'] + m['AFTER_AFTER'] + m['OVERLAP_AFTER'])
    f1_after = 2 * p_after * r_after / (p_after + r_after)
    p_overlap = 1.0 * m['OVERLAP_OVERLAP'] / (m['OVERLAP_BEFORE'] + m['OVERLAP_AFTER'] + m['OVERLAP_OVERLAP'])
    r_overlap = 1.0 * m['OVERLAP_OVERLAP'] / (m['BEFORE_OVERLAP'] + m['AFTER_OVERLAP'] + m['OVERLAP_OVERLAP'])
    f1_overlap = 2 * p_overlap * r_overlap / (p_overlap + r_overlap)
    
    print 'p_before', p_before
    print 'r_before', r_before
    print 'f1_before', f1_before
    print 'p_after', p_after
    print 'r_after', r_after
    print 'f1_after', f1_after
    print 'p_overlap', p_overlap
    print 'r_overlap', r_overlap
    print 'f1_overlap', f1_overlap
    
    macro_p = (p_before + p_after + p_overlap) / 3
    print 'macro_p', macro_p
    macro_r = (r_before + r_after + r_overlap) / 3
    print 'macro_r', macro_r
    macro_f1 = (f1_before + f1_after + f1_overlap) / 3
    print 'macro_f1', macro_f1
    
    bo = {}
    bo['BEFORE_BEFORE'] = m['BEFORE_BEFORE']
    bo['BEFORE_OTHER'] = m['BEFORE_AFTER'] + m['BEFORE_OVERLAP']
    bo['OTHER_BEFORE'] = m['AFTER_BEFORE'] + m['OVERLAP_BEFORE']
    bo['OTHER_OTHER'] = m['AFTER_AFTER'] + m['AFTER_OVERLAP'] + m['OVERLAP_AFTER'] + m['OVERLAP_OVERLAP']
    
    ao = {}
    ao['AFTER_AFTER'] = m['AFTER_AFTER']
    ao['AFTER_OTHER'] = m['AFTER_BEFORE'] + m['AFTER_OVERLAP']
    ao['OTHER_AFTER'] = m['BEFORE_AFTER'] + m['OVERLAP_AFTER']
    ao['OTHER_OTHER'] = m['BEFORE_BEFORE'] + m['BEFORE_OVERLAP'] + m['OVERLAP_BEFORE'] + m['OVERLAP_OVERLAP']
    
    oo = {}
    oo['OVERLAP_OVERLAP'] = m['OVERLAP_OVERLAP']
    oo['OVERLAP_OTHER'] = m['OVERLAP_BEFORE'] + m['OVERLAP_AFTER']
    oo['OTHER_OVERLAP'] = m['BEFORE_OVERLAP'] + m['AFTER_OVERLAP']
    oo['OTHER_OTHER'] = m['BEFORE_BEFORE'] + m['BEFORE_AFTER'] + m['AFTER_BEFORE'] + m['AFTER_AFTER']
    
    s = {}
    s['TRUE_TRUE'] = bo['BEFORE_BEFORE'] + ao['AFTER_AFTER'] + oo['OVERLAP_OVERLAP']
    s['TRUE_FALSE'] = bo['BEFORE_OTHER'] + ao['AFTER_OTHER'] + oo['OVERLAP_OTHER']
    s['FALSE_TRUE'] = bo['OTHER_BEFORE'] + ao['OTHER_AFTER'] + oo['OTHER_OVERLAP']
    s['FALSE_FALSE'] = bo['OTHER_OTHER'] + ao['OTHER_OTHER'] + oo['OTHER_OTHER']
    
    micro_p = 1.0 * s['TRUE_TRUE'] / (s['TRUE_TRUE'] + s['TRUE_FALSE'])
    print 'micro_p', micro_p
    micro_r = 1.0 * s['TRUE_TRUE'] / (s['TRUE_TRUE'] + s['FALSE_TRUE'])
    print 'micro_r', micro_r
    micro_f1 = 2 * micro_p * micro_r / (micro_p + micro_r)
    print 'micro_f1', micro_f1
    
    sys.stdout = bak

def hist(ds):

    within = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    between = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    
    for tl in ds.tlinks:
        if tl.tl_type == 'NONE':
            continue
        if tl.sid == -1:
            between[tl.sent_dis] += 1
        else:
            within[len(tl.mid)] += 1
    return [within, between]

def count_src(ds):
    hypo = 0
    closure = 0
    gold = 0
    
    for d in ds.docs:
        hypo += len(d.h_tlinks)
        closure += len(d.cl_tlinks)
        gold += len(d.i_tlinks)
        
    print hypo, closure, gold
    return

def count_type(ds):
    total = [0, 0, 0, 0]
    for d in ds.docs:
        before = 0
        after = 0
        overlap = 0
        none = 0
        for tl in d.h_tlinks:
            if tl.tl_type == 'BEFORE':
                before += 1
            elif tl.tl_type == 'AFTER':
                after += 1
            elif tl.tl_type == 'OVERLAP':
                overlap += 1
            else:
                none += 1
        total[0] += before
        total[1] += after
        total[2] += overlap
        total[3] += none
        print d.ds_id, before, after, overlap, none
    print total
    return

def conflict_res(fp, fname):
    sys.stdout = open('/Users/yaocheng/Desktop/' + fname, 'w')
    
    accu = []
    ratio = []
    for line in fp:
        if line[:9] == 'Accuracy:':
            accu.append(float(line[10:-1]))
        if line[:15] == 'Conflict Ratio:':
            ratio.append(float(line[16:-1]))
    accu = accu[1:-1]
    before = accu[::2]
    after = accu[1::2]
    diff = []
    print '\t'.join(['before', 'after', 'improvement', 'conflict ratio'])
    for i in range(len(before)):
        dif = after[i] - before[i]
        diff.append(dif)
        print '\t'.join([str(i) for i in [before[i], after[i], dif, ratio[i]]])
    #t = paired_t([], [], 0, diff)
    print 'Number of Sents:', len(diff)
    print 'Average Improvement:', sum(diff) / len(diff)
    print 'Average Conflict Ratio:', sum(ratio) / len(ratio)
    #print 't value:', t
    
def paired_t(a, b, u=0, diff=None):
    if len(a) != len(b):
        print 'size of samples has to be the same'
        return
    if not diff:
        diff = []
        for i in range(len(a)):
            dif = b[i] - a[i]
            diff.append(dif)
    avg = sum(diff) / len(diff)
    sd = math.sqrt(sum([math.pow(dif - avg, 2) for dif in diff]) / len(diff))
    t = (avg - u) / (sd / math.sqrt(len(diff)))
    return t
    
    
def main():
    with open(sys.argv[1]) as fp:
        prefix = sys.argv[1].split('.')[0].split('_')[-1]
        fname = prefix + '.txt'
        conflict_res(fp, fname)

if __name__ == '__main__':
    main()
