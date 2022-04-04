cd dataset/test_train/$1
files=$(ls)
cd ../../..

outfile=stats/$1_stats.csv
echo 'Filename,Wrong Sectors,Accuracy' > $outfile

for file in $files; do
	filesize=$(wc -c "dataset/test_train/${1}/${file}" | awk '{print $1}')
	if [ $filesize -lt 2560 ]; then # require min of 5 sectors
		echo "- Skipping ${file} (too small)"
		continue
	fi
	
	echo "+ $file"
	echo -n "${file}," >> $outfile
	
	python3 fragment_file.py dataset/test_train/$1/$file fragmented/$file > /dev/null
	python3 recover_file.py fragmented/$file $1 localhost:8080 --csv >> $outfile
	
	rm fragmented/${file}_frag.dat
	rm fragmented/${file}_frag.json
done
