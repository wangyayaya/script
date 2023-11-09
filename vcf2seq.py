#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Function: Convert SNP data in VCF format to sequence (fasta/phylip)
# wang 20231108

import argparse
import sys


def generate_ambiguous_code(base1, base2):
    # 非纯和突变碱基的歧义码IUPAC Ambiguity Codes，类型没有vcf2phylip的多，但运行结果检查了一下和那个脚本是一样的，因为只考虑单碱基突变的话就只有下面这几种突变
    base1 = base1.upper()
    base2 = base2.upper()
    # 这里是获得的基因型，ATGC*.,"."是缺失的情况
    # 不考虑一个位点涉及多个碱基的情况
    if base1 == base2:
        if {base1} <= {"A", "T", "G", "C"}:
            return base1
        elif base1 == '.':
            return "-"
        elif base1 == '*':
            return 'N'
    elif base1 not in ["A", "T", "G", "C"] and base2 not in ["A", "T", "G", "C"]:
        return "N"
    elif {base1, base2} <= {"A", "C"}:
        return "M"
    elif {base1, base2} <= {"A", "G"}:
        return "R"
    elif {base1, base2} <= {"A", "T"}:
        return "W"
    elif {base1, base2} <= {"C", "G"}:
        return "S"
    elif {base1, base2} <= {"C", "T"}:
        return "Y"
    elif {base1, base2} <= {"G", "T"}:
        return "K"
    elif {base1, base2} <= {"A", "*"}:
        return "A"
    elif {base1, base2} <= {"T", "*"}:
        return "T"
    elif {base1, base2} <= {"G", "*"}:
        return "G"
    elif {base1, base2} <= {"C", "*"}:
        return "C"
    else:
        return "N"


def convert_vcf_to_seq(vcf_file, out_file, format, LF):
    if LF.upper().startswith("F"):
        LF = False
    else:
        LF = True
    # Open the input vcf file.
    with open(vcf_file) as vcf_file:
        lines = vcf_file.readlines()
    for line in lines:
        if line.startswith("#CHROM"):
            sample_name = line.strip().split()[9:]
            # print(sample_name)
            seqs = [""] * len(sample_name)
            # print(seqs)
        elif line.startswith("#"):
            pass
        elif line.strip():
            fields = line.strip().split()
            ref = fields[3]
            alleles = [ref] + fields[4].split(",")
            # print(alleles)
            # 这里只考虑每个位点只涉及单个碱基突变的情况，多个碱基突变的话就很难考虑那个歧义码。之前写的脚本是以最长那一个突变为准
            # 不考虑歧义码，其它缺失的用‘-’来补齐，如果同时考虑歧义码及多个碱基，没办法转换
            base_len_le_1 = True
            for base in alleles:
                base_len = len(base)
                if base_len > 1:
                    base_len_le_1 = False
                    break
            if base_len_le_1:
                for i, alleles_indices in enumerate(fields[9:], start=0):
                    # i是转化后sample_name列表中物种名的索引
                    if alleles_indices.split(":")[0]:
                        alleles_indices = alleles_indices.split(":")[0]
                        try:
                            if '/' in alleles_indices:
                                allele1 = alleles_indices.split('/')[0]
                                allele2 = alleles_indices.split('/')[1]
                            elif '|' in alleles_indices:
                                allele1 = alleles_indices.split('|')[0]
                                allele2 = alleles_indices.split('|')[1]
                            base1 = alleles[int(allele1)]
                            base2 = alleles[int(allele2)]
                        except ValueError:
                            base1 = base2 = '.'
                        # print(base1, base2)
                        base = generate_ambiguous_code(base1, base2)
                        # print(base)
                        seqs[i] += base
    # for i in range(len(sample_name)):
    #   print(f">{sample_name[i]}\n{seqs[i]}")

    if format == 'phylip':
        # phy序列不换行
        phylip_str = f"{len(sample_name)} {len(seqs[0])}\n"
        for i in range(len(sample_name)):
            phylip_str += f"{sample_name[i].ljust(10)} {seqs[i]}\n"
        out_str = phylip_str

    elif format == 'fasta' and LF:
        # fa格式60个字符换一行
        fasta_str_LF = ""
        for i in range(len(sample_name)):
            fasta_str_LF += f">{sample_name[i]}\n"
            seq = seqs[i]
            while len(seq) > 0:
                fasta_str_LF += seq[:60] + "\n"
                seq = seq[60:]  # 每一次删掉序列前60个碱基
        out_str = fasta_str_LF

    elif format == 'fasta' and not LF:
        # fa格式不换行
        fasta_str = ""
        for i in range(len(sample_name)):
            fasta_str += f">{sample_name[i]}\n{seqs[i]}\n"
        out_str = fasta_str

    with open(out_file, 'w') as f:
        f.writelines(out_str)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f'''Function: Convert SNP data in VCF format to sequence (fasta/phylip)
Example:  python {__file__} -i snp_filter_gatk.vcf -o snp_filter_gatk.fa -f fasta -LF F''')

    parser.add_argument("-i", type=str, dest='in_file', help="VCF file")
    parser.add_argument("-o", type=str, dest='out_file', help="out file")
    parser.add_argument("-LF", type=str, dest='line_feed', default="F",
                        help="if line feed for fasta format, default: F/False")
    parser.add_argument("-f", type=str, dest='format', default="fasta",
                        help="format of the output file (phylip/fasta), default: fasta")
    args = parser.parse_args()
    try:
        vcf_file = args.in_file
        out_file = args.out_file
        format = args.format
        LF = args.line_feed
        convert_vcf_to_seq(vcf_file, out_file, format, LF)
    except Exception:
        print(parser.description)
        print(parser.format_usage())
        sys.exit()
