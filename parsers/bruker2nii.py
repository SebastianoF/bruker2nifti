import argparse
from bruker2nifti.converter import Bruker2Nifti


def main():
    """
    Parser from terminal with:
    $ python2 bruker2nifti_study -i input_file_path -o output_file_path
    """

    parser = argparse.ArgumentParser(version=0.0)

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

    # list_new_nifti_file_names = None,
    parser.add_argument('-list_new_nifti_file_names',
                        dest='list_new_nifti_file_names',
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
                        default=2)

    # sform= 1,
    parser.add_argument('-sform_code',
                        dest='sform_code',
                        type=int,
                        default=1)

    # axis_direction = (-1, -1, 1),
    parser.add_argument('-axis_direction',
                        dest='axis_direction',
                        type=tuple,
                        default=(-1, -1, 1))

    # save_human_readable = True,
    parser.add_argument('-save_human_readable',
                        dest='save_human_readable',
                        action='store_true')

    # correct_slope = False,
    parser.add_argument('-correct_slope',
                        dest='correct_slope',
                        action='store_false')
    # verbose = 1
    parser.add_argument('-verbose', '-v',
                        dest='verbose',
                        action='store_true')

    # Parse the input arguments
    args = parser.parse_args()

    # instantiate a converter:
    bruconv = Bruker2Nifti(args.pfo_input,
                           args.pfo_output,
                           study_name=args.study_name)

    bruconv.scans_list = args.scans_list
    bruconv.list_new_name_each_scan = args.list_new_name_each_scan
    bruconv.list_new_nifti_file_names = args.list_new_nifti_file_names
    bruconv.nifti_version = args.nifti_version
    bruconv.qform_code = args.qform_code
    bruconv.sform_code = args.sform_code
    bruconv.save_human_readable = args.save_human_readable
    bruconv.correct_slope = args.correct_slope
    bruconv.verbose = args.verbose

    bruconv.convert()

if __name__ == "__main__":
    main()