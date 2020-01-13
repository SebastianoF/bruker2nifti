import argparse
import os

from bruker2nifti.converter import Bruker2Nifti
import bruker2nifti._utils as utils


def main_scan():
    """
    Parser from terminal with
    $ python2 bruker2nifti_scan -h
    $ python2 bruker2nifti_scan -i input_file_path -o output_file_path
    """

    parser = argparse.ArgumentParser()

    # pfo_input_scan
    parser.add_argument(
        "-i",
        "--input_scan_folder",
        dest="pfo_input",
        type=str,
        required=True,
        help="Bruker scan folder.",
    )
    # pfo_output
    parser.add_argument(
        "-o",
        "--output_scan_folder",
        dest="pfo_output",
        type=str,
        required=True,
        help="Output folder where the study will be saved.",
    )
    # fin_output = None
    parser.add_argument("--fin_output", dest="fin_output", type=str, default=None)
    # nifti_version = 1,

    parser.add_argument("-nifti_version", dest="nifti_version", type=int, default=1)
    # qform = 1,
    parser.add_argument("-qform_code", dest="qform_code", type=int, default=1)
    # sform = 2,
    parser.add_argument("-sform_code", dest="sform_code", type=int, default=2)

    # do_not_save_human_readable = False,
    parser.add_argument(
        "-do_not_save_human_readable",
        dest="do_not_save_human_readable",
        action="store_true",
    )

    # correct_slope = False,

    parser.add_argument("-correct_slope", dest="correct_slope", action="store_true")

    # correct_offset = False,
    parser.add_argument("-correct_offset", dest="correct_offset", action="store_true")

    # sample_upside_down = False,
    parser.add_argument(
        "-sample_upside_down", dest="sample_upside_down", action="store_true"
    )

    # frame_body_as_frame_head = False,
    parser.add_argument(
        "-frame_body_as_frame_head",
        dest="frame_body_as_frame_head",
        action="store_true",
    )

    # verbose = 1
    parser.add_argument("-verbose", "-v", dest="verbose", type=int, default=1)

    args = parser.parse_args()

    # instantiate a converter:
    bruconv = Bruker2Nifti(os.path.dirname(args.pfo_input), args.pfo_output)
    # get the attributes
    bruconv.nifti_version = args.nifti_version
    bruconv.qform_code = args.qform_code
    bruconv.sform_code = args.sform_code
    bruconv.save_human_readable = not args.do_not_save_human_readable
    bruconv.correct_slope = args.correct_slope
    bruconv.correct_offset = args.correct_offset
    bruconv.verbose = args.verbose
    # Sample position
    bruconv.sample_upside_down = args.sample_upside_down
    bruconv.frame_body_as_frame_head = args.frame_body_as_frame_head

    if parser.add_argument > 0:

        print("\nConverter parameters: ")
        print("-------------------------------------------------------- ")
        print("Study Folder         : {}".format(os.path.dirname(args.pfo_input)))
        print("Scan to convert      : {}".format(os.path.basename(args.pfo_input)))
        print("List of scans        : {}".format(bruconv.scans_list))
        print("Output NifTi version : {}".format(bruconv.nifti_version))
        print("Output NifTi q-form  : {}".format(bruconv.qform_code))
        print("Output NifTi s-form  : {}".format(bruconv.sform_code))
        print("Save human readable  : {}".format(bruconv.save_human_readable))
        print("Correct the slope    : {}".format(bruconv.correct_slope))
        print("Correct the offset   : {}".format(bruconv.correct_offset))
        print("-------------------------------------------------------- ")
        print("Sample upside down         : {}".format(bruconv.sample_upside_down))
        print(
            "Frame body as frame head   : {}".format(bruconv.frame_body_as_frame_head)
        )
        print("-------------------------------------------------------- ")

    # convert the single:
    bruconv.convert_scan(
        args.pfo_input,
        args.pfo_output,
        nifti_file_name=args.fin_output,
        create_output_folder_if_not_exists=True,
    )

    # Print a warning message for paths with whitespace as it may interfere
    # with subsequent steps in an image analysis pipeline
    if utils.path_contains_whitespace(
        bruconv.pfo_study_nifti_output, bruconv.study_name
    ):
        print("INFO: Output path/filename contains whitespace")


if __name__ == "__main__":
    main_scan()
