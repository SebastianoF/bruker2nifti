[![status](http://joss.theoj.org/papers/2ee6a3a3b1a4d8df1633f601bf2b0ffe/status.svg)](http://joss.theoj.org/papers/2ee6a3a3b1a4d8df1633f601bf2b0ffe)
[![Build Status](https://travis-ci.org/SebastianoF/bruker2nifti.svg?branch=master)](https://travis-ci.org/SebastianoF/bruker2nifti)

## Bruker2nifti

Medical image format converter: from raw [Bruker](http://imaging.mrc-cbu.cam.ac.uk/imaging/FormatBruker) 
ParaVision to [NifTi](https://nifti.nimh.nih.gov/nifti-1), written in Python.

Further information about the motivation can be found [here](https://github.com/SebastianoF/bruker2nifti/tree/master/paper).
Code repository can be found [here](https://github.com/SebastianoF/bruker2nifti).

### Requirements
* Python 2.7+ and the libraries listed in the file [requirements.txt](https://github.com/SebastianoF/bruker2nifti/blob/master/requirements.txt).

### Installation
To install the latest (stable) release as a python library via pip, type 
```
pip install bruker2nifti
```
(installing the library inside a [virtualenvironment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) is warmly recommended).

To install the current development version, please see the 
[wiki-installing](https://github.com/SebastianoF/bruker2nifti/wiki/Installing-latest-updates-and-in-development-mode) page. 

### Usage:

The converter can be accessed via: 
+ Python command shell, 
+ Command Line Utility (CLI) to integrate it in a bash script,
+ Graphical User Interface (GUI).

Moreover, a launcher can be automatically created to access the GUI with no-Python knowledge required.  

#### Python command shell
After installing the stable release with `pip install bruker2nifti`, access the Python command shell typing `python` (or `ipython` if the 
[interactive command](https://en.wikipedia.org/wiki/IPython) shell is preferred), then import bruker2nifti with
```
import bruker2nifti
```
An example can be found in [wiki-example](https://github.com/SebastianoF/bruker2nifti/wiki/Examples) 

#### Command Line utility
After installing bruker2nifti with `pip install bruker2nifti`, type `bruker2nifti -h` at the prompt to access the
 help of the CLI.

<!--
#### Accessing the Command Line Utility without installing
If you prefer to access the command line utility without installing the library on your python environment,
you can download the [latest release](https://github.com/SebastianoF/bruker2nifti/releases) or the 
[development version](https://github.com/SebastianoF/bruker2nifti) on your system, then add it to the python path
with `PYTHONPATH="${PYTHONPATH}:path-to-bruker2nifti-repository"` and access the help of the CLI via  

+ `python parsers/bruker2nii.py -h`

Where the invoked Python is a distribution provided with the [required libraries](https://github.com/SebastianoF/bruker2nifti/blob/master/requirements.txt). .
-->

#### Open the Graphical User Interface (GUI)
After installing bruker2nifti with `pip install bruker2nifti`, type `bruker2nifti -h` at the prompt to access the
 help of the CLI.
```
bruker2nifti_gui
```
This will open the graphical user interface:

![gui_example](https://github.com/SebastianoF/bruker2nifti/blob/master/screenshots/gui_example.jpg)

#### Open the GUI and convert data for non-Python developers
Download the repository as a .zip from the [release page](https://github.com/SebastianoF/bruker2nifti/releases) 
for the stable version or from the [repository home page](https://github.com/SebastianoF/bruker2nifti) for the latest 
development version via **clone or download** green button.
Unzip the donwloaded file and double click on the file `run_setupper_MAC` in the `GUI` folder inside the project.

After the automatic installation of a virtualenvironment with the required libraries, if everything worked 
(see below for troubleshooting), you will find a new file called 'OpenGUIbru2nii' in the code structure. 

Double click on this launcher: will open the graphical user interface. 

Keep the terminal open while doing the conversion, as there you will see the steps and the output of the different
conversion steps.
The launcher can be moved around in the user system. If you need to move the folder where you donwloaded the code, you will need to re-create the 
launcher from the new code location.

#### Further examples and troubleshooting:

Please check the [wiki](https://github.com/SebastianoF/bruker2nifti/wiki) page for more examples and real data applications.
If something went wrong please raise an issue in the [issue page of the repository](https://github.com/SebastianoF/bruker2nifti/issues).

### Testing
Unit testing with [nosetest](http://pythontesting.net/framework/nose/nose-introduction/).
After installing the latest development version, type `nosetests` to run the tests.   
Some of the tests are based on an open dataset Bruker images downloadable with the repo, in the folder 
[test_data](https://github.com/SebastianoF/bruker2nifti/tree/master/test_data).
Current deployment version undergoes continuous integration on [travis-ci](https://travis-ci.org/SebastianoF/bruker2nifti).

### API documentation, further notes and examples <a name="up"></a>
Essential API documentation can be found [here](http://bruker2nifti.readthedocs.io/en/latest/).
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
Matthew Brett (Berkeley Brain Imaging Center).
