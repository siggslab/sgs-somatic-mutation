#!/bin/bash -
#===============================================================================
#
#          FILE: test.sh
#
#         USAGE: ./test.sh
#
#   DESCRIPTION: 
#
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 04/21/22 00:13:46
#      REVISION:  ---
#===============================================================================

set -o nounset                                  # Treat unset variables as an error
echo "========"
echo $1
ls -lh $1
echo "========"
echo $2
ls -lh $2

echo "testBucket_mount11.log"
cat $1/z_qiao-hail/testBucket_mount11.log

echo "done"


