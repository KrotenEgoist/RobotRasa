#!/bin/bash
export SQLALCHEMY_SILENCE_UBER_WARNING=1

eval "$(conda shell.bash hook)"
conda activate rasa_dev

rasa shell