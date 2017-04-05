import argparse
from bruker2nifti.scan_converter import convert_a_scan, write_info, write_to_nifti, get_info_and_img_data


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
    parser.add_argument('-qform',
                        dest='qform',
                        type=int,
                        default=2)
    # sform = 1,
    parser.add_argument('-sform',
                        dest='sform',
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

    if not args.info_only and not args.nifti_only:
        convert_a_scan(args.pfo_input,
                       args.pfo_output,
                       fin_output=args.fin_output,
                       nifti_version=args.nifti_version,
                       qform=args.qform,
                       sform=args.sform,
                       axis_direction=args.axis_direction,
                       save_human_readable=args.save_human_readable,
                       normalise_b_vectors_if_dwi=args.normalise_b_vectors_if_dwi,
                       correct_slope=args.correct_slope,
                       verbose=args.verbose)

    if args.info_only:
        info, img_data = get_info_and_img_data(args.pfo_input)
        write_info(info,
                   args.pfo_output,
                   save_human_readable=args.save_human_readable,
                   separate_shells_if_dwi=False,  # TODO
                   num_shells=3,
                   num_initial_dir_to_skip=None,
                   normalise_b_vectors_if_dwi=True,
                   verbose=args.verbose)

    if args.nifti_only:
        info, img_data = get_info_and_img_data(args.pfo_input)

        if args.fin_output is None:
            fin_output = info['method']['Method'].lower() + \
                         str(info['acqp']['ACQ_time'][0][-11:]).replace(' ', '').replace(':', '_') + '.nii.gz'
        else:
            fin_output = args.fin_output

        write_to_nifti(info,
                       img_data,
                       fin_output,
                       correct_slope=args.correct_slope,
                       correct_shape=False,  # TODO
                       separate_shells_if_dwi=False,  # TODO
                       num_shells=3,
                       num_initial_dir_to_skip=7,
                       nifti_version=args.nifti_version,
                       qform=args.qform,
                       sform=args.sform,
                       axis_direction=args.axis_direction,
                       verbose=args.verbose)

if __name__ == "__main__":
    main()
