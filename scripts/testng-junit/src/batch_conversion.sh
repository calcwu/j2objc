#!/bin/bash

# Check if there are no arguments provided
#
#

modules=(
  "domain/library/feature-visibility"
  "domain/library/firms"
  "domain/library/fxfwd"
  "domain/library/gff"
  "domain/library/gffvalidation"
)

conversion_script="/Volumes/code/j2objc/scripts/testng-junit/src/testng2junit5.py"
echo "conversion_script: $conversion_script"

rm -f run_test.sh
mkdir -p tests
for module in "${modules[@]}"; do
  echo "python $conversion_script $module"
  last_part=$(basename "$module")
  python $conversion_script $module
  # commit the change for each module.
  git commit -am $last_part
  run_cmd="./buck test $module:test &> tests/$last_part"
  echo "echo \"$run_cmd\"" >> run_test.sh
  echo "$run_cmd" >> run_test.sh
done

chmod a+x run_test.sh