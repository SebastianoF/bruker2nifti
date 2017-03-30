"""
Study: folder structure containing Scans.
Scans are parsed individually and saved in a specular folder structure.

"""
import os
import pprint

from utils import list_files, bruker_read_files
from scan_converter import convert_a_scan, get_PV_version_from_info


def show_study_structure(pfo_study):
    # spacchetta
    # prendi la version da ACQ_sw_version=( 65 ) <PV 5.1> come da dizionario
    #
    print('Study folder structure: ')
    scans_list = list_files(pfo_study)
    print('\n')
    print('List of scans: {}'.format(scans_list))
    pfi_first_scan = os.path.join(pfo_study, scans_list[0])
    acqp = bruker_read_files('acqp', pfi_first_scan)
    print('Version: {}'.format(acqp['ACQ_sw_version'][0]))
