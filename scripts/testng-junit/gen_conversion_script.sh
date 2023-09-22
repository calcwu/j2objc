#!/bin/bash

# Check if there are no arguments provided
if [ $# -eq 0 ]; then
  echo "Usage: $0 [base-module] (infra/library) "
  exit 1
fi

SKIP_INFRA_LIB_MODULES=("bson" "kafka-manual-ack" "blobstore-s3" "messaging" "configutils" "crypto" "distributedlocks" "filemuncher" "grpc" "guice" "jersey" "jetty-filter" "jetty" "jooq" "jsonapi" "kafka-server" "kafka" "kryo" "lang" "logging" "maxwell" "mongo" "multistage" "parquet" "request" "rest" "secrets" "ssl" "syndicatedcache" "testing" "threads" "kafka-admin")
script_dir=$(dirname $0)
conversion_script="$script_dir/testng2junit.py"
echo "conversion_script: $conversion_script"

echo "Run: find . -name 'BUCK' | grep $1 | awk -F 'BUCK' '{print \$1}' | awk -F '/' '{print \$4}'"
list_all_modules=$(find . -name 'BUCK' | grep "$1" | awk -F 'BUCK' '{print $1}' | awk -F '/' '{print $4}')


rm -rf run_test.sh
for module in $list_all_modules; do
  buck_module="$1/$module"
  if [ -d "$buck_module/src/test" ]; then
    skip=0
    for item in "${SKIP_INFRA_LIB_MODULES[@]}"; do
      if [ "$module" = "$item" ]; then
        skip=1
        break  # Exit the loop early if a match is found
      fi
    done

    # Check if a match was found
    if [ $skip -eq 1 ]; then
      echo "Skip problematic module: $module"
    else
      echo "python $conversion_script $buck_module"
      python $conversion_script $buck_module
      # commit the change for each module.
#      git commit -am $module
      run_cmd="./buck test $buck_module:test &> $module.test"
      echo "echo \"$run_cmd\"" >> run_test.sh
      echo "$run_cmd" >> run_test.sh
    fi
  fi
done
chmod a+x run_test.sh