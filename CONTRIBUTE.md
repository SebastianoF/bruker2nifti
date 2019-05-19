# Contributing to bruker2nifti

Thanks for contributing to bruker2nifti!

In any study using MR Bruker scanners, there are multiple scanner settings, 
ParaVision versions and MRI protocols involved. Take this into consideration when proposing a new contribution.

## Code of Conduct

This project adopts the [Covenant Code of Conduct](https://contributor-covenant.org/). 
This can be shortly summarised with: "please be polite and to not go off topic." 
 
## What you should know 

You should be familiar with the bruker ParaVision folder structure and the NifTi (1 and 2)
format.
A starting point can be the links in the [README](https://github.com/SebastianoF/bruker2nifti/blob/master/README.md) 
and the [wiki page](https://github.com/SebastianoF/bruker2nifti/wiki).

The bruker2nifti code structure and API is as simple and straight as possible and the
 code is as commented as possible to make collaboration easier. See in particular this 
[wiki-page](https://github.com/SebastianoF/bruker2nifti/wiki/Code-rationale,-definitions-and-structure). 

## Contributions: Questions, bugs, issues and new features 

+ For any issue bugs or question related to the code, please raise an issue in the 
[bruker2nifti issue page](https://github.com/SebastianoF/bruker2nifti/issues).

+ Propose here as well improvements suggestions and new features.

+ **Please use a new issue for each thread:** make your issue re-usable and reachable by other users that may have 
encountered a similar problem.

+ When raise an issue, please follow the 
[proposed definitions](https://github.com/SebastianoF/bruker2nifti/wiki/Code-rationale,-definitions-and-structure).

+ If you forked the repository and made some contributions that you would like to integrate in the git master branch, 
you can do a [git pull request](https://yangsu.github.io/pull-request-tutorial/). Please **check tests are all passed** 
before this (please follow the [test guidelines](https://github.com/SebastianoF/bruker2nifti/wiki/Code-Testing-and-Continuous-Integration-with-Nosetest)).

## New feature guidelines

bruker2nifti converts a Bruker ParaVision data structure into an initial nifti image, with the less possible 
extra input from the user. It is intended to provides the first step for a subsequent image processing pipeline. 

Every extra processing after the conversion, that are typically integrated into a pipeline, such as:
+ Bias field correction,
+ Intensities normalisation,
+ Automatic segmentation or skull stripping,
+ Otsu background thresholding,
+ Specific reorientation,
+ Tensor fitting
+ ...

are not considered part of the converter, as too dependent on the specific-user needs.

By new feature we mean the possibility of converting data from ParaVision versions different from the one considered,
  modalities different from the one considered, providing different decision options that the one currently provided,
  as well as correcting bugs and improving the testing.
  
## Styleguides

+ The code follows the [PEP-8](https://www.python.org/dev/peps/pep-0008/) style convention. 
+ Please follow the [ITK standard prefix commit message convention](https://itk.org/Wiki/ITK/Git/Develop) for commit messages. 
+ Please use the prefix `pfi_` and `pfo_` for the variable names containing path to files and path to folders respectively

## To-Do list

See the [todo wiki-page](https://github.com/SebastianoF/bruker2nifti/wiki/Work-in-progress-and--Future-work) 
for the directions the next releases are oriented to go.
