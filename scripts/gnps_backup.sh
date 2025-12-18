#!/bin/bash

# Define source and destination directories
SOURCE1="/data/nf_data/server/db_dump"
SOURCE2="/data/nf_data/server/nf_tasks"
DEST="/home/ftpuser/data/CCBL/gnps2backpup"
LOGFILE="rsync-backup.log"

# Add a timestamp to the log file
echo "--- Backup started at $(date) ---" >> "$LOGFILE"

# The rsync command
rsync -avz -e ssh "$SOURCE1" rsilva@nppns-data.fcfrp.usp.br:"$DEST" >> "$LOGFILE" 2>&1
rsync -avz -e ssh "$SOURCE2" rsilva@nppns-data.fcfrp.usp.br:"$DEST" >> "$LOGFILE" 2>&1

echo "--- Backup completed at $(date) ---" >> "$LOGFILE"

