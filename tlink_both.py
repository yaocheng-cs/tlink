'''
Created on Mar 12, 2013

@author: yaocheng
'''

import os
import sys
import cPickle
from lxml import etree
from data import Dataset, Document, Sentence, Token, i2b2Event, TimeX3, SecTime, TLink, DependencyNode
from tlink_candidate import *
from tlink_feature import positional_feats, contextual_feats, dependency_feats, tense_feats, other_feats
from mallet import Config
from mallet_ML import train_on_data, apply_to_data
from project_path import project_base, mallet_bin, project_temp, data_pre_1, data_pre_2


within_tlink_feats = positional_feats + contextual_feats + dependency_feats + tense_feats + other_feats
#within_tlink_feats = contextual_feats + dependency_feats + tense_feats + other_feats
#within_tlink_feats = positional_feats + dependency_feats + tense_feats + other_feats
#within_tlink_feats = positional_feats + contextual_feats + tense_feats + other_feats
#within_tlink_feats = positional_feats + contextual_feats + dependency_feats + other_feats
#within_tlink_feats = positional_feats + contextual_feats + dependency_feats + tense_feats
#within_tlink_feats = positional_feats + tense_feats + other_feats

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
    train_cfg = Config(mallet_bin, project_temp, data_pre + '_within')
    train_on_data(within_tls, lambda x: x.ds_id, lambda x: x.type, within_tlink_feats, 'MaxEnt', train_cfg)
    
    data_pre = data_pre_2
    try:
        with open(os.path.join(project_base, data_pre + '_dmp'), 'r') as fp:
            print 'un-pickling...'
            ds = cPickle.load(fp)
    except IOError:
        print 'something wrong with the pickle file path'
        
    within_candids = []
    between_candids = []
    for doc in ds.docs.values():
        # within
        w_candid = create_candid_within3(doc)
        update_candid_id(w_candid, doc.ds_id)
        within_candids.extend(w_candid)
        test_cfg = Config(mallet_bin, project_temp, data_pre + '_within_' + doc.ds_id)
        ti = apply_to_data(w_candid, lambda x: x.ds_id, within_tlink_feats, train_cfg.model_path, test_cfg)
        for c in w_candid:
            c.pred = ti.ID2pred[c.ds_id]
            c.probs = ti.ID2probs[c.ds_id]
        # between
        b_candid = create_candid_event2sectime(doc)
        coref = create_candid_coref(doc)
        for c in coref:
            tl = search_tlink_between_enty(c.from_enty, c.to_enty, b_candid)
            if tl:
                tl.pred = 'OVERLAP'
            else:
                b_candid.append(c)
        between_candids.extend(b_candid)
        
        gold_xml = project_base + '/' + data_pre_2 + '_i_sub' + '/' + doc.ds_id + '.xml'
        if not os.path.exists(gold_xml):
            print 'skip xml', doc.ds_id
            continue
        pred_xml = project_base + '/' + data_pre_2 + '_pred_all' + '/' + doc.ds_id + '.xml'
        parser = etree.XMLParser(recover=True)
        try:
            tree = etree.parse(gold_xml, parser)
        except:
            print 'Something wrong with opening/parsing specified input xml file'
            raise
        root = tree.getroot()
        tags = root.find('TAGS')
        # for evaluation purpose, remove original tlink
        tlinks = tags.findall('TLINK')
        for tl in tlinks:
            tags.remove(tl)
            
        counter = 0
        for tl in w_candid + b_candid:
            tl_elmt = etree.Element('TLINK')
            tl_elmt.set('id', 'TL' + str(counter))
            tl_elmt.set('fromID', tl.from_enty.origin_id)
            tl_elmt.set('fromText', str(tl.from_enty))
            tl_elmt.set('toID', tl.to_enty.origin_id)
            tl_elmt.set('toText', str(tl.to_enty))
            tl_elmt.set('type', tl.pred)
            # the 'tail' is set so that each TLINK will start from a new line
            tl_elmt.tail = '\n'
            tags.append(tl_elmt)
            counter += 1
            
        with open(pred_xml, 'w') as fp:
            fp.write(etree.tostring(root, xml_declaration=True).replace('/>', ' />'))
    """
    try:
        p = os.path.join(project_base,  data_pre + '_within_result_dmp')
        if not os.path.exists(p):
            with open(p, 'w') as fp:
                cPickle.dump(within_candids, fp)
        p = os.path.join(project_base,  data_pre + '_between_result_dmp')
        if not os.path.exists(p):
            with open(p, 'w') as fp:
                cPickle.dump(between_candids, fp)
    except:
        print 'something wrong when dumping tlink result'
    """


def main_within():
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
    train_cfg = Config(mallet_bin, project_temp, data_pre + '_within')
    train_on_data(within_tls, lambda x: x.ds_id, lambda x: x.type, within_tlink_feats, 'MaxEnt', train_cfg)
    
    data_pre = data_pre_2
    try:
        with open(os.path.join(project_base, data_pre + '_dmp'), 'r') as fp:
            print 'un-pickling...'
            ds = cPickle.load(fp)
    except IOError:
        print 'something wrong with the pickle file path'
        
    for doc in ds.docs.values():
        # within
        w_candid = create_candid_within3(doc)
        update_candid_id(w_candid, doc.ds_id)
        test_cfg = Config(mallet_bin, project_temp, data_pre + '_within_' + doc.ds_id)
        ti = apply_to_data(w_candid, lambda x: x.ds_id, within_tlink_feats, train_cfg.model_path, test_cfg)
        for c in w_candid:
            c.pred = ti.ID2pred[c.ds_id]
            c.probs = ti.ID2probs[c.ds_id]
        
        gold_xml = project_base + '/' + data_pre_2 + '_i_sub' + '/' + doc.ds_id + '.xml'
        if not os.path.exists(gold_xml):
            print 'skip xml', doc.ds_id
            continue
        w_pred_xml = project_base + '/' + data_pre_2 + '_w_pred_dep_contx' + '/' + doc.ds_id + '.xml'
        # w_gold_xml = project_base + '/' + data_pre_2 + '_w_gold_all' + '/' + doc.ds_id + '.xml'
        parser = etree.XMLParser(recover=True)
        try:
            tree = etree.parse(gold_xml, parser)
        except:
            print 'Something wrong with opening/parsing specified input xml file'
            raise
        root = tree.getroot()
        tags = root.find('TAGS')
        # for evaluation purpose, remove original tlink
        tlinks = tags.findall('TLINK')
        for tl in tlinks:
            tags.remove(tl)
            
        counter = 0
        for tl in w_candid:
            tl_elmt = etree.Element('TLINK')
            tl_elmt.set('id', 'TL' + str(counter))
            tl_elmt.set('fromID', tl.from_enty.origin_id)
            tl_elmt.set('fromText', str(tl.from_enty))
            tl_elmt.set('toID', tl.to_enty.origin_id)
            tl_elmt.set('toText', str(tl.to_enty))
            tl_elmt.set('type', tl.pred)
            # the 'tail' is set so that each TLINK will start from a new line
            tl_elmt.tail = '\n'
            tags.append(tl_elmt)
            counter += 1
            
        with open(w_pred_xml, 'w') as fp:
            fp.write(etree.tostring(root, xml_declaration=True).replace('/>', ' />'))
            
        """
        tlinks = tags.findall('TLINK')
        for tl in tlinks:
            tags.remove(tl)
            
        for tl in doc.tlinks_within_gold:
            tl_elmt = etree.Element('TLINK')
            tl_elmt.set('id', str(tl.origin_id))
            tl_elmt.set('fromID', tl.from_enty.origin_id)
            tl_elmt.set('fromText', str(tl.from_enty))
            tl_elmt.set('toID', tl.to_enty.origin_id)
            tl_elmt.set('toText', str(tl.to_enty))
            tl_elmt.set('type', tl.type)
            # the 'tail' is set so that each TLINK will start from a new line
            tl_elmt.tail = '\n'
            tags.append(tl_elmt)
            
        with open(w_gold_xml, 'w') as fp:
            fp.write(etree.tostring(root, xml_declaration=True).replace('/>', ' />'))
        """
        
def main_between():
    data_pre = data_pre_2
    try:
        with open(os.path.join(project_base, data_pre + '_dmp'), 'r') as fp:
            print 'un-pickling...'
            ds = cPickle.load(fp)
    except IOError:
        print 'something wrong with the pickle file path'
        
    for doc in ds.docs.values():
        b_candid = create_candid_event2sectime(doc)
        coref = create_candid_coref(doc)
        for c in coref:
            tl = search_tlink_between_enty(c.from_enty, c.to_enty, b_candid)
            if tl:
                tl.pred = 'OVERLAP'
            else:
                b_candid.append(c)
        
        gold_xml = project_base + '/' + data_pre_2 + '_i_sub' + '/' + doc.ds_id + '.xml'
        if not os.path.exists(gold_xml):
            print 'skip xml', doc.ds_id
            continue
        b_pred_xml = project_base + '/' + data_pre_2 + '_b_pred' + '/' + doc.ds_id + '.xml'
        b_gold_xml = project_base + '/' + data_pre_2 + '_b_gold' + '/' + doc.ds_id + '.xml'
        parser = etree.XMLParser(recover=True)
        try:
            tree = etree.parse(gold_xml, parser)
        except:
            print 'Something wrong with opening/parsing specified input xml file'
            raise
        root = tree.getroot()
        tags = root.find('TAGS')
        # for evaluation purpose, remove original tlink
        tlinks = tags.findall('TLINK')
        for tl in tlinks:
            tags.remove(tl)
            
        counter = 0
        for tl in b_candid:
            tl_elmt = etree.Element('TLINK')
            tl_elmt.set('id', 'TL' + str(counter))
            tl_elmt.set('fromID', tl.from_enty.origin_id)
            tl_elmt.set('fromText', str(tl.from_enty))
            tl_elmt.set('toID', tl.to_enty.origin_id)
            tl_elmt.set('toText', str(tl.to_enty))
            tl_elmt.set('type', tl.pred)
            # the 'tail' is set so that each TLINK will start from a new line
            tl_elmt.tail = '\n'
            tags.append(tl_elmt)
            counter += 1
            
        with open(b_pred_xml, 'w') as fp:
            fp.write(etree.tostring(root, xml_declaration=True).replace('/>', ' />'))
            
        
        tlinks = tags.findall('TLINK')
        for tl in tlinks:
            tags.remove(tl)
            
        for tl in doc.tlinks_between_gold:
            tl_elmt = etree.Element('TLINK')
            tl_elmt.set('id', str(tl.origin_id))
            tl_elmt.set('fromID', tl.from_enty.origin_id)
            tl_elmt.set('fromText', str(tl.from_enty))
            tl_elmt.set('toID', tl.to_enty.origin_id)
            tl_elmt.set('toText', str(tl.to_enty))
            tl_elmt.set('type', tl.type)
            # the 'tail' is set so that each TLINK will start from a new line
            tl_elmt.tail = '\n'
            tags.append(tl_elmt)
            
        with open(b_gold_xml, 'w') as fp:
            fp.write(etree.tostring(root, xml_declaration=True).replace('/>', ' />'))
        
        
if __name__ == '__main__':
    #main_within()
    main_between()
    #main()