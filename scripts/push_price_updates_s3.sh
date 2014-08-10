#!/bin/bash

/usr/bin/aws s3 sync ${FTSE100_PRICES}/${DATE} \
  s3://conor10.tickdata/prices/FTSE100/${DATE}

/usr/bin/aws s3 sync ${ASX200_PRICES}/${DATE} \
  s3://conor10.tickdata/prices/ASX200/${DATE}

/usr/bin/aws s3 sync ${SP500_PRICES}/${DATE} \
  s3://conor10.tickdata/prices/SP500/${DATE}