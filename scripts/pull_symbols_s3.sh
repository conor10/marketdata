#!/bin/bash

/usr/bin/aws s3 cp --recursive s3://conor10.tickdata/symbols/SP500/${DATE} \
        ${SP500_SYMBOLS}/${DATE}
