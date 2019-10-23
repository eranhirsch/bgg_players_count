#!/bin/bash
autoflake -r --in-place --remove-unused-variables .
isort -rc .
black .
mypy -p bgg
mypy -p observers
mypy *.py
pylama -i E501
