'''
Created on Jan 23, 2013

@author: yaocheng
'''

from mallet import *

def objs2insts(objs, get_id, get_label, feats):
    insts = []
    for obj in objs:
        inst = Instance(get_id(obj), get_label(obj))
        for f in feats:
            fn = f.func_name
            v = f(obj)
            if v and v != []:
                if isinstance(v, list):
                    for i in v:
                        inst.add_feat(fn + '=' + str(i))
                else:
                    inst.add_feat(fn + '=' + str(v))
        insts.append(inst)
    return insts

def train_on_data(data, get_id, get_label, feats, MLA, mallet_cfg):
    training = Training(mallet_cfg, objs2insts(data, get_id, get_label, feats))
    training.write_mallet()
    training.write_vector()
    training.train(MLA)
    return mallet_cfg

def apply_to_data(data, get_id, feats, ML_model, mallet_cfg):
    testing = Testing(mallet_cfg, objs2insts(data, get_id, lambda x: 'dummy', feats))
    testing.set_model(ML_model)
    testing.write_mallet()
    testing.test()
    ti = TestingInspector(mallet_cfg)
    return ti