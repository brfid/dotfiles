#!/bin/bash
free -h | awk '/^Swap:/{print $3"/"$2}'
