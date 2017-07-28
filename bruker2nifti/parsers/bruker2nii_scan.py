import argparse
import os

from bruker2nifti.converter import Bruker2Nifti


def main():
    """
    Parser from terminal with
    $ python2 bruker2nifti_study -i input_file_path -o output_file_path
    """

    parser = argparse.ArgumentParser(version=0.0)

    # pfo_input_scan
    parser.add_argument('-i', '--input_scan_folder',
                        dest='pfo_input',
                        type=str,
                        required=True,
                        help='Bruker scan folder.')
    # pfo_output
    parser.add_argument('-o', '--output_scan_folder',
                        dest='pfo_output',
                        type=str,
                        required=True,
                        help='Output folder where the study will be saved.')
    # fin_output = None
    parser.add_argument('--fin_output',
                        dest='fin_output',
                        type=str,
                        default=None)
    # nifti_version = 1,
    parser.add_argument('-nifti_version',
                        dest='nifti_version',
                        type=int,
                        default=1,
                        help='Filename of the nifti output.')
    # qform = 2,
    parser.add_argument('-qform_code',
                        dest='qform_code',
                        type=int,
                        default=2)
    # sform = 1,
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
    # normalise_b_vectors_if_dwi = True,
    parser.add_argument('-normalise_b_vectors_if_dwi',
                        dest='normalise_b_vectors_if_dwi',
                        action='store_true')
    # correct_slope = False,
    parser.add_argument('-correct_slope',
                        dest='correct_slope',
                        action='store_false')
    # verbose = 1
    parser.add_argument('-verbose',
                        dest='verbose',
                        action='store_true')
    # -info_only
    parser.add_argument('-info_only',
                        dest='info_only',
                        action='store_false')
    # -nifti_only
    parser.add_argument('-nifti_only',
                        dest='nifti_only',
                        action='store_false')

    args = parser.parse_args()

    # instantiate a converter:
    bruconv = Bruker2Nifti(os.path.dirname(args.pfo_input), args.pfo_output)
    # get the attributes
    bruconv.nifti_version = args.nifti_version
    bruconv.qform_code = args.qform_code
    bruconv.sform_code = args.sform_code
    bruconv.save_human_readable = args.save_human_readable
    bruconv.correct_slope = args.correct_slope
    bruconv.verbose = args.verbose
    # convert the single:
    bruconv.convert_scan(args.pfo_input, args.pfo_output, nifti_file_name=args.fin_output,
                         create_output_folder_if_not_exists=True)


if __name__ == "__main__":
    main()
