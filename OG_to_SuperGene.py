import sys
import os

from Bio import SeqIO

args = sys.argv

if len(args) < 2:
    print(f'Function: Coalescence to Concatenation')
    print(f'Usage: python3 {args[0]} gene_list_path(path/sp%n.txt) OG_path(path/OG%n) >out')
    exit()

gene_list_path = args[1]
OG_path = args[2]


def get_infile_list(in_path):
    """根据目录获取文件中所有文件，返回一个列表"""
    file_list = [f for f in os.listdir(in_path) if f != '']
    return [os.path.join(in_path, infile) for infile in file_list]


def get_super_gene(gene_list_path, OG_path):
    """将比对后的每个OG串联为super gene， 为确保每个物种序列长度一致，当某个OG中物种覆盖率不是100%时，
    用’-‘*seq_length作为缺失物种的序列。输入参数为物种基因list目录，以及序列比对后的OG目录（文件为fasta格式），
    将物种基因list目录下文件名作为串联后序列名称"""

    OG_list = get_infile_list(OG_path)
    sp_list = get_infile_list(gene_list_path)

    for sp_path in sp_list:
        sp = os.path.splitext(os.path.split(sp_path)[1])[0]
        gene_list = []
        with open(sp_path, 'r') as f:
            for geneid in f.readlines():
                geneid = geneid.strip()
                gene_list.append(geneid)

        sp_seq = ''
        for OG in OG_list:
            seq_tmp = ''
            # id_in_genelist = False
            for line in SeqIO.parse(OG, 'fasta'):
                gene_id = line.id
                # print(id)
                seq = line.seq
                seq_len = len(seq)
                # while not id_in_genelist:
                if gene_id in gene_list:
                    seq_tmp = seq
                    # id_in_genelist = True
                    break
                else:
                    seq_tmp = '-' * seq_len
                    # break
            sp_seq += seq_tmp
        print(f'>{sp}\n{sp_seq}')

if __name__ == '__main__':
    get_super_gene(gene_list_path, OG_path)
