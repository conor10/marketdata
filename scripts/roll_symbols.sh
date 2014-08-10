#!/bin/bash

CURRENT="current"
CURRENT_SYMBOLS="${CURRENT}/symbols.txt"


main() {
  for dir in "${FTSE100_SYMBOLS}" "${SP500_SYMBOLS}" "${ASX200_SYMBOLS}"; do
    update_symbols "${dir}"
  done
}


update_symbols() {
  dir=$1
  if [[ -d "${dir}" ]]; then
    cd "${dir}"
    latest_dir=$(ls -d 20* | tail -1)
    latest_symbols="${latest_dir}/symbols.txt"

    if [[ -L "${CURRENT}" ]]; then
      /usr/bin/diff "${CURRENT_SYMBOLS}" "${latest_symbols}" > /dev/null
      if (( $? == 1 )); then
        line_count="$(/usr/bin/wc -l ${latest_symbols} \
          | /usr/bin/cut -d' ' -f1)"
        prev_line_count="$(/usr/bin/wc -l ${CURRENT_SYMBOLS} \
          | /usr/bin/cut -d' ' -f1)"
        tolerence=$(( ${prev_line_count} - 5 ))
        if (( ${line_count} > ${tolerence} )); then
          msg "Deleting previous link, new symbol list size: ${line_count},"\
            "previous symbol list size: ${prev_line_count}"
          echo /bin/rm "${CURRENT}"
          msg "Setting ${latest_dir} to current"
          ln -s "${latest_dir}" "${CURRENT}"
        fi
      fi
    else
      msg "Creating new symlink for ${latest_dir}"
      ln -s "${latest_dir}" "${CURRENT}"
    fi

  else
    err "Directory: ${dir} does not exist"
  fi
}


main "$@"