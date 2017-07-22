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

# create the virtualenvironment where to install the libraries:
conda create -n venv python=2.7 anaconda
# activate it
source activate venv
# install the required libraries:
conda install -n vevn -c conda-forge nose
conda install -n vevn -c conda-forge nibabel
conda install -n vevn -c anaconda numpy
conda install -n vevn -c anaconda setuptools
conda install -n vevn -c anaconda sympy
# install bruker2nifti as a local library:
python setup.py install
# deacrivate
source deactivate

echo
echo 'Selecting paths required to have the python of the virtualenvironment:'
echo

CALLER=//anaconda/envs/venv/bin/python
EXEC=$PARENTDIR/open_GUI.py

echo
echo 'Generating launcher-like and add permission:'
echo

echo '#!/bin/sh' > OpenGUIbru2nii
echo $CALLER $EXEC >> OpenGUIbru2nii
chmod +x OpenGUIbru2nii


echo
echo '...DONE!'