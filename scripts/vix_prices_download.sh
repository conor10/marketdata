#!/bin/bash

DEST_DIR="${VIX_PRICES}/${DATE}"
SYMBOL_LIST="${VIX_SYMBOLS}/current/symbols.txt"
REQUESTOR="$(dirname $0)/google_price_requestor.py"

main() {
  create_dir "${DEST_DIR}"
  /usr/bin/env python "$REQUESTOR" "${SYMBOL_LIST}" "${DEST_DIR}"
}


main "$@"
