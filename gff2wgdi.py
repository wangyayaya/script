#! /bin/python
# -*- coding:UTF-8 -*-
# Function: Process the gff file into the format required by WGDI
# Wang 2023.1.11

import sys
import getopt

Usage = '''
        Usage:
        -h or --help :   Get usage
        -p or --prefix : The prefix of the output file (str, required!)
        -g or --gff :    gff file (file, required!)
        -t or --type :   Which line in the gff file is used as the extract (gene/mRNA/..., default: gene)
        -k or --key :    Which feature in the gff file is used as the gene id (ID/Name/Parent/..., default: ID)
        Example: python script.py -p Csinensis -g Camellia_sinensis.gff -t gene -k ID
        
        Note: The chromosome length is roughly calculated according to the gff file, not the exact length,
        but it has no effect on the result.
        '''


def parameters_get():
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   '-h,-p:-g:-t:-k:',
                                   ['help', 'prefix=', 'gff=', 'type=', 'keyword='])
        if not opts:
            print(Usage)
            sys.exit()
        for opt_name, opt_value in opts:
            if opt_name in ('-h', '--help'):
                print(Usage)
                sys.exit()
            if opt_name in ('-p', '--prefix'):
                parameters['prefix'] = opt_value
            if opt_name in ('-g', '--gff'):
                parameters['gff'] = opt_value
            if opt_name in ('-t', '--type'):
                parameters['type'] = opt_value
            if opt_name in ('-k', '--keyword'):
                parameters['keyword'] = opt_value

    except getopt.GetoptError:
        print('        Error: Incorrect input parameters' + Usage)
        sys.exit()


if __name__ == "__main__":
    parameters = {}
    parameters_get()
    if 'prefix' not in parameters:
        print("Error: The prefix must be specified!")
        sys.exit()
    if 'gff' not in parameters:
        print("Error: The gff file must be specified!")
        sys.exit()
    if 'type' not in parameters:
        parameters['type'] = "gene"
    if 'keyword' not in parameters:
        parameters['keyword'] = "ID"

p = parameters['prefix']
gff = parameters['gff']
extract_type = parameters['type']
keyword = parameters['keyword']

len_file = open(f'{p}.len', 'w')
gff_file = open(f'{p}.gff', 'w')

chr_list = []
file = open(gff, 'r')
for line in file.readlines():
    if not line.startswith('#'):
        line = line.split("\t")
        chr_id = line[0]
        chr_list.append(chr_id)
chr_list = sorted(set(chr_list), key=chr_list.index)


for chr_id in chr_list:
    gene_number = 0
    chr_len = 0
    file = open(gff, 'r')
    for line in file.readlines():
        if not line.startswith('#'):
            line = line.split()
            if line[2] == extract_type and line[0] == chr_id:
                gene_name = line[8].split(f'{keyword}=')[1].split(';')[0]
                old_name = line[8].split(';')[1].split("=")[1]
                start = eval(line[3])
                end = eval(line[4])
                gene_number += 1
                strand = line[6]
                if end > chr_len:
                    chr_len = end
                print(f'{chr_id}\t{gene_name}\t{start}\t{end}\t{strand}\t{gene_number}\t{old_name}', file=gff_file)
    print(f'{chr_id}\t{chr_len}\t{gene_number}', file=len_file)
