## Bruker2nifti

Medical image format converter: from raw Brukert ParaVision to nifti, written in Python.

### Requirements
* Python 2.7+

### Installation
* `pip install -r requirements.txt`
* (optional) `python setup.py install` to install as a library
* (suggested) `pip install -e .` to install with pip in development mode.

### GUI Installation
Open a terminal in the root folder of the cloned repository, then
* `chmod 777 gui_setupper_MAC.sh`
* `./gui_setupper_MAC.sh`
Alternatively double click on gui_run_setupper_MAC

This simple bash script will create sort of 'launcher', named runGUIbru2nii that uses a virtualenvironment
created in the root directory (not tested yet for LINUX). 
Once created, the location of the launcher can be changed, copy-pasted and moved around the system.
The location of bruker2nifti folder cannot be moved. If moved the GUI Installation needs to be repeated

### Testing
Unit testing with [nosetest](http://pythontesting.net/framework/nose/nose-introduction/):
* `nosetests`

### Use the parser from command line    
* `python parsers/bruker2nii -h`
* `python parsers/bruker2nii -i path/to/bruker/study -o path/to/output/folder`


### Further notes <a name="up"></a>
Additional documentation and how to run for non-python programmers: [bruker2nifti_wiki](https://github.com/SebastianoF/bruker2nifti/wiki).

### Useful links <a name="utilities"></a>
+ [nifti format](https://nifti.nimh.nih.gov/nifti-1): official documentation.
+ [nifti format](https://brainder.org/2012/09/23/the-nifti-file-format/): unofficial documentation.
+ [nibabel](http://nipy.org/nibabel/): neuroimaging python library. 
+ [bruker format info](http://imaging.mrc-cbu.cam.ac.uk/imaging/FormatBruker): one of the few places where to find 
information about Bruker format, other than the official documentation stored under 
<PvInstDir>/prog/docu/english/pvman/D/Docs/D02_PvParams.pdf of the ParaVision installation. 
+ [pvconv](https://github.com/matthew-brett/pvconv): from Bruker to Analyze, Perl.
+ [Bru2Nii](https://github.com/neurolabusc/Bru2Nii): from Bruker to Nifti, Pascal. Conversion is based on the parameters contained in the **reco** parameter file. This
parameter file exists only if the image was created using ParaVision reconstruction.
+ [mpi](https://github.com/francopestilli/mpi): from Bruker to Vistasoft or Analyze in Matlab. As Bru2nii the conversion 
is based on the parameters contained in the **reco** parameter file.
+ [Bruker2nifti](https://github.com/CristinaChavarrias/Bruker2nifti): from Bruker to Nifti, Matlab (not maintained anymore?).

### Thanks <a name="thanks"></a>
Thanks to 
Bernard Siow (Centre for Advanced Biomedical Imaging, UCL), 
Willy Gsell (Department of Imaging and Pathology, KU Leuven) 
and 
Mattew Brett (Berkeley Brain Imaging Center).





