#!/bin/bash

DEST_DIR="${ASX200_PRICES}/${DATE}"
SYMBOL_LIST="${ASX200_SYMBOLS}/current/symbols.txt"
REQUESTOR="$(dirname $0)/google_price_requestor.py"
EXCHANGE="ASX"

main() {
  create_dir "${DEST_DIR}"
  /usr/bin/env python "$REQUESTOR" "${SYMBOL_LIST}" "${DEST_DIR}" "${EXCHANGE}"
}


main "$@"
