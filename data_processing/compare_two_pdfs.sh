file1=`pwd`"/"$1
file2=`pwd`"/"$2
logfile=`pwd`"/"$3
cd pdfc-sdk-22.10.225/i-net\ PDFC
bash compare.sh -e -logmaxerror 1000000 -logfile $logfile $file1 $file2
