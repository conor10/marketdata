#!/bin/bash

DEST_DIR="${FTSE100_SYMBOLS}/${DATE}"
TEMP_DIR="${FTSE100_SYMBOLS}/tmp"
HTML_OUT="${TEMP_DIR}/ftse_telegraph_${DATE}.html"
OUTFILE="${DEST_DIR}/symbols.txt"
SOURCE_URL='http://shares.telegraph.co.uk/indices/?index=UKX'


download_symbols() {
  /usr/bin/wget -O "${HTML_OUT}" "${SOURCE_URL}"
}


extract_symbol_list() {
  grep -o '?epic=[A-Z0-9\.]\+"' "${HTML_OUT}" \
    | uniq \
    | sed -e 's/.*=//g' -e 's/"//g' \
    > "${OUTFILE}"
}


main() {
  create_dir "${DEST_DIR}"
  create_dir "${TEMP_DIR}"

  download_symbols
  extract_symbol_list
}


main "$@"

