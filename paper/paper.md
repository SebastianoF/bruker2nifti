---
title: 'Bruker2nifti: Magnetic Resonance Images converter from Bruker ParaVision to Nifti format'
tags:
  - Medical Imaging
  - Bruker
  - Nifti
  - Format converter
authors:
 - name: Sebastiano Ferraris
   orcid: 0000-0001-9279-4765
   affiliation: 1
 - name: Dzhoshkun Ismail Shakir
   orcid: 0000-0003-3009-4178
   affiliation: 1
 - name: Johannes Van Der Merwe
   orcid: 0000-0002-1381-4033
   affiliation: 2
 - name: Willy Gsell
   orcid: 0000-0001-7334-6107
   affiliation: 3
 - name: Jan Deprest
   orcid: 0000-0002-4920-945X
   affiliation: 1,2,4
 - name: Tom Vercauteren
   orcid: 0000-0003-1794-0456
   affiliation: 1,2,4
affiliations:
 - name: Translational Imaging Group, Centre for Medical Image Computing (CMIC), Department of Medical Physics and Bioengineering, University College London, Malet Place Engineering Building, London, WC1E 6BT, UK
   index: 1
 - name: Department of Development and Regeneration, Organ System Cluster, Group Biomedical Sciences, KU Leuven, Belgium.
   index: 2
 - name: Biomedical MRI, Department of Imaging and Pathology, KU Leuven, Belgium.
   index: 3
 - name: Wellcome/EPSRC Centre for Interventional and Surgical Sciences, University College London, UK.
   index: 4
date: 28 July 2017
bibliography: paper.bib
---


# Motivations and Summary

In clinical and pre-clinical research involving medical images, the first step following a Magnetic Resonance Imaging dataset acquisition, usually entails the image conversion from the native scanner format to a format suitable for the intended analysis. 
The [Bruker ParaVision](https://www.bruker.com/products/mr/preclinical-mri/software/service-support.html) proprietary software is not currently providing the tools for the data conversion to a suitable open formats for research, such as nifti [@cox2004sort], for which most of the available tools for medical image analysis are implemented. 

For this purpose we have designed and developed [bruker2nifti](https://github.com/SebastianoF/bruker2nifti), a pip-installable Python tool provided with a Graphical User Interface to convert from the native MRI Bruker format 
to the nifti format, without any intermediate step through the DICOM standard formats [@mustra2008overview].

Bruker2nifti is intended to be a tool to access the data structure and to parse every Parameter Files of the Bruker ParaVision format into python dictionaries, to select the relevant information to fill the Nifti header and data volume. Lastly it is meant to be a starting point where to integrate possible future variations in Bruker hardware and ParaVision software future releases.

# Acknowledgements

This work was supported by Wellcome / Engineering and Physical Sciences Research Council (EPSRC) [WT101957; NS/A000027/1; 203145Z/16/Z]. Sebastiano Ferraris is supported by the EPSRC-funded UCL Centre for Doctoral Training in Medical Imaging (EP/L016478/1) and Doctoral Training Grant (EP/M506448/1).
Hannes Van Der Merwe is co-funded with support of the Erasmus + Programme of the European Union (Framework Agreement number: 2013-0040). This publication reflects the views only of the author, and the Commission cannot be held responsible for any use which may be made of the information contained therein. 
We would also like to thank all the people who directly contributed to bruker2nifti with offline hints and suggestions: Bernard Siow (Centre for Advanced Biomedical Imaging, University College London), Chris Rorden (McCausland Center for Brain Imaging, University of South Carolina) and Mattew Brett (Berkeley Brain Imaging Center).


# References





