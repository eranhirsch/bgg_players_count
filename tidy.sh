#!/bin/bash
autoflake -r --in-place --remove-unused-variables .
isort -rc .
black .
mypy -p bgg
mypy *.py
pylama -i E501
