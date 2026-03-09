#!/bin/bash
awk '{printf "%.0fC", $1/1000}' /sys/class/thermal/thermal_zone0/temp
