import argparse
import os

from bruker2nifti.converter import Bruker2Nifti


def main_scan():
    """
    Parser from terminal with
    $ python2 bruker2nifti_scan -h
    $ python2 bruker2nifti_scan -i input_file_path -o output_file_path
    """

    parser = argparse.ArgumentParser()

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

    args = parser.parse_args()

    # instantiate a converter:
    bruconv = Bruker2Nifti(os.path.dirname(args.pfo_input), args.pfo_output)
    # get the attributes
    bruconv.nifti_version = args.nifti_version
    bruconv.qform_code = args.qform_code
    bruconv.sform_code = args.sform_code
    bruconv.save_human_readable = not args.do_not_save_human_readable
    bruconv.correct_slope = args.correct_slope
    bruconv.verbose = args.verbose

    if parser.add_argument > 0:
        print('\nConverter parameters: ')
        print('-------------------------------------------------------- ')
        print('Study Folder         : {}'.format(os.path.dirname(args.pfo_input)))
        print('Scan to convert      : {}'.format(os.path.basename(args.pfo_input)))
        print('List of scans        : {}'.format(bruconv.scans_list))
        print('Output NifTi version : {}'.format(bruconv.nifti_version))
        print('Output NifTi q-form  : {}'.format(bruconv.qform_code))
        print('Output NifTi s-form  : {}'.format(bruconv.sform_code))
        print('Save human readable  : {}'.format(bruconv.save_human_readable))
        print('Correct the slope    : {}'.format(bruconv.correct_slope))
        print('-------------------------------------------------------- ')
    # convert the single:
    bruconv.convert_scan(args.pfo_input, args.pfo_output, nifti_file_name=args.fin_output,
                         create_output_folder_if_not_exists=True)


if __name__ == "__main__":
    main_scan()
