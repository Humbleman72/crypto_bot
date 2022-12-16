#!/usr/bin/env bash

# File:        install/install_conda_crypto_logger_environment.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       bash install/install_conda_crypto_logger_environment.sh
# Description: Installs all packages required for the crypto_logger.

CONDA_ENV_NAME="crypto_logger"
PYTHON_VERSION="3"

# Automagic.
/opt/conda/bin/conda create --yes --name ${CONDA_ENV_NAME} --channel conda-forge gcc gxx_linux-64 gcc_linux-64 cython numexpr bottleneck numpy pandas scipy matplotlib tqdm ta-lib pip python=${PYTHON_VERSION} && \
/opt/conda/bin/conda init bash && \
source /opt/conda/bin/activate ${CONDA_ENV_NAME} && \
if [[ "$(echo $PS1 | cut -d' ' -f1 | tr -d '()')" == "${CONDA_ENV_NAME}" ]]
then
    yes | pip install --upgrade --no-cache-dir numpy python-binance ta 'typing_extensions==3.10.0.2' git+https://github.com/twopirllc/pandas-ta
else
    echo "Could not source activate ${CONDA_ENV_NAME}..."
fi
