# genebank to fasta and split
import Bio
from Bio import SeqIO
import sys
import os

if len(sys.argv) < 3:
    print(f'Usage: python {__file__} gb_file out_path')
    sys.exit()

gb_file = sys.argv[1]
output_path = sys.argv[2]



if not os.path.exists(output_path):
    os.makedirs(output_path)

for reco in Bio.SeqIO.parse(gb_file, 'genbank'):
    # print(reco.annotations)
    sp = reco.annotations['accessions'][0] + '_' + reco.annotations['organism'].replace(' ', '_')
    with open(f'{output_path}/{sp}', 'w') as f:
        for feature in reco.features:
            if feature.type == 'CDS' and 'gene' in feature.qualifiers:
                try:
                    id = feature.qualifiers['gene'][0]
                    seq = feature.qualifiers['translation'][0]
                    print(f'>{id}', file=f)
                    print(seq, file=f)
                except KeyError:
                    pass

