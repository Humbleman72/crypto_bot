#!/usr/bin/env bash

# File:        install/uninstall_conda.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       bash install/uninstall_conda.sh
# Description: Uninstall conda if needed.

if [[ "$(which conda)" != "" ]]
then
    if [[ "$(echo $PS1 | cut -d' ' -f1 | tr -d '()')" != "base" ]]
    then
        conda deactivate
    fi

    conda clean --yes --all --force-pkgs-dirs && \
    conda install --yes anaconda-clean && \
    anaconda-clean --yes && \
    sudo rm -rf /opt/conda && \
    echo "Don't forget to manually remove anaconda3 PATH in ~/.bash_profile and ~/.bashrc!"
fi

