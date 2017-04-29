## bruker2nifti: medical image converter - from MRI Bruker to nifti

Python 2.7 and Python 3 compatible. Most of the time [PEP-8](https://www.python.org/dev/peps/pep-0008/) coding convention.

### Table of Contents
+ [Definitions](#def)
+ [Code rationale](#rationale)
+ [Use with caution](#caution)
+ [Common file structure](#file_structure)
+ [Example](#example)
+ [Instructions](#instructions)
+ [ParaVision versions 5 and 6 note](#pv56)
+ [Wip](#wip)
+ [Thanks](#thanks)

### Definitions <a name="def"></a>

**study**: a series of acquisition related to the same subject, acquired in the same scanning session
and usually containing multiple scans.
It is provided as a folder structure containing the scans produced with paravision (PV) software.
Patient/subject information are embedded in the study (opposed hierarchy as in the DICOM files). 

**scan or experiment, sub-scans and sub-volumes**: individual folder image acquired with various protocols. 
To a scan can belong more than one 
processed image, or reconstruction. Each processed image can be a single volume or can contain more than one sub-volume 
embedded in the same processed image.

**header**: header of the nifti format.

**img_data**: data of the nifti format, stored in a 2d or 3d matrix.

**struct**: intermediate structure (dictionary), proposed in this code, aimed at collecting the information from 
the raw Bruker and to progressively creating the nifti images.


### Code rationale <a name="rationale"></a>

The code is written an runs in python 2.7 (cross compatibility with python 3 is implemented when possible but 
not always tested).
The choice of Python programming language is after personal preferences, the availability of nibabel library,
the availability of dictionaries (mapping) type and numpy arrays, that appears to be
the best option to parse the textfiles of Paravision into easily accessible structures while 
keeping the same original name convention.  


### Use with caution <a name="caution"></a>

Mainly due to lack of information, at the present stage not all the possible
output of the ParaVision software are
covered (ParaVision version or scanner settings). Your data may not be correctly converted. 
Use it with caution, and to not use it just as a black box.
The code is written in the most readable way, and has a good deal of comments, 
to make it easier for you to modify it
according to your needs and to contribute to make it more general.


### Bruker ParaVision file structure <a name="file_structure"></a>

***root_ParaVision/study_name/experiment_numbers*/pdata/*processed_image_numbers***

+ *root_ParaVision*: arbitrary path where the ParaVision data are stored.
+ *study_name*: name of the study, related to the same subject. Information related to the subject are in 
the root_ParaVision/study_name/file subject
+ *experiment_numbers* (or scan_numbers): set of folders named with '1', '2', ... containing each experiment or scan.
+ pdata: (short for processed data) folder created by ParaVision containing a new hierarchy of folders named with '1', '2', ... called here *sub-scans*
+ *processed_image_numbers*: set of folders named with '1', '2', ... containing sub-scans, having in common the 
same scan modality and scanner configuration. Each sub scan has its own *visu_pars* data file (see below).

A Study structure in ParaVision can be:
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
where each folder numbered 1 to 6 is an **experiment** or **scan**, whose sub-structure can be
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
Under pdata the (unzipped) file **2dseq** contains the information of the image volume. **d3proc** contains a summary of 
the relevant information relate to the volume (lacking of orientation and resolution, among others; beware some converter uses
only the d3proc to reconstruct the new image. In ParaVision version 6 some sub-scans may not have the d3proc file, as in the structure example below). 

The Bruker structure contains more information than the one required to fill a
nifti header (unique identifier, scanner setting, location, users, sample or subject scanned biometrics
can appear in the Bruker raw data, if filled when scanning the data).
To obtain relevant information to fill the nifti header (and b-values and b-vectors if any) 
we can restrict our attention towards only some parameter files other than the 2dseq. These are:
**method**, **acqp**, **reco** and **visu_pars**.

When the ParaVision embedded DICOM converter is used, only the **visu_pars** file is considered by the DICOM-converter.
For some scanner configuration, this may not contain the resolution of the scan.

## How to use the converter - Example <a name="example"></a>

#### From command line

Type
```
python parsers/bruker2nii -h
```
for help and see the options.

You can convert a study from the parsers without any installation, with 
```
python parsers/bruker2nii -i path/to/bruker/study -o path/to/output/folder
```
To convert a scan, to modify the code or to call the code with an import within other python module it is recommended to
install the python package as a library following the next instructions.

#### In a python module

You can add the bruker2nifti folder in your PYTHONPATH, or you can install 
the converter as a library (next section more instructions on this).

To convert a Study:
```
from bruker2nifti.study_converter import convert_a_study

path_folder_study = '/Volumes/Examples/study_name'
path_folder_output = '/Volumes/Examples/folder'

convert_a_study(path_folder_study,
                path_folder_output,
                study_name='my_stu,
                scans_list=None,
                list_new_name_each_scan=None,
                list_new_nifti_file_names=None,
                nifti_version=1,
                qform=2,
                sform=1,
                save_human_readable=True,
                normalise_b_vectors_if_dwi=True,
                save_b0_if_dwi=True,
                correct_slope=False,
                verbose=1
                )

```

To convert a Scan:
```
from bruker2nifti.scan_converter import convert_a_scan


path_folder_scan = '/Volumes/Examples/study_name/3'
path_folder_output = '/Volumes/Examples/folder'

# conversion
convert_a_scan(path_folder_scan, 
               path_folder_output, 
               create_output_folder_if_not_exists=True,
               nifti_version=1,
               qform=2,
               sform=1,
               correct_slope=True,
               fin_scan='scan3',
               normalise_b_vectors_if_dwi=True,
               save_b0_if_dwi=True,
               save_human_readable=True,
               separate_shells_if_dwi=False,
               num_shells=3,
               num_initial_dir_to_skip=None,
               verbose=1)

```


## Installation instructions <a name="instructions"></a>

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
To delete the library in the virtualenv in case something really wrong happen (should not, just in case...) and pip uninstall will not be able to work correctly:
```
sudo rm -rf /path_to_site_packages_in_virtualenv/site-packages/bruker2nifti*
```

## Code structure:

+ **bruker2nifti._cores.py** contains the core of the parser. It is not possible to disentangle the information of some
of the raw Bruker files and parse them individually with individual parsers to create the nifti. Data useful to 
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


### Utilities <a name="utilities"></a>

+ [official documentation nifti format](https://nifti.nimh.nih.gov/nifti-1).
+ [non-official documentation nifti format](https://brainder.org/2012/09/23/the-nifti-file-format/).
+ [nibabel python library](http://nipy.org/nibabel/).
+ [bruker format info](http://imaging.mrc-cbu.cam.ac.uk/imaging/FormatBruker): one of the few places where to find 
information about Bruker format, other than the official documentation stored under 
<PvInstDir>/prog/docu/english/pvman/D/Docs/D02_PvParams.pdf of the ParaVision installation. 
+ [pvconv](https://github.com/matthew-brett/pvconv): from Bruker to Analyze, Perl.
+ [Bru2Nii](https://github.com/neurolabusc/Bru2Nii): from Bruker to Nifti, Pascal.
+ [mpi](https://github.com/francopestilli/mpi): from Bruker to Vistasoft in Matlab.

## Note about ParaVision versions 5 and 6 <a pv56="wip"></a>:

Keeping in mind the caution note above, the converter can deal with ParaVision version 5 and 6 in the parsing of the parameters files .

#### Examples of differencies between 5 and 6 in the parameters files are:

Under **methods** the attribute `PVM_SpatDimEnum` in pv5 appears as: 

```
##$PVM_SpatDimEnum=3D
```
whereas in pv6:
 
```
##$PVM_SpatDimEnum=<3D>

```

Under **methods** the attribute `ACQ_time` in pv5 appears as:

```
##$ACQ_time=( 24 )
<20:19:47  1 Sep 2016>

```
whereas in pv6 is:
```
##$ACQ_time=<2017-03-07T19:56:48,575+0100>
```

 
## WIP <a name="wip"></a>

Parsers for a single scan/experiment only drafted. Missing good testing framework. Individual shells DWI saving options. 
Affine directions for Bruker data (Bruker convention still to be explored) to nifti yet to be understand.   


## Thanks <a name="thanks"></a>

Thanks to Bernard Siow (Centre for Advanced Biomedical Imaging, UCL) and Willy Gsell (Department of Imaging and Pathology, KU Leuven).

