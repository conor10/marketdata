#!/bin/bash

/usr/bin/aws s3 sync ${FTSE100_SYMBOLS}/${DATE} \
  s3://conor10.tickdata/symbols/FTSE100/${DATE}

/usr/bin/aws s3 sync ${ASX200_SYMBOLS}/${DATE} \
  s3://conor10.tickdata/symbols/ASX200/${DATE}

/usr/bin/aws s3 sync ${SP500_SYMBOLS}/${DATE} \
  s3://conor10.tickdata/symbols/SP500/${DATE}
