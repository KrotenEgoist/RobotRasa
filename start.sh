#!/bin/zsh
export SQLALCHEMY_SILENCE_UBER_WARNING=1
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
conda activate rasa_test
