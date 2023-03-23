#!/bin/zsh
conda activate rasa_test
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
export SQLALCHEMY_SILENCE_UBER_WARNING=1
