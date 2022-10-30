#!/usr/bin/env bash

# File:        install/install_rltrader_environment.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       cd ~/workspace/RLTrader && bash install/install_rltrader_environment.sh
# Description: Installs all packages required for finance data science and analysis.

CONDA_ENV_NAME="rltrader"
PYTHON_VERSION="3"
PIP_VERSION="21.0.1"
NUMPY_VERSION="1.19.5"
CUDATOOLKIT_VERSION="11"
TENSORFLOW_VERSION="1.14.0"

conda create --yes --name ${CONDA_ENV_NAME} --channel conda-forge certifi ta-lib h5py pandas colorlog gym tensorflow-gpu=${TENSORFLOW_VERSION} tensorboard typeguard cudatoolkit=${CUDATOOLKIT_VERSION} pip=${PIP_VERSION} python=${PYTHON_VERSION} && \
conda init bash && \
source activate ${CONDA_ENV_NAME} && \
if [[ "$(echo $PS1 | cut -d' ' -f1 | tr -d '()')" == "${CONDA_ENV_NAME}" ]]
then
    yes | python -m pip install -r requirements.base.txt
else
    echo "Could not source activate ${CONDA_ENV_NAME}..."
fi
