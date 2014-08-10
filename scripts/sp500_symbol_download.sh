#!/bin/bash

DEST_DIR="${SP500_SYMBOLS}/${DATE}"
REQUESTOR="$(dirname $0)/sp_symbol_download.py"

main() {
  create_dir "${DEST_DIR}"
  /usr/bin/env python "$REQUESTOR" "SP500" "${DEST_DIR}"
}


main "$@"

