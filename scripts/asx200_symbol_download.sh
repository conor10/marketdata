#!/bin/bash

DEST_DIR="${ASX200_SYMBOLS}/${DATE}"
REQUESTOR="$(dirname $0)/sp_symbol_download.py"

main() {
  create_dir "${DEST_DIR}"
  /usr/bin/env python "$REQUESTOR" "ASX200" "${DEST_DIR}"
}


main "$@"

