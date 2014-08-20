#!/bin/bash
export DATE=$(date -u '+%Y%m%d')


err() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $@" >&2
}


msg() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $@"
}


send_mail() {
  recipient=$1
  subject=$2
  /usr/bin/mail -s "${subject}" "${recipient}" < /dev/null
}


send_text() {
  recipient=$1
  message=$2
  /usr/bin/curl -X POST 'https://api.twilio.com/2010-04-01/Accounts/ACa87ebe424f8191a64a5a88e2e9fc3942/Messages.json' \
    --data-urlencode "To=${recipient}"  \
    --data-urlencode 'From=+14843711050'  \
    --data-urlencode "Body=${message}" \
    -u ACa87ebe424f8191a64a5a88e2e9fc3942:5dbda90d061beeaf3d32e6ec0daffc32

}

create_dir() {
  local dir_name=$1

  if [[ ! -d "${dir_name}" ]]; then
    mkdir -p "${dir_name}"
  fi
}


verify_linecount_equals() {
  local expected=$1
  local file=$2

  count=$(wc -l < "${file}")

  if (( ${count} != ${expected} )); then
    err "Bad expected line count: ${count} != expected: ${expected}"
    return 1
  fi
}


verify_linecount_at_least() {
  local expected=$1
  local file=$2

  count=$(wc -l < "${file}")

  if (( ${count} < ${expected} )); then
    err "Bad expected line count: ${count} < expected: ${expected}"
    return 1
  fi
}