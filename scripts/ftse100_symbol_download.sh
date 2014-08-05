#!/bin/bash

DEST_DIR="${FTSE100_SYMBOLS}/${DATE}"
TEMP_DIR="${FTSE100_SYMBOLS}/tmp"
HTML_OUT="${TEMP_DIR}/ftse_yahoo_${DATE}.html"
OUTFILE="${DEST_DIR}/symbols.txt"
SOURCE_URLS_FILE="$(dirname $0)/yahoo_urls.txt"


download_symbols() {
  /usr/bin/wget -i "${SOURCE_URLS_FILE}" -O "${HTML_OUT}"
}


extract_symbol_list() {
  grep -o '>[A-Z]*\.L</a>' "${HTML_OUT}" \
    | sed -n "s/>\(.*\)<\/a>/\1/p" \
    > "${OUTFILE}"
}


main() {
  create_dir "${DEST_DIR}"
  create_dir "${TEMP_DIR}"

  download_symbols
  extract_symbol_list
  verify_linecount_equals 101 "${OUTFILE}"
}


main "$@"

