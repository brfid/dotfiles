#!/bin/bash
ps -e --no-headers -o comm | grep -vc "^\["
