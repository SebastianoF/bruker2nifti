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
curl https://bootstrap.pypa.io/get-pip.py | python  # after issue with pip 9.0.1
python setup.py install
pip install -r $PARENTDIR/requirements.txt
deactivate

echo
echo 'Selecting paths required to have the python of the virtualenvironment:'
echo

DIR_PY=venv/bin/python
CALLER=$PARENTDIR/$DIR_PY
EXEC=$PARENTDIR/bruker2nifti/gui/open.py

echo
echo 'Generating launcher-like and add permission:'
echo

echo '#!/bin/sh' > OpenGUIbru2nii
echo $CALLER $EXEC >> OpenGUIbru2nii
chmod +x OpenGUIbru2nii


echo
echo '...DONE!'
echo 'Double click on OpenGUIbru2nii inside the cloned repository to open the gui!'