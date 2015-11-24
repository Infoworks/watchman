#!/bin/bash
set -x
set -e
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
data_dir="/tmp/sftp_webtrends_files/"

#Create the data files
rm -rf "$data_dir"
mkdir "$data_dir"
cd "$data_dir"
scala "$script_dir/DataCreator.scala" 2015 01 - 10000

#Create Hive schema
hive -f "$script_dir/hive.sql"
