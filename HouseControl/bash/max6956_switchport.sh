#!/bin/bash
sudo i2cset -y 0 0x45 $1 $2
exit 0