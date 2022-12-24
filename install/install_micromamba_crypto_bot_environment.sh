#!/usr/bin/env bash

# File:        install/install_micromamba_crypto_bot_environment.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       bash install/install_micromamba_crypto_bot_environment.sh
# Description: Installs all packages required for the crypto_bot.

MICROMAMBA_ENV_NAME="crypto_bot"

# Automagic.
/opt/micromamba/bin/micromamba create --yes --name ${MICROMAMBA_ENV_NAME} gcc \
                                                                          gxx_linux-64 \
                                                                          cython \
                                                                          numpy \
                                                                          bottleneck \
                                                                          numexpr \
                                                                          pandas \
                                                                          scipy \
                                                                          matplotlib \
                                                                          seaborn \
                                                                          setuptools-git \
                                                                          tqdm \
                                                                          mosquitto \
                                                                          paramiko \
                                                                          regex \
                                                                          pandas-ta \
                                                                          ta \
                                                                          ta-lib \
                                                                          ipywidgets \
                                                                          jupyterlab \
                                                                          widgetsnbextension \
                                                                          typeguard \
                                                                          typing_extensions \
                                                                          click \
                                                                          dateparser \
                                                                          beautifulsoup4 \
                                                                          flask-socketio \
                                                                          requests \
                                                                          websockets \
                                                                          python-binance \
                                                                          pip \
                                                                          python=3
