#!/bin/sh

# simple bash script to create a gui 'launcher'.
# Location of the launcher can be changed, copy-pasted and moved around
# location of the bruker2nifti folder cannot be moved!!


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

echo
echo 'create virtual environment, install the libraries and deactivate'
echo

pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo
echo 'select paths required to have the python of the virtualenvironment'
echo


DIR_PY=venv/bin/python
CALLER=$DIR/$DIR_PY
EXEC=$DIR/open_GUI.py

echo
echo 'generate launcher-like and add permission'
echo


echo '#!/bin/sh' > runGUIbru2nii
echo $CALLER $EXEC >> runGUIbru2nii
chmod +x runGUIbru2nii