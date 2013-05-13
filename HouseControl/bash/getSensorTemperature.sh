#!/bin/bash
#sensors=$(cat /sys/bus/w1/devices/w1_bus_master1/w1_master_slaves)
#sensors=( 10-00080123d4a1 10-000801248e98 10-00080119602a 10-000801244d84 10-00080123a0ff 10-00080123a848 10-000801246971 );
item=$1
sleep 0.5
out="0"
retry=5
crc="no"
temp=""
while [ "$crc" = "no" ];
do
	sensor_output=$(cat /sys/bus/w1/devices/$item/w1_slave);
	temp=$(echo $sensor_output | grep --regexp=crc=[[:xdigit:]][[:xdigit:]][[:space:]]YES);
	
	if [ "$temp" != "" ] 
	then
		crc="Y";
		out=$(echo $sensor_output | grep t= | cut -f3 -d= | awk '{print $1/1000}');
	fi

	retry=$(($retry-1))

	if [ $retry -eq 0 ]
	then
		break
	fi
done

echo $out
exit 0