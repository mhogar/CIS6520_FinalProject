entry=$(ifind -f fat32 -n $2 $1)
if echo $entry | grep -q "not found"; then
	echo "File not found"
	exit 0
fi

sectors=$(istat -f fat32 $1 $entry | grep -A 1000 "Sectors:" | tail -n +2)

mkdir -p $3

i=-1
for sector in $sectors; do
	((i=i+1))
	if [ $sector == "0" ]; then continue; fi

	filename="${3}/${2}_${i}.dat"
	echo "${sector} -> ${filename}"
	blkcat -f fat32 $1 $sector > $filename
done
