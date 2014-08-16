#!/bin/bash

/usr/bin/aws s3 sync ${SP500_CHAINS}/${DATE} \
  s3://conor10.tickdata/chains/SP500/${DATE}