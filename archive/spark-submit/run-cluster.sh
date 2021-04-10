#!/usr/bin/env bash

# set -eux

export NAMESPACE=spark-jobs
PRIORITY_CLASSES=("routine" "urgent" "exceptional" "rush")
NUMBER_REGEX='^[0-9]+$'

error() {
  echo "Error: $1"
  usage
  exit 1
}

usage() {
  echo "Usage: $0 [<priority class>[:<instances>] [<priority class>[:<instances>] [...]]]"
  echo "<priority class> must be one of ${PRIORITY_CLASSES[*]}"
  echo "<instances> the number of instances for that priority"
  echo "If no argument is given, the script will launch 1 Spark job with priority '${PRIORITY_CLASSES[0]}'"
  echo "Ex: $0 routine:2 urgent:5 rush"
}

launch() {
  ./spark-submit-py-pi.sh $1 > /dev/null 2>&1 &
}

if [[ "$#" -eq 0 ]]; then
  launch "${PRIORITY_CLASSES[0]}"
else
  PRIORITIES=()
  INSTANCES=()

  # Check params
  while (( "$#" )); do
    IFS=':' TOKENS=( $1 )
    if (( ${#TOKENS[@]} > 2 )); then
      error "Bad params '$1'"
    fi

    PR=${TOKENS[0]}
    if [[ ! " ${PRIORITY_CLASSES[@]} " =~ " ${PR} " ]]; then
      error "Bad priority class '${PR}'"
    fi

    INST=${TOKENS[1]:-1}
    if ! [[ ${INST} =~ ${NUMBER_REGEX} ]] ; then
     error "'${INST}' is not a number"
    fi

    PRIORITIES+=(${PR})
    INSTANCES+=(${INST})

    shift
  done

  # Let's run
  for ((i=0; i < ${#PRIORITIES[@]}; i++)); do
    for ((j=0; j < ${INSTANCES[i]}; j++)); do
      launch ${PRIORITIES[i]}
    done
  done
fi

# echo "-- Run 'watch kubectl get pods --namespace=${NAMESPACE} -o wide' to see the running pods"

watch kubectl get pods --namespace=${NAMESPACE} -o wide
