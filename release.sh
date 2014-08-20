#!/bin/bash
SETUP_FILE="setup.py"
HOSTS="ec2-54-79-86-205.ap-southeast-2.compute.amazonaws.com \
    ec2-54-79-63-250.ap-southeast-2.compute.amazonaws.com"

PACKAGE_NAME="marketdata"
RELEASE_NAME="marketdata-0.1"
RELEASE_ARCHIVE="${RELEASE_NAME}.tar.gz"
DESTINATION_DIRECTORY="~/trading"
TIMESTAMP="$(date +'%Y%m%d-%H%M%S')"

if [[ ! -f "${SETUP_FILE}" ]]; then
  echo "Error $SETUP_FILE does not exist, exiting"
  exit 1
fi

python setup.py sdist

for host in $HOSTS; do
  scp -i ~/aws/awskey.pem "dist/${RELEASE_ARCHIVE}" \
    "ubuntu@${host}:${DESTINATION_DIRECTORY}"
done

for host in $HOSTS; do
  ssh -i ~/aws/awskey.pem "ubuntu@${host}" "cd ${DESTINATION_DIRECTORY} \
    && mv marketdata marketdata.${TIMESTAMP} \
    && tar xzvf ${RELEASE_ARCHIVE} \
    && mv ${RELEASE_NAME} marketdata"
done