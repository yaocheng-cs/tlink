'''
Created on Aug 7, 2012

@author: yaocheng
'''

import sys

vector = '/Users/yaocheng/Desktop/i2b2/xml_eval_output/within-0.vector.txt'

def feature(src_path):
    try:
        with open(src_path, 'r') as src:
            instances = []
            for line in src:
                if line[0:6] == 'name: ':
                    inst = {}
                    inst['ID'] = line[6:-1]
                    continue
                if line[0:8] == 'target: ':
                    inst['label'] = line[8:-1]
                    continue
                if line == '\n':
                    instances.append(inst)
                    continue
                if line[0:7] == 'input: ':
                    content = line[7:-1]
                else:
                    content = line[:-1]
                i1 = content.find('=')
                i2 = content.rfind('(')
                i3 = content.rfind('=')
                ft = content[0:i1]
                fv = content[i1+1:i2]
                val = content[i3+1:-2]
                if ',' in fv or '%' in fv or '"' in fv or "'" in fv or '=' in fv:
                    continue
                else:
                    inst[ft + '=' + fv] = val
            
            features = []    
            for inst in instances:
                for feat in inst.keys():
                    if feat not in features and feat not in ['ID', 'label']:
                        features.append(feat)
            
            return features
    except IOError:
        print 'Abort: source file or destination file could not be opend or created'
        return
    
def instance_id(src_path):
    try:
        with open(src_path, 'r') as src:
            instances = []
            for line in src:
                if line[0:6] == 'name: ':
                    inst = {}
                    inst['ID'] = line[6:-1]
                    continue
                if line[0:8] == 'target: ':
                    inst['label'] = line[8:-1]
                    continue
                if line == '\n':
                    instances.append(inst)
                    continue
                if line[0:7] == 'input: ':
                    content = line[7:-1]
                else:
                    content = line[:-1]
                i1 = content.find('=')
                i2 = content.rfind('(')
                i3 = content.rfind('=')
                ft = content[0:i1]
                fv = content[i1+1:i2]
                val = content[i3+1:-2]
                if ',' in fv or '%' in fv or '"' in fv or "'" in fv or '=' in fv:
                    continue
                else:
                    inst[ft + '=' + fv] = val
        return [inst['ID'] for inst in instances]
    except IOError:
        print 'Abort: source file or destination file could not be opend or created'
        return
    

def convert(src_path, des_path, features=None):
    try:
        with open(src_path, 'r') as src:
            with open(des_path, 'w') as des:
                instances = []
                for line in src:
                    if line[0:6] == 'name: ':
                        inst = {}
                        inst['ID'] = line[6:-1]
                        continue
                    if line[0:8] == 'target: ':
                        inst['label'] = line[8:-1]
                        continue
                    if line == '\n':
                        instances.append(inst)
                        continue
                    if line[0:7] == 'input: ':
                        content = line[7:-1]
                    else:
                        content = line[:-1]
                    i1 = content.find('=')
                    i2 = content.rfind('(')
                    i3 = content.rfind('=')
                    ft = content[0:i1]
                    fv = content[i1+1:i2]
                    val = content[i3+1:-2]
                    if ',' in fv or '%' in fv or '"' in fv or "'" in fv or '=' in fv:
                        continue
                    else:
                        inst[ft + '=' + fv] = val
                
                if not features:
                    features = []    
                    for inst in instances:
                        for feat in inst.keys():
                            if feat not in features and feat not in ['ID', 'label']:
                                features.append(feat)
                            
                des.write('@relation temporal-weka.filters.unsupervised.attribute.AddID-Cfirst-NID\n\n')
                
                #des.write('@attribute ID string\n')
                for feat in features:
                    line = ' '.join(['@attribute', feat, 'numeric']) + '\n'
                    des.write(line)
                des.write('@attribute label {<null>}\n\n')
                
                des.write('@data\n')
                for inst in instances:
                    #line = inst['ID'] + ','
                    line = ''
                    keys = inst.keys()
                    for feat in features:
                        if feat in keys:
                            val = inst[feat]
                        else:
                            val = '0'
                        line = line + val + ','
                    line = line + inst['label'] + '\n'
                    des.write(line)
        return
    except IOError:
        print 'Abort: source file or destination file could not be opend or created'
        return
    
def main():
    #features = feature(sys.argv[3])
    #convert(sys.argv[1], sys.argv[2], features)
    instance_id()
    return

if __name__ == '__main__':
    main()