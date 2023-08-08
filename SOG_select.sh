#!/bin/bash

#筛选orthofinder直系同源单拷贝基因，需要orthofinder跑出来的Orthogroup_Sequences目录，以及一个包含所有物种名的txt文件，该文件中的命名应与基因id匹配，能够通过物种名将该物种基因匹配出来，如物种名CSS，基因名CSS001、CSS002……

if [ $# -lt 4 ];then
	echo -e "
	筛选orthofinder直系同源单拷贝基因，需要orthofinder跑出来的Orthogroup_Sequences目录，以及一个包含所有物种名的txt文件，该文件中>的命名应与基因id匹配，能够通过物种名将该物种基因匹配出来，如物种名CSS，基因名CSS001、CSS002……
	Usage:$0 <Orthogroup_Sequences: othofinder result> <cover:float> <sample.txt: txt include all species name> <out_path>";
	exit;
fi




Orthogroup_Sequences=`realpath $1`
cover=$2
sample=`realpath $3`
out_path=`realpath $4`

[ ! -d ${out_path} ] && mkdir ${out_path}

cd ${out_path}/

[ ! -d Select_Result ] && mkdir -p Select_Result/00_Orthogroup_id Select_Result/01_Single_Copy_Orthogroup_id

run_SOG() {
	for i in `ls ${Orthogroup_Sequences}`;do
		touch tmp.txt
		grep '>' ${Orthogroup_Sequences}/$i |sed 's/>//g'>Select_Result/00_Orthogroup_id/$i
		for j in `cat ${sample}`;do
			n=`grep -E "^$j" Select_Result/00_Orthogroup_id/$i|wc -l|awk '{print $1}'`
			if [ $n -gt 1 ];then
				perl -i -p -e 's/\n/|/' ${out_path}/tmp.txt
				echo $j >> ${out_path}/tmp.txt
			fi
		done
		z=`cat ${out_path}/tmp.txt|head -n 1`
		grep -vE "^$z" Select_Result/00_Orthogroup_id/$i >Select_Result/01_Single_Copy_Orthogroup_id/$i
		rm -f tmp.txt

		n=`wc -l Select_Result/01_Single_Copy_Orthogroup_id/$i |awk '{print $1}'`
		if [ $n -eq 0 ];then
			rm -f Select_Result/01_Single_Copy_Orthogroup_id/$i
		fi
	done
}

directory="Select_Result/01_Single_Copy_Orthogroup_id"
if [ -z "$(find "$directory" -mindepth 1 -maxdepth 1)" ]; then
    run_SOG
else
    echo "单拷贝基因筛选之前已完成，现在筛选物种覆盖率的OG，如果筛选到的OG不全，请删除${directory}下全部文件重新运行此脚本"
fi

species_number=`wc -l ${sample}|awk '{print $1}'`
gene_number=`echo ${species_number}*${cover}|bc`
cd ${out_path}/Select_Result
[ ! -d 02_OG_cover_${cover} ] && mkdir 02_OG_cover_${cover}
for i in `ls 01_Single_Copy_Orthogroup_id`;do
	n=`wc -l 01_Single_Copy_Orthogroup_id/$i|awk '{print $1}'`
	a=`echo "$n >= ${gene_number}"|bc`
	if [ $a -eq 1 ];then
		cp 01_Single_Copy_Orthogroup_id/$i 02_OG_cover_${cover}/$i
	fi
done
