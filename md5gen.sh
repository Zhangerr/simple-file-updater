#!/bin/sh
cd $1;rm master.md5 md5sums;find . -type f | while read line;do md5sum $line;done > md5sums
md5sum md5sums > master.md5
