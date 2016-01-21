'''
Created on Jul 31, 2012

@author: yaocheng
'''

import os
import re
from collections import defaultdict

class Instance(object):

    # leave id as "" to generate numeric ids for instance names
    # or pass in an id (e.g., tlink.ds_id)
    # meta is optional string of information to be stored with the instance that will
    # not affect mallet processing (ie. for storing notes about the instance).
    def __init__(self, id_='', label=None):
        self.id_ = id_
        self.label = label
        self.feats = []
        # meta data string used to capture info for future debugging
        # e.g., the sentence, event strings, etc.
        # self.meta = meta

    # add a feature to the mallet instance.
    # Each feature is composed of a name and value
    # This way we can post-filter features by name to test different feature sets
    def add_feat(self, feat, allow_dup=False):
        if not allow_dup:
            if feat in self.feats:
                return
        self.feats.append(feat)

    def to_str(self):
        if self.label:
            return self.label + ' ' + ' '.join(self.feats)
        else:
            return ' '.join(self.feats)
    
    def __str__(self):
        if self.label:
            return self.id_ + ' ' + self.label + ' ' + ' '.join(self.feats)
        else:
            return self.id_ + ' ' + ' '.join(self.feats)
        
        
class Config(object):
    
    def __init__(self, binary_dir, output_dir, output_base='example'):
        self.binary_dir = binary_dir
        self._output_dir = output_dir
        self._output_base = output_base
        self.multi_model = False
        self._update_config()
        
    @property
    def output_dir(self):
        return self._output_dir
        
    @output_dir.setter
    def output_dir(self, val):
        self._output_dir = val
        self._update_config()
        
    @property
    def output_base(self):
        return self._output_base
        
    @output_base.setter
    def output_base(self, val):
        self._output_base = val
        self._update_config()
        
    def _update_config(self):
        _output_path = os.path.join(self._output_dir, self._output_base)
        self.mallet_path = _output_path + '.mallet'
        self.vector_path = _output_path + '.vector'
        self.pruned_vector_path = _output_path + '.pruned.vector'
        self.vector_txt_path = _output_path + '.vector.txt'
        self.model_path = _output_path + '.model'
        self.output_path = _output_path + '.output'
        self.stdout_path = _output_path + '.stdout'
        self.stderr_path = _output_path + '.stderr'
        
        
class Run(object):
    
    def __init__(self, config, instances):
        self.cfg = config
        self.instances = instances
        
    # write instance (<id> <label> <feature1> <feature2> ...) to a mallet file
    def write_mallet(self):
        with open(self.cfg.mallet_path, 'w') as fp:
            for inst in self.instances:
                fp.write(str(inst) + '\n')
        return
    
    
class Training(Run):

    def __init__(self, config, instances):
        super(Training, self).__init__(config, instances)
        
    def write_vector(self):
        cmd = os.path.join(self.cfg.binary_dir, 'csv2vectors') + \
            ' --token-regex "[^ ]+"' + \
            ' --input ' + self.cfg.mallet_path + \
            ' --output ' + self.cfg.vector_path + \
            ' --print-output TRUE > ' + self.cfg.vector_txt_path
        print '[write_vector_file] cmd: %(cmd)s' % {'cmd': cmd}
        os.system(cmd)
        return
        
    def prune_vector(self):
        cmd = os.path.join(self.cfg.binary_dir, 'vectors2vectors') + \
            ' --input ' + self.cfg.vector_path + \
            ' --output ' + self.cfg.pruned_vector_path + \
            ' --prune-infogain 2000'
        print '[prune_vector] cmd: %(cmd)s' % {'cmd': cmd}
        os.system(cmd)
        self.cfg.vector_path = self.cfg.pruned_vector_path
        return
    
    # train a mallet classifier
    # trainer is the case-sensitive name for a mallet classifier (e.g., "MaxEnt", "NaiveBayes")
    # To divide training data into a training and evaluation set, set training_portion to a value
    # between 0 and 1, (e.g., .7)
    # To do cross validation, set number_cross_val to some number >= 2 (e.g., 10)
    # To use all instances to train a classifier, leave both parameters empty (i.e., = 0)
    # Model will be in $train_path_prefix.<trainer>.model
    # Output (accuracy, confusion matrix, label predicted/actual) is in $train_path_prefix.<trainer>.out
    # Command line format: vectors2train --training-file train.vectors --trainer  MaxEnt --output-classifier foo_model --report train:accuracy train:confusion> foo.stdout 2>foo.stderr
    def train(self, MLA, cross=None, portion=None):
        #cmd = self.cfg.mallet_dir + '/' + 'mallet train-classifier' + \
        cmd = os.path.join(self.cfg.binary_dir, 'vectors2classify') + \
            ' --input ' + self.cfg.vector_path + \
            ' --trainer ' + MLA + \
            ' --output-classifier ' + self.cfg.model_path + \
            ' --report test:accuracy test:confusion test:raw > ' + self.cfg.output_path
        if cross >= 2:
            # use cross validation will cause multiple training process, and part of the data being used as testing portion
            cmd += ' --cross-validation ' + str(cross)
        if portion > 0.0 and portion < 1.0:
            # part of the data used as testing portion
            cmd += ' --training-portion ' + str(portion)
        #cmd += ' 1> ' + self.stdout_path # standard output will be directed to the path specified in --report option
        cmd += ' 2> ' + self.cfg.stderr_path
        
        print '[train_classifier] cmd: %(cmd)s' % {'cmd': cmd}
        os.system(cmd)
        return
        
        '''
        # --report test:raw option provides <id> <actual> <predicted> labels, e.g.
        # 2 OUT OUT:0.6415563874015857 IN:0.3584436125984143 
        
        if cross >= 2:
            cmd = self.cfg.mallet_dir + '/' + 'mallet train-classifier' + \
                ' --input ' + self.vect_path + \
                ' --trainer ' + MLA + \
                ' --output-classifier ' + self.model_path + \
                ' --cross-validation ' + str(cross) + \
                ' --report test:accuracy test:confusion test:raw > ' + self.output_path + \
                ' 1> ' + stdout_path + \
                ' 2> ' + stderr_path
        elif portion > 0.0 and portion < 1.0:
            cmd = self.cfg.mallet_dir + '/' + 'mallet train-classifier' + \
                ' --input ' + self.vect_path + \
                ' --trainer ' + MLA + \
                ' --output-classifier ' + self.model_path + \
                ' --training-portion ' + str(portion) + \
                ' --report test:accuracy test:confusion train:raw > ' + self.output_path + \
                ' 1> ' + stdout_path + \
                ' 2> ' + stderr_path
        else:
            cmd = self.cfg.mallet_dir + '/' + 'mallet train-classifier' + \
                ' --input ' + self.vect_path + \
                ' --trainer ' + MLA + \
                ' --output-classifier ' + self.model_path + \
                ' --report test:accuracy test:confusion test:raw > ' + self.output_path + \
                ' 1> ' + stdout_path + \
                ' 2> ' + stderr_path
        '''
        
        
class Testing(Run):
    
    def __init__(self, config, instances, training_cfg=None):
        super(Testing, self).__init__(config, instances)
        if training_cfg:
            # testing needs training data vector (containing "pipeline") to generate testing data vector
            self._training_vector_path = training_cfg.vector_path
            if training_cfg.multi_model:
                self.cfg.model_path = training_cfg.model_path + '.trial0'
            else:
                self.cfg.model_path = training_cfg.model_path
        # if no traning_cfg is passed in, then model (and training data vector) needs to be set directly
            
    def set_training_vector(self, val):
        self._training_vector_path = val
        
    # testing can use mallet file directly, so this method is not "absolutely" necessary
    # if called before testing, the vector txt file will be over-written, as the dummy label
    # will be substituted by <null>
    def write_vector(self):
        cmd = os.path.join(self.cfg.binary_dir, 'csv2vectors') + \
            ' --token-regex "[^ ]+"' + \
            ' --input ' + self.cfg.mallet_path + \
            ' --use-pipe-from ' + self._training_vector_path + \
            ' --output ' + self.cfg.vector_path + \
            ' --print-output TRUE > ' + self.cfg.vector_txt_path
        print '[write_vectors_file] cmd: %(cmd)s' % {'cmd': cmd}
        os.system(cmd)
        return
    
    def set_model(self, val):
        self.cfg.model_path = val
        
    def test(self):
        """
        testing can directly use mallet file as input
        """
        #cmd = self.cfg.binary_dir + '/' + 'mallet classify-file' + \
        cmd = os.path.join(self.cfg.binary_dir, 'csv2classify') + \
            ' --input ' + self.cfg.mallet_path + \
            ' --classifier ' + self.cfg.model_path + \
            ' --output ' + self.cfg.output_path
        cmd += ' 1> ' + self.cfg.vector_txt_path # standard output will record content of the vector file in human-readable format
        cmd += ' 2> ' + self.cfg.stderr_path
        
        print '[classify] cmd: %(cmd)s' % {'cmd': cmd}
        os.system(cmd)
        return
    
    def train_test(self):
        """
        due to feature selection, have to train again on vector file, then test on another vector file,
        so before this, call to "write_vector" becomes necessary
        """
        return
    
    
class Inspector(object):
    
    def __init__(self, config):
        
        """
        Use Inspector object to get the ID, label or feats of interested instances
        Then go back to Dataset or Document, use ID to retrieve the actualy object under inspection
        """
        self.cfg = config
        
        # if the testing data is truly unlabelled, then values in this dictionay
        # will be "dummy" values, such as '<null>', or could be any other string
        self.ID2actual = {}
        self.ID2pred = {}
        self.ID2label_pair = {}
        self.label_pair2ID = defaultdict(list)
        self.ID2feats = {}
        self.feat2ID = defaultdict(list)
        
        self._load_mallet()
        self._load_output()
    
    def _load_mallet(self):
        with open(self.cfg.mallet_path, 'r') as fp:
            for line in fp:
                line = line.strip()
                line_fields = line.split()
                ID = line_fields[0]
                actual = line_fields[1]
                feats = line_fields[2:]
                self.ID2actual[ID] = actual
                self.ID2feats[ID] = feats
    
                for feat in feats:
                    self.feat2ID[feat].append(ID)
        return
    
    def _load_output(self):
        pass
    
    def get_tlink_of_label_pair(self, actual, pred):
        try:
            return self.label_pair2ID[actual + '_' + pred]
        except KeyError:
            return None
    
    def get_tlink_with_feature(self, feat):
        try:
            return self.feat2ID[feat]
        except KeyError:
            return None
    
    
class TrainingInspector(Inspector):
    
    def __init__(self, config):
        super(TrainingInspector, self).__init__(config)
        
    def _load_output(self):
        """
        this need to me examined to make sure that inspection of cross-validation result is viable
        """
        #if not self.inspecting_run.testing_portion:
        #    print 'No testing portion available in the training process, so nothing to inspect'
        #    return None
        
        # extract Trial 0 raw data from the .output file
        in_trial0_rslt = False

        # process the .output file for label information (output of report test:raw option)
        # NOTE: in the case of cross validation folds, this will only capture the Trial 0 result
        with open(self.cfg.output_path, 'r') as fp:
            for line in fp:
                if in_trial0_rslt:
                    m = re.match('^(?P<ID>[^ ]+) (?P<actual_label>[^ ]+) (?P<pred_label>[^ ]+):', line)
                    if m:
                        ID = m.group('ID')
                        actual = m.group('actual_label')
                        pred = m.group('pred_label')
                        self.ID2pred[ID] = pred
                        self.ID2label_pair[ID] = [actual, pred]
                    else:
                        in_trial0_rslt = False
                        break
                if line == ' Raw Testing Data\n':
                    in_trial0_rslt = True
        
        for ID in self.ID2label_pair.keys():
            actual, pred = self.ID2label_pair[ID]
            label_pair = actual + '_' + pred
            self.label_pair2ID[label_pair].append(ID)
            
        return
    
    
class TestingInspector(Inspector):
    
    def __init__(self, config):
        self.ID2probs = defaultdict(dict)
        super(TestingInspector, self).__init__(config)
    
    def _load_output(self):
        with open(self.cfg.output_path, 'r') as fp:
            for line in fp:
                buf = line.split('\t')
                ID = buf[0]
                labels = buf[1::2]
                probs = [float(p) for p in buf[2::2]]
                pred = labels[probs.index(max(probs))]
                self.ID2pred[ID] = pred
                for i in range(3):
                    self.ID2probs[ID][labels[i]] = probs[i]
                # this "actual" will be a dummy value if testing data is truly unlabelled
                actual = self.ID2actual[ID]
                self.ID2label_pair[ID] = [actual, pred]
                
        for ID in self.ID2label_pair.keys():
            actual, pred = self.ID2label_pair[ID]
            label_pair = actual + '_' + pred
            self.label_pair2ID[label_pair].append(ID)
            
        return
        