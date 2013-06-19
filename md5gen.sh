#!/bin/sh
cd $1;find . -type f | while read line;do md5sum $line;done > md5sums
md5sum md5sums > master.md5
