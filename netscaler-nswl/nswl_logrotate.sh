#!/bin/sh

###
# Title: Logrotate for NSWL Logs
# Version: 0.1
# Last Update: 2023-02-24
# Description: This is a helper for log rotation of the NSWL utility
#              Schedulation should be achived with cron
# Author: Emil Pandocchi
# Notes: logs from NSWL are not compatible with logrotate.d
###

# Variables
NSWL_LOG_FOLDER="/opt/NSweblog"
NSWL_ARCHIVE_FOLDER="/opt/NSweblog-archive"
DAYS_TO_KEEP=30

## Execution

# Compress every file not created today (from midnight)
# Extensions for NSWL log files can be: .log, .log.0, .log.1, etc...
find "$NSWL_LOG_FOLDER" -regex ".*\.log\.?.?.?" -type f -daystart -mtime +0 -exec gzip {} \;

# Move compressed file to the archive folder
find "$NSWL_LOG_FOLDER" -name "*.gz" -type f -exec mv -t "$NSWL_ARCHIVE_FOLDER" {} \;

# Remove every file older than 30days
find "$NSWL_LOG_FOLDER" -name "*" -type f -daystart -mtime +"$DAYS_TO_KEEP" -exec rm -f {} \;
find "$NSWL_ARCHIVE_FOLDER" -name "*" -type f -daystart -mtime +"$DAYS_TO_KEEP" -exec rm -f {} \;
