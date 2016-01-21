import os
import utility.utility as utility
from project_path import project_base
from project_path import berkeleyParser_jar, berkeleyParser_gr

def clean():
    src_folder = os.path.join(project_base, 'full_txt')
    trgt_folder = os.path.join(project_base, utility.extend_name('full_txt', 'cleaned'))
    if not os.path.exists(trgt_folder):
        os.mkdir(trgt_folder)
    src_names = os.listdir(src_folder)

    for src_name in src_names:
        trgt_name = utility.extend_name(src_name, 'cleaned', '.')
        src_path = os.path.join(src_folder, src_name)
        trgt_path = os.path.join(trgt_folder, trgt_name)
        with open(src_path, 'r') as in_fp, open(trgt_path, 'w') as out_fp:
            buf = in_fp.read()
            buf = utility.replace_xml_predefined_char(buf)
            out_fp.write(buf)

def parse():
    src_folder = os.path.join(project_base, 'full_txt_cleaned')
    trgt_folder = os.path.join(project_base, utility.extend_name('full_txt_cleaned', 'parsed'))
    if not os.path.exists(trgt_folder):
        os.mkdir(trgt_folder)
    src_names = os.listdir(src_folder)

    for src_name in src_names:
        trgt_name = utility.extend_name(src_name, 'parsed', '.')
        src_path = os.path.join(src_folder, src_name)
        trgt_path = os.path.join(trgt_folder, trgt_name)
        cmd = 'java -Xmx1g -jar ' + berkeleyParser_jar + \
              ' -gr ' + berkeleyParser_gr + \
              ' -inputFile ' + src_path + \
              ' -outputFile ' + trgt_path
        os.system(cmd)


if __name__ == '__main__':
    #clean()
    parse()