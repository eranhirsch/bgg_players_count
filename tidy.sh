#!/bin/bash
autoflake -r --in-place --remove-unused-variables .
isort -rc .
black .
/opt/homebrew/bin/mypy -p bgg
/opt/homebrew/bin/mypy -p observers
/opt/homebrew/bin/mypy *.py
pylama -i E501
