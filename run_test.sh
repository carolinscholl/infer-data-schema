#!/bin/bash
SCRIPT_PATH=$(readlink -f "$0")

WORKDIR=$(dirname "$SCRIPT_PATH")
cd "$WORKDIR" || exit

export RUN_ENV=infer-schema

if ! { conda env list | grep $RUN_ENV; } >/dev/null 2>&1; then conda env create -f environment.yml; fi
source activate base
conda activate $RUN_ENV

export PYTHONPATH="${WORKDIR}:${PYTHONPATH}"

python -m unittest discover test
