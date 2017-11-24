#!/bin/bash

NO_VENT=false

_error() {
    echo $1; exit 1;
}

function _python () {
    python3 $@
}

function _is_virtualenv_installed () {
    _python -m virtualenv --help 1>2 &>/dev/null || _error "'virtualenv' is needed but not installed properly"
}

function _is_pip_installed () {
    _python -m pip 1>2 &>/dev/null || _error "'pip' required but not installed properly, exiting"
}

function _is_npm_installed () {
    $(command -v npm &> /dev/null) || _error "'npm' is needed but not installed properly"
}

function _pip() {
    _python -m pip $@
}

function _virtualenv() {
    _python -m virtualenv $@
}

function _npm() {
    npm $@
}

case $1 in
    --venv )
        shift
        VENV=true
        VENV_PATH=$1 && shift
        if [[ -z $VENV_PATH ]] ; then
            echo "VENV_PATH" is required
        fi
        ;;
    --dev )
        shift
        DEV=true
        ;;
    -h | --help )
        echo "usage: setup.sh [-h] [--venv VENV_PATH]
        options:
        --venv      Create a virtual env in given patch and install all python packages inside the virtual env.
        --dev       Install dev packages, or only production packages are installed.
        "
        exit 0
        ;;
esac

_is_pip_installed
_is_npm_installed

if [[ $VENV == 'true' ]] ; then
    _is_virtualenv_installed
    _virtualenv $VENV_PATH
    source $VENV_PATH/bin/activate
fi

echo "Installing requirements of Metadash"
if [[ -f 'requirements.txt' ]]; then
    _pip install -r requirements.txt
fi

if [[ $DEV == 'true' && -f 'requirements.dev.txt' ]]; then
    echo "Installing dev requirements of Metadash"
    _pip install -r requirements.txt
fi

echo "Installing requirements of Plugins"
for file in ./metadash/plugins/*/requirements.txt; do
    if [[ -f $file ]]; then
        _pip install -r $file
    fi
done

echo "Install npm packages"
_npm install

echo "Rebuilding Assets"
_npm run build