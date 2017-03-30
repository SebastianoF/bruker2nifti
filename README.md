## Conversion from bruker format to nifti

### Glossary:

study: folder structure containing the scans produced with paravision (PV) software.
scan: individual image acquired with various protocols.
header: header of the nifti format.
img_data: data of the nifti format.
info: dictionary aimed at collecting the information from the raw Bruker and
store them to the nifti header and to reshape img_data.

### Code rationale:

Mainly due to lack of information, at the present stage not all the possible
output of the paravision software are
covered. The code deals with file structures
that are assumed as the common one and provided below.
We do not exclude that different settings of the same scanner
and the same PV version
can produce different folder structures.
Therefore the code is written in the most readable way (readability is always
preferred to efficiency) so that you will be hopefully able to modify it
according to your needs.

Further versions may sacrifice readability for the sake of efficiency only
the general enough case will be covered.

In the range of my possibilities PEP-8 convention was followed.

### Common file structure:

Usual structure of a study (paravision 5) is:

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

where each folder numbered 1 to 6 is a scan, whose usual structure is

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

Information to fill the header (and b-values and b-vectors if any) are in the files
method, acqp, reco and visu_pars. The img_data is stored in the file 2dseq.


Usual structure of a study (paravision 6) is:

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

where each folder numbered 1 to 6 is a scan, whose usual structure is

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

Information to fill the header (and b-values and b-vectors if any) are
again in the files
method, acqp, reco and visu_pars. The img_data is stored in the file 2dseq.


## Code structure:


## Examples:



## Instructions

+ Install python requirements in requirements.txt with

    `pip install -r requirements.txt`

in a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).


+ activate the virtualenvironment and go in the root folder of the repository.

+ To install as a library (option 1):

`python setup.py sdist`

`cd ../`

`pip install LabelManager/dist/LabelsManager-XX.tar.gz`

where XX is the chosen version.

+ To install as a library (option 2):

`python setup.py install`

+ To install in [development mode](http://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode) (option 1) 

`python setup.py develop`

+ To install in development mode (option 2)

`pip install -e .`

+ To verify that it works:

`python`

`from labels_manager.main import LabelsManager as LM`

`lm = LM('/some/folder')`

To uninstall:

 `pip uninstall LabelsManager`
 
To delete the library in the virtualenv in case something really wrong happen and pip uninstall will not work correctly:
  
  `sudo rm -rf /path_to_site_packages_in_virtualenv/site-packages/LabelsManager*`
 

## Utilities:
websites...


# Thanks
Thanks to Bernard Siow (Centre for Advanced Biomedical Imaging, UCL) and Willy Gsell (Department of Imaging and Pathology, KU Leuven).
