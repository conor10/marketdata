#!/bin/bash

# On an 8GB AWS box, we can only hold 67 days worth of chains before we
# run out of inodes & therefore disk space
/usr/bin/find ${SP500_CHAINS}/* -depth -maxdepth 0 -mtime +30 -type d -exec rm -rf {} \;
