#!/bin/sh

# simple bash script to create a gui 'launcher'.
# Location of the launcher can be changed, copy-pasted and moved around
# location of the bruker2nifti folder cannot be moved!!

# get directory bruker2 nifty, and move there.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

# create virtual environment, install the libraries and deactivate
sudo apt-get install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# select paths required to have the python of the virtualenvironment

DIR_PY=venv/bin/python
CALLER=$DIR/$DIR_PY
EXEC=$DIR/open_GUI.py

# generate 'launcher' and add permission

echo '#!/bin/sh' > runGUIbru2nii
echo $CALLER $EXEC >> runGUIbru2nii
chmod +x runGUIbru2nii