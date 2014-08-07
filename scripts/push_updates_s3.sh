#!/bin/bash
/usr/bin/aws s3 sync ${FTSE100_SYMBOLS}/${DATE} \
  s3://conor10.tickdata/symbols/FTSE100/${DATE}

/usr/bin/aws s3 sync ${FTSE100_PRICES}/${DATE} \
  s3://conor10.tickdata/prices/FTSE100/${DATE}