#!/bin/bash

DEST_DIR="${SP500_PRICES}/${DATE}"
SYMBOL_LIST="${SP500_SYMBOLS}/current/symbols.txt"
REQUESTOR="$(dirname $0)/google_price_requestor.py"
EXCHANGE=""

main() {
  create_dir "${DEST_DIR}"
  /usr/bin/env python "$REQUESTOR" "${SYMBOL_LIST}" "${DEST_DIR}" "${EXCHANGE}"
}


main "$@"
