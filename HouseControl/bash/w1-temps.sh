#!/bin/bash
sleep 1

#SENSOR_TEMPERATURE_HEATING = "10-000801244d84"
#SENSOR_TEMPERATURE_WATER = "10-00080119602a"
#SENSOR_TEMPERATURE_INDOOR = "10-000801246971"
#SENSOR_TEMPERATURE_GROUNDFLOOR_FLOW = "10-00080123a0ff"
#SENSOR_TEMPERATURE_GROUNDFLOOR_RETURN = "10-00080123a848"
#SENSOR_TEMPERATURE_UPPERFLOOR_FLOW = "10-00080123d4a1"
#SENSOR_TEMPERATURE_UPPERFLOOR_RETURN = "10-000801248e98"
#SENSOR_TEMPERATURE_OUTDOOR = "OutdoorWeb"

outdoor=$(head -n 1 /home/pi/housecontrol/settings/outdoorTemp.txt | sed -e 's/,/./g')
#sensors=$(cat /sys/bus/w1/devices/w1_bus_master1/w1_master_slaves)
sensors=( 10-000801244d84 10-00080119602a 10-000801246971 10-00080123a0ff 10-00080123a848 10-00080123d4a1 10-000801248e98 );
while [ true ]
do
out="";
for item in ${sensors[*]}
do
	crc="no"
	temp=""
	while [ "$crc" = "no" ];
	do
		sensor_output=$(cat /sys/bus/w1/devices/$item/w1_slave);
		temp[$pos]=$(echo $sensor_output | grep --regexp=crc=[[:xdigit:]][[:xdigit:]][[:space:]]YES);
		if [ "$temp" != "" ] 
		then
			crc="Y";
			out=$out','$(echo $sensor_output | grep t= | cut -f3 -d= | awk '{print $1/1000}');
		fi
	done
done

echo $(date +'%Y%m%d%H%M%S')$out,$outdoor
#echo $(date +'%Y%m%d%H%M%S')$out,$outdoor > /home/pi/housecontrol/settings/currenttemps.txt
done

exit 0