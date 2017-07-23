#!/bin/bash

# simple bash script to create a gui 'launcher'.
# Location of the launcher can be changed, copy-pasted and moved around
# location of the bruker2nifti folder cannot be moved!!

# get directory bruker2 nifty, and move there.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENTDIR="$(dirname "$DIR")"
cd $PARENTDIR

echo
echo 'Creating virtual environment, installing the libraries and deactivating:'
echo

sudo apt-get install virtualenv
sudo apt-get install python-tk
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
python setup.py install
deactivate

echo
echo 'Selecting paths required to have the python of the virtualenvironment:'
echo

DIR_PY=venv/bin/python
CALLER=$PARENTDIR/$DIR_PY
EXEC=$DIR/open_GUI.py

echo
echo 'Generating launcher-like and add permission:'
echo

echo '#!/bin/sh' > OpenGUIbru2nii
echo $CALLER $EXEC >> OpenGUIbru2nii
chmod +x OpenGUIbru2nii

echo
echo '...DONE!'