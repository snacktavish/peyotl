#!/bin/sh
plr="peyotl/test/output/pytlint_report"
echo "Running pylint..."
pylint --rcfile=dev/pylintrc peyotl > "$plr" 2>&1
cat "$plr" | sed -n '/Report/q;p'
grep '^Your code has been rated' "$plr"
