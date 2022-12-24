#!/usr/bin/env bash

# File:        install/install_micromamba_crypto_logger_environment.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       bash install/install_micromamba_crypto_logger_environment.sh
# Description: Installs all packages required for the crypto_logger.

MICROMAMBA_ENV_NAME="crypto_logger"

# Automagic.
/opt/micromamba/bin/micromamba create --yes --name ${MICROMAMBA_ENV_NAME} gcc \
                                                                          gxx_linux-64 \
                                                                          cython \
                                                                          bottleneck \
                                                                          numexpr \
                                                                          numpy \
                                                                          pandas \
                                                                          matplotlib \
                                                                          scipy \
                                                                          ta \
                                                                          pandas-ta \
                                                                          ta-lib \
                                                                          tqdm \
                                                                          python-binance \
                                                                          typing_extensions \
                                                                          pip \
                                                                          python=3
