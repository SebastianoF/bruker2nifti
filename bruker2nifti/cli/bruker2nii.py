import sys
import argparse
from bruker2nifti.converter import Bruker2Nifti


def main():
    """
    Parser from terminal with:
    $ python2 bruker2nifti -h
    $ python2 bruker2nifti -i input_file_path -o output_file_path
    """

    parser = argparse.ArgumentParser()

    # custom helper
    parser.add_argument('-what',
                        dest='what',
                        action='store_true',
                        required=False,
                        help='Get more information about the software')

    # pfo_study_bruker_input
    parser.add_argument('-i', '--input_study_folder',
                        dest='pfo_input',
                        type=str,
                        required=False,
                        help='Bruker study folder.')

    # pfo_study_nifti_output
    parser.add_argument('-o', '--output_study_folder',
                        dest='pfo_output',
                        type=str,
                        required=False,
                        help='Output folder where the study will be saved.')

    # study_name = None,
    parser.add_argument('-study_name',
                        dest='study_name',
                        default=None)

    # scans_list = None
    parser.add_argument('-scans_list',
                        dest='scans_list',
                        default=None)

    # list_new_name_each_scan = None,
    parser.add_argument('-list_new_name_each_scan',
                        dest='list_new_name_each_scan',
                        default=None)

    # nifti_version = 1,
    parser.add_argument('-nifti_version',
                        dest='nifti_version',
                        type=int,
                        default=1)

    # qform = 2,
    parser.add_argument('-qform_code',
                        dest='qform_code',
                        type=int,
                        default=1)

    # sform= 1,
    parser.add_argument('-sform_code',
                        dest='sform_code',
                        type=int,
                        default=2)

    # do_not_save_human_readable = False,
    parser.add_argument('-do_not_save_human_readable',
                        dest='do_not_save_human_readable',
                        action='store_true')

    # correct_slope = True,
    parser.add_argument('-correct_slope',
                        dest='correct_slope',
                        action='store_true')

    # correct_offset = True,
    parser.add_argument('-correct_offset',
                        dest='correct_offset',
                        action='store_true')

    # correct_offset = True,
    parser.add_argument('-sample_upside_down',
                        dest='sample_upside_down',
                        action='store_false')

    # correct_offset = True,
    parser.add_argument('-frame_body_as_frame_head',
                        dest='frame_body_as_frame_head',
                        action='store_false')

    # verbose = 1
    parser.add_argument('-verbose', '-v',
                        dest='verbose',
                        type=int,
                        default=1)

    # ------ Parsing user's input ------ #

    args = parser.parse_args()

    # Check input:
    if args.what:
        msg = 'Code repository : {} \n' \
              'Documentation   : {}'.format('https://github.com/SebastianoF/bruker2nifti',
                                            'https://github.com/SebastianoF/bruker2nifti/wiki')
        sys.exit(msg)

    if not args.pfo_input or not args.pfo_output:
        sys.exit('Input bruker study [-i] and output folder [-o] required')

    # Instantiate a converter:
    bruconv = Bruker2Nifti(args.pfo_input,
                           args.pfo_output,
                           study_name=args.study_name)

    if args.scans_list is not None:
        bruconv.scans_list = args.scans_list
    if args.list_new_name_each_scan is not None:
        bruconv.list_new_name_each_scan = args.list_new_name_each_scan

    # Basics
    bruconv.nifti_version       = args.nifti_version
    bruconv.qform_code          = args.qform_code
    bruconv.sform_code          = args.sform_code
    bruconv.save_human_readable = not args.do_not_save_human_readable
    bruconv.correct_slope       = args.correct_slope
    bruconv.correct_offset      = args.correct_offset
    bruconv.verbose             = args.verbose
    # Sample position
    bruconv.sample_upside_down       = args.sample_upside_down
    bruconv.frame_body_as_frame_head = args.frame_body_as_frame_head

    print('\nConverter input parameters: ')
    print('-------------------------------------------------------- ')
    print('Study name           : {}'.format(bruconv.study_name))
    print('List of scans        : {}'.format(bruconv.scans_list))
    print('List of scans names  : {}'.format(bruconv.list_new_name_each_scan))
    print('Output NifTi version : {}'.format(bruconv.nifti_version))
    print('Output NifTi q-form  : {}'.format(bruconv.qform_code))
    print('Output NifTi s-form  : {}'.format(bruconv.sform_code))
    print('Save human readable  : {}'.format(bruconv.save_human_readable))
    print('Correct the slope    : {}'.format(bruconv.correct_slope))
    print('Correct the offset   : {}'.format(bruconv.correct_offset))
    print('-------------------------------------------------------- ')
    print('Sample upside down         : {}'.format(bruconv.sample_upside_down))
    print('Frame body as frame head   : {}'.format(bruconv.frame_body_as_frame_head))
    print('-------------------------------------------------------- ')
    bruconv.convert()


if __name__ == "__main__":
    main()
