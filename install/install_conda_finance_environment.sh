#!/usr/bin/env bash

# File:        install/install_conda_finance_environment.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       cd ~/workspace/crypto_logger && bash install/install_conda_finance_environment.sh
# Description: Installs all packages required for finance data science and analysis.

CONDA_ENV_NAME="finance"
PYTHON_VERSION="3"
PIP_VERSION="21.0.1"
NUMPY_VERSION="1.19.5"
CUDATOOLKIT_VERSION="11"
ONNX_VERSION="1.4.1"
TENSORFLOW_VERSION="2.4.1"
PYTORCH_VERSION="1.7"
TORCHVISION_VERSION="0.8"

# Automagic.
conda create --yes --name ${CONDA_ENV_NAME} --channel pytorch --channel conda-forge gcc gxx_linux-64 gcc_linux-64 cython pandas=1.2.5 numpy matplotlib tqdm setuptools-git ta-lib featuretools python-graphviz lunarcalendar convertdate holidays requests==2.23.0 requests-cache flask beautifulsoup4 selenium jupyterlab ipywidgets widgetsnbextension scipy scikit-learn statsmodels gym h5py tensortrade tensorflow-gpu=${TENSORFLOW_VERSION} tensorflow-estimator tensorflow-datasets tensorflow-hub tensorflow-metadata tensorflow-probability keras keras-applications keras-preprocessing tensorboard typeguard pytorch=${PYTORCH_VERSION} torchvision=${TORCHVISION_VERSION} cudatoolkit=${CUDATOOLKIT_VERSION} pip=${PIP_VERSION} python=${PYTHON_VERSION} && \
conda init bash && \
source activate ${CONDA_ENV_NAME} && \
if [[ "$(echo $PS1 | cut -d' ' -f1 | tr -d '()')" == "${CONDA_ENV_NAME}" ]]
then
    conda install --yes --channel pytorch --channel conda-forge openjdk=11 lightgbm requests-cache && \
    yes | python -m pip install --upgrade --no-cache-dir numpy==${NUMPY_VERSION} python-binance investpy quantstats yfinance geckodriver-autoinstaller 'featuretools[complete]' 'ray[default,tune,rllib,serve]' yahoofinancials ta 'typing_extensions==3.10.0.2' pandas_market_calendars git+https://github.com/twopirllc/pandas-ta eif
    yes | python -m pip install -q --no-deps tensorflow-addons~=0.6
    CMDSTAN=/tmp/cmdstan-2.22.1 STAN_BACKEND=CMDSTANPY yes | python -m pip install --upgrade prophet cmdstanpy==0.9.5
    yes | python -m pip deinstall fbprophet
    yes | python -m pip install --upgrade --no-cache-dir pystan==2.19.1.1
    yes | python -m pip install --upgrade --no-cache-dir fbprophet
    yes | python -m pip install --no-cache-dir -e Merlion/[plot]
    yes | python -m pip install --no-cache-dir -e Merlion/ts_datasets/
else
    echo "Could not source activate ${CONDA_ENV_NAME}..."
fi

