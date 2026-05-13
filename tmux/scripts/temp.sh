#!/bin/bash
awk '{printf "%.0f°C", $1/1000}' /sys/class/thermal/thermal_zone0/temp
