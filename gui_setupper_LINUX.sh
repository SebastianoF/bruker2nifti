#!/bin/bash

# simple bash script to create a gui 'launcher'.
# Location of the launcher can be changed, copy-pasted and moved around
# location of the bruker2nifti folder cannot be moved!!

# get directory bruker2 nifty, and move there.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

echo '\n create virtual environment, install the libraries and deactivate\n'
sudo apt-get install virtualenv
sudo apt-get install python-tk
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
deactivate

echo '\n select paths required to have the python of the virtualenvironment\n'

DIR_PY=venv/bin/python
CALLER=$DIR/$DIR_PY
EXEC=$DIR/open_GUI.py

echo '\n generate launcher-like and add permission \n'

echo '#!/bin/sh' > runGUIbru2nii
echo $CALLER $EXEC >> runGUIbru2nii
chmod +x runGUIbru2nii