#!/bin/bash
i2cset -y 0 0x45 0x4c 0x00
i2cset -y 0 0x45 0x54 0x00
i2cset -y 0 0x45 0x5c 0x00

exit 0
