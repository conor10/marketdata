#!/bin/bash
export DATE=$(date -u '+%Y%m%d')


err() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $@" >&2
}


msg() {
  echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $@"
}


send_mail() {
  subject=$1
  recipient=$2
  /usr/bin/mail -s "${subject}" "${recipient}" < /dev/null
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