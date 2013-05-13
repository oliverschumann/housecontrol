#!/bin/bash
outdoor=$(head -n 1 /home/pi/housecontrol/settings/outdoorTemp.txt | sed -e 's/,/./g')
echo $outdoor
exit 0