#!/bin/sh

# simple bash script to create a gui 'launcher'.
# Location of the launcher can be changed, copy-pasted and moved around
# location of the bruker2nifti folder cannot be moved!!


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENTDIR="$(dirname "$DIR")"
cd $PARENTDIR

echo
echo 'Creating virtual environment, installing the libraries and deactivating:'
echo

pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
python setup.py install
deactivate

echo
echo 'Selecting paths required to have the python of the virtualenvironment:'
echo

DIR_PY=venv/bin/python
CALLER=$PARENTDIR/$DIR_PY
EXEC=$PARENTDIR/bruker2nifti/open_GUI.py

echo
echo 'Generating launcher-like and add permission:'
echo

echo '#!/bin/sh' > OpenGUIbru2nii
echo $CALLER $EXEC >> OpenGUIbru2nii
chmod +x OpenGUIbru2nii


echo
echo '...DONE!'