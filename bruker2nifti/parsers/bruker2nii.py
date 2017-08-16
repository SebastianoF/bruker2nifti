import argparse
from bruker2nifti.converter import Bruker2Nifti


def main():
    """
    Parser from terminal with:
    $ python2 bruker2nifti -h
    $ python2 bruker2nifti -i input_file_path -o output_file_path
    """

    parser = argparse.ArgumentParser()

    # pfo_study_bruker_input
    parser.add_argument('-i', '--input_study_folder',
                        dest='pfo_input',
                        type=str,
                        required=True,
                        help='Bruker study folder.')

    # pfo_study_nifti_output
    parser.add_argument('-o', '--output_study_folder',
                        dest='pfo_output',
                        type=str,
                        required=True,
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

    # correct_slope = False,
    parser.add_argument('-correct_slope',
                        dest='correct_slope',
                        action='store_true')
    # verbose = 1
    parser.add_argument('-verbose', '-v',
                        dest='verbose',
                        type=int,
                        default=1)

    # Parse the input arguments
    args = parser.parse_args()

    # instantiate a converter:
    bruconv = Bruker2Nifti(args.pfo_input,
                           args.pfo_output,
                           study_name=args.study_name)

    if args.scans_list is not None:
        bruconv.scans_list = args.scans_list
    if args.list_new_name_each_scan is not None:
        bruconv.list_new_name_each_scan = args.list_new_name_each_scan
    bruconv.nifti_version = args.nifti_version
    bruconv.qform_code = args.qform_code
    bruconv.sform_code = args.sform_code
    bruconv.save_human_readable = not args.do_not_save_human_readable
    bruconv.correct_slope = args.correct_slope
    bruconv.verbose = args.verbose

    if parser.add_argument > 0:
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
        print('-------------------------------------------------------- ')
    bruconv.convert()


if __name__ == "__main__":
    main()
