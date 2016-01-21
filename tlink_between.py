'''
Created on Jan 18, 2013

@author: yaocheng
'''

import os
import sys
import cPickle

from data import Dataset, Document, Sentence, Token, i2b2Event, TimeX3, SecTime, TLink, DependencyNode
from tlink_candidate import *
from conflict import verify
from tlink_feature import between_tlink_feats
from mallet import Config
from mallet_ML import train_on_data, apply_to_data
from project_path import project_base, mallet_bin, project_temp, data_pre_1, data_pre_2

def main():
    sys.stdout = open(os.path.join(project_base, data_pre_1 + '_' + data_pre_2 + '_between_log'), 'w')
    
    data_pre = data_pre_1
    try:
        with open(os.path.join(project_base, data_pre + '_dmp'), 'r') as fp:
            print 'un-pickling...'
            ds = cPickle.load(fp)
    except IOError:
        print 'something wrong with the pickle file path'
        
    between_tls = []
    for doc in ds.docs.values():
        between_tls.extend(doc.tlinks_between_gold)
    cfg = Config(mallet_bin, project_temp, data_pre + '_between')
    train_cfg = train_on_data(between_tls, lambda x: x.ds_id, lambda x: x.type, between_tlink_feats, 'MaxEnt', cfg)
        
    data_pre = data_pre_2
    try:
        with open(os.path.join(project_base, data_pre + '_dmp'), 'r') as fp:
            print 'un-pickling...'
            ds = cPickle.load(fp)
    except IOError:
        print 'something wrong with the pickle file path'
    
    pair = [0, 0, 0, 0]
    label = [0, 0, 0, 0]
    for doc in ds.docs.values():
        gold = doc.tlinks_between_gold
        candid = create_candid_event2sectime(doc)
        coref = create_candid_coref(doc)
        for c in coref:
            tl = search_tlink_between_enty(c.from_enty, c.to_enty, candid)
            if tl:
                tl.pred = 'OVERLAP'
            else:
                candid.append(c)
        update_candid_id(candid, doc.ds_id)
        cfg = Config(mallet_bin, project_temp, data_pre + '_between_' + doc.ds_id)
        ti = apply_to_data(candid, lambda x: x.ds_id, between_tlink_feats, train_cfg.model_path, cfg)
        for c in candid:
            c.pred = ti.ID2pred[c.ds_id]
        print 'document:', doc.ds_id
        rslt = verify(candid, gold)
        print rslt
        pair = [x + y for (x, y) in zip(pair, rslt[0])]
        label = [x + y for (x, y) in zip(label, rslt[1])]
    print 'pair', pair
    print 'label', label
    
if __name__ == '__main__':
    main()
        
    
    
        
        