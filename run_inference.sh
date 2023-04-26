#!/bin/bash
SCRIPT_PATH=$(readlink -f "$0")
DATA_PATH=$(readlink -f "$1")  # will get absolute path of file
if [[ ! -z $2 ]]; then SCHEMA_PATH=$(readlink -f "$2"); fi

WORKDIR=$(dirname "$SCRIPT_PATH")
cd "$WORKDIR" || exit

export RUN_ENV=infer-schema

if ! { conda env list | grep $RUN_ENV; } >/dev/null 2>&1; then conda env create -f environment.yml; fi
source activate base
conda activate $RUN_ENV

export PYTHONPATH="${WORKDIR}:${PYTHONPATH}"

if [[ ! -z $2 ]]; then
  python ./src/main.py "$DATA_PATH" --schema_fpath "$SCHEMA_PATH"
elif [[ ! -z $1 ]]; then
  python ./src/main.py "$DATA_PATH"
else
  python ./src/main.py --h
fi

conda deactivate
