## Bruker2nifti

Medical image format converter: from raw Brukert ParaVision to nifti, written in Python.

### Requirements
* Python 2.7+ provided with the libraries in requirements.txt (generated with pipreqs).

### Installation
To install it as a Python library
```
pip install bruker2nifti
```

### To install in development mode:
```
cd path-to-bruker2nifti-repo
pip install -e .
```

### CLI usage (no installation):
* `PYTHONPATH="${PYTHONPATH}:path-to-bruker2nifti-repo"`
* `python parsers/bruker2nii.py -h`
* `python parsers/bruker2nii.py -i path/to/a/bruker/study -o path/to/output/folder`
Where python is a distribution proivided with the required libraries.

### Open the GUI
```
cd path-to-bruker2nifti-repo
chmod 777 GUI/setupper_MAC.sh
./GUI/setupper_MAC.sh
```

Alternatively double click on 
`GUI/run_setupper_MAC`.
After the installation, double-click on the file 'OpenGUIbru2nii' to open the GUI. 
The launcher can be moved around in the user system.

![gui_example](https://github.com/SebastianoF/bruker2nifti/blob/master/screenshots/gui_example.jpg)

### Testing
Unit testing with [nosetest](http://pythontesting.net/framework/nose/nose-introduction/):
* `nosetests`
Tests are based on an open dataset Bruker images downloadable with the repo, in the folder 
[test_data](https://github.com/SebastianoF/bruker2nifti/tree/master/test_data)

### API documentation, further notes and examples <a name="up"></a>
Essential API documentation can be found [here](bruker2nifti.rtfd.io).
Additional documentation and examples can be found in the [bruker2nifti wiki pages](https://github.com/SebastianoF/bruker2nifti/wiki).

### Useful links and related software <a name="utilities"></a>
+ [nifti format](https://nifti.nimh.nih.gov/nifti-1): official documentation.
+ [nifti format](https://brainder.org/2012/09/23/the-nifti-file-format/): unofficial documentation.
+ [nibabel](http://nipy.org/nibabel/): neuroimaging python library. 
+ [bruker format info](http://imaging.mrc-cbu.cam.ac.uk/imaging/FormatBruker): one of the few places where to find 
information about Bruker format, other than the official documentation stored under 
<PvInstDir>/prog/docu/english/pvman/D/Docs/D02_PvParams.pdf of the ParaVision installation. 
+ [pvconv](https://github.com/matthew-brett/pvconv): from Bruker to Analyze, Perl.
+ [Bru2Nii](https://github.com/neurolabusc/Bru2Nii): from Bruker to Nifti, written in Pascal. 
+ [mpi](https://github.com/francopestilli/mpi): from Bruker to Vistasoft or Analyze in Matlab. Conversion is based on the parameters contained in the **reco** parameter file. This
parameter file exists only if the image was created using ParaVision reconstruction.
+ [Bruker2nifti](https://github.com/CristinaChavarrias/Bruker2nifti): from Bruker to Nifti, Matlab (not maintained anymore?).


### Copyright and Licence 
Copyright (c) 2017, Sebastiano Ferraris.
Bruker2nifti is available as free open-source software under [MIT License](https://github.com/SebastianoF/bruker2nifti/blob/master/LICENCE.txt).

### Thanks <a name="thanks"></a>
Thanks to 
Bernard Siow (Centre for Advanced Biomedical Imaging, University College London), 
Chris Rorden (McCausland Center for Brain Imaging, University of South Carolina) 
and 
Mattew Brett (Berkeley Brain Imaging Center).
