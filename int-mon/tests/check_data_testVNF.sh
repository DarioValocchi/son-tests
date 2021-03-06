#!/bin/bash

tw_end=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
tw_start=$(date -u -d -10minutes '+%Y-%m-%dT%H:%M:%SZ')
resp=$(curl -s \
-H "Accept: application/json" \
-H "Content-Type:application/json" \
-X POST --data '{"name":"vm_mem_perc","start": "'$tw_start'", "end": "'$tw_end'", "step": "10s", "labels": [{"labeltag":"exported_job", "labelid":"vnf"}]}' "http://sp.int3.sonata-nfv.eu:8000/api/v1/prometheus/metrics/data" )

job=$(echo $resp | python -mjson.tool | grep "exported_job")

instance=$(echo $resp | python -mjson.tool | grep "exported_instance")

if [[ $job =~ .*vnf.* ]]
then
	if [[ $instance =~ .*TEST-VNF.* ]]
	then
	   echo "Success: TEST VNF(VM) FOUND!"
	else
	   echo "Error: TEST VNF(VM) NOT FOUND"
	   exit -1
	fi    
else
   echo "Error: No monitoring data for vnfs!!"
   exit -1
fi
