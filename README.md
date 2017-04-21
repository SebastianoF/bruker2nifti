## bruker2nifti: conversion from Bruker raw format to nifti

Python 2.7 and Python 3 compatible.

### Table of Contents
+ [Glossary](#glossary)
+ [Code rationale](#rationale)
+ [Common file structure](#file_structure)
+ [Instructions](#instructions)
+ [Utilities](#utilities)
+ [Thanks](#thanks)
+ [Wip](#wip)


### Glossary <a name="glossary"></a>

**study**: a series of acquisition related to the same subject, acquired in the same scanning session
and usually containing multiple scans.
It is provided as a folder structure containing the scans produced with paravision (PV) software.
Patient/subject information are embedded in the study (opposed hierarchy as in the DICOM files). 

**scan**: individual folder image acquired with various protocols. To a scan can corresponds more than one image
as sub-scans or sub-volumes (or both).

**header**: header of the nifti format.

**img_data**: data of the nifti format.

**struct**: intermediate structure (dictionary) aimed at collecting the information from the raw Bruker and
and to progressively creating the nifti images.


### Code rationale <a name="rationale"></a>

Mainly due to lack of information, at the present stage not all the possible
output of the paravision software are
covered. The code deals with file structures
that are assumed as the common one and provided below.
We do not exclude that different settings of the same scanner
and the same PV version
can produce different folder structures.
Therefore the code is written in the most readable way (readability is always
preferred to efficiency, at least at this stage) so that it will be easier for you to modify it
according to your needs.

Further versions may sacrifice readability for the sake of efficiency only
when the standards will be established and tested.

In the range of my possibilities PEP-8 convention is followed.

The code is written an runs in python 2.7 (cross compatibility with python 3 is implemented when possible).
The choice of Python programming language is after personal preferences, the availability of nibabel library,
the availability of dictionaries (mapping) type and numpy arrays, that appears to be
the best option to parse the textfiles of Paravision into easily accessible structures while 
keeping the same original name convention.  


### Common file structure <a name="file_structure"></a>

A study structure in ParaVision 5 can be:
```
└── StudyName
    ├── 1
    ├── 2
    ├── 3
    ├── 4
    ├── 5
    ├── 6
    ├── AdjResult
    ├── AdjStatePerStudy
    └── subject
```
where each folder numbered 1 to 6 is a **scan**, whose sub-structure can be
```
├── 3
│   ├── AdjRefgProfiles.dat
│   ├── AdjStatePerScan
│   ├── acqp
│   ├── fid
│   ├── method
│   ├── pdata
│   │   └── 1
│   │       ├── 2dseq
│   │       ├── d3proc
│   │       ├── id
│   │       ├── meta
│   │       ├── procs
│   │       ├── reco
│   │       └── visu_pars
│   ├── pulseprogram
│   ├── spnam0
│   ├── spnam23
│   └── uxnmr.par
```
Under pdata 

The Bruker structure contains more information than the one required to fill a
nifti header (scanner setting, location, users, sample or subject scanned biometrics
can appear in the Bruker raw data, if filled when scanning the data).
To obtain relevant information to fill the nifti header (and b-values and b-vectors if any) 
we can restrict our attention towards
**method**, **acqp**, **reco** and **visu_pars**. The img_data is stored in the file **2dseq**.


A study structure in paravision 6 can be:
```
└── StudyName
    ├── 1
    ├── 2
    ├── 3
    ├── 4
    ├── 5
    ├── AdjResult
    ├── AdjStatePerStudy
    ├── ResultState
    ├── ScanProgram.scanProgram
    └── subject
```
where each folder numbered 1 to 6 is a scan, whose structure can be
```
├── 3
│   ├── AdjStatePerScan
│   ├── acqp
│   ├── configscan
│   ├── fid
│   ├── method
│   ├── pdata
│   │   ├── 1
│   │   │   ├── 2dseq
│   │   │   ├── id
│   │   │   ├── procs
│   │   │   ├── reco
│   │   │   ├── roi
│   │   │   └── visu_pars
│   │   └── 2
│   │       ├── 2dseq
│   │       ├── d3proc
│   │       ├── id
│   │       ├── isa
│   │       ├── procs
│   │       ├── roi
│   │       └── visu_pars
│   ├── pulseprogram
│   ├── specpar
│   ├── uxnmr.info
│   ├── uxnmr.par
│   └── visu_pars
```
Information to fill the header (and b-values and b-vectors if any) are
again in the files
method, acqp, reco and visu_pars. The img_data is stored in the file 2dseq.



## Code structure:

+ **bruker2nifti._cores.py** contains the core of the parser. It is not possible to disentangle the information of some
of the raw Brukert files and parse them individually with individual parsers to create the nifti. Data useful to 
build the nifti are stored in an intermediate structure, called struct (yes, I know...), that is than used to
create and save the nifti image(s) and the file.
+ **bruker2nifti._utils.py** contains the utils, whose core is the method indian_file_parser component of the bridge 
parsing the text contained in the main raw bruker structure into dictionaries.
+ **bruker2nifti.scan_converter.py** contains the code to convert a single scan.
The main method convert_a_scan put togheter the main components get_info_and_img_data, write_info and write_to_nifti.
+ **bruker2nifti.study_converter.py** contains the code to convert a study.
The main method convert_a_study browse the study folder and apply convert_a_scan to all the scans contained.
Results are saved in a folder structure homologous to bruker study with the files converted to nifti.
+ The folder **parsers** contains some parsers that can be used to access the method directly
from command line.

<!---
## Examples:
--->

### Instructions <a name="instructions"></a>

+ Install python requirements in requirements.txt with
```
pip install -r requirements.txt
```

in a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).


+ activate the virtualenvironment and go in the root folder of the repository.

+ To install as a library (option 1):
```
python setup.py sdist

cd ../

pip install bruker2nifti/dist/bruker2nifti-XX.tar.gz
```
where XX is the chosen version.

+ To install as a library (option 2):
```
python setup.py install
```
+ To install in [development mode](http://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode) (option 1) 
```
python setup.py develop
```

+ To install in development mode (option 2, suggested)
```
pip install -e .
```

+ To verify that it has been installed in your libraries, see the list of libraries installed:
```
pip list
```
+ To verify that that it works (at least the setup):
```    
python
import bruker2nifti
```

To uninstall:
```
pip uninstall bruker2nifti
```
To delete the library in the virtualenv in case something really wrong happen and pip uninstall will be able to work correctly:
```
sudo rm -rf /path_to_site_packages_in_virtualenv/site-packages/bruker2nifti*
```

### Utilities <a name="utilities"></a>

+ [official documentation nifti format](https://nifti.nimh.nih.gov/nifti-1)
+ [non-official documentation nifti format](https://brainder.org/2012/09/23/the-nifti-file-format/)
+ [nibabel python library](http://nipy.org/nibabel/)

## Thanks <a name="thanks"></a>

Thanks to Bernard Siow (Centre for Advanced Biomedical Imaging, UCL) and Willy Gsell (Department of Imaging and Pathology, KU Leuven).


<!---
### Note about the differencies between paravision 5 and 6:

Examples of differencies in the text-files:

Under **methods** the attribute `PVM_SpatDimEnum` in pv5 appears as: 

```
## $PVM_SpatDimEnum=3D
```

whereas in pv6:
 
```
## $PVM_SpatDimEnum=<3D>

```
$ACQ_time:
paravision 5: 
##$ACQ_time=( 24 )
<20:19:47  1 Sep 2016>

paravision 6: 
##$ACQ_time=<2017-03-07T19:56:48,575+0100>



--->


## WIP <a name="wip"></a>
Expose Slope as single file.
Parsers missing, good testing framework, individual shells DWI saving options, affine directions parsing 
(Bruker convention still to explore).   
