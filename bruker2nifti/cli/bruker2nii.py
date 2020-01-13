import argparse
from datetime import datetime, timedelta
import re
import sys

from bruker2nifti.converter import Bruker2Nifti
import bruker2nifti._utils as utils
from bruker2nifti._metadata import BrukerMetadata


def main():
    """
    Parser from terminal with:
    $ python2 bruker2nifti -h
    $ python2 bruker2nifti -i input_file_path -o output_file_path
    """

    parser = argparse.ArgumentParser()

    # The action to be taken
    #  'convert': Convert images to nifti format (default)
    #  'list': List scans without converting
    parser.add_argument(
        "command",
        type=str,
        nargs="?",
        default="convert",
        choices=["convert", "list"],
        help="Action to take: "
        + "convert - convert to nifti, "
        + "list - list studies and exit",
    )

    # custom helper
    parser.add_argument(
        "-what",
        dest="what",
        action="store_true",
        required=False,
        help="Get more information about the software",
    )

    # pfo_study_bruker_input
    parser.add_argument(
        "-i",
        "--input_study_folder",
        dest="pfo_input",
        type=str,
        required=False,
        help="Bruker study folder.",
    )

    # pfo_study_nifti_output
    parser.add_argument(
        "-o",
        "--output_study_folder",
        dest="pfo_output",
        type=str,
        required=False,
        help="Output folder where the study will be saved.",
    )

    # study_name = None,
    parser.add_argument("-study_name", dest="study_name", default=None)

    # scans_list = None
    # Accepts a list of single digit numbers without any separators. Unable to
    # specify multi-digit scan numbers this way. The --scans argument specified
    # below supersedes this but --scans_list is left in for backwards
    # compatibility. If --scans is also supplied, this paramater is ignored.
    parser.add_argument("-scans_list", dest="scans_list", default=None)

    # A comma or space/tab separated list of scans to operate on
    parser.add_argument("--scans", dest="scans", default=None)

    # list_new_name_each_scan = None,
    parser.add_argument(
        "-list_new_name_each_scan", dest="list_new_name_each_scan", default=None
    )

    # nifti_version = 1,
    parser.add_argument("-nifti_version", dest="nifti_version", type=int, default=1)

    # qform = 1,
    parser.add_argument("-qform_code", dest="qform_code", type=int, default=1)

    # sform= 2,
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

    # sample_upside_down = True,
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

    # ------ Parsing user's input ------ #

    args = parser.parse_args()

    if args.scans:
        scan_list = re.split(r"[^\d]+", args.scans)
    elif args.scans_list:
        scan_list = list(args.scans_list)
    else:
        scan_list = None

    # Check input:
    if args.command == "list":
        list_scans(args.pfo_input)
        sys.exit(0)

    if args.what:
        msg = "Code repository : {} \n" "Documentation   : {}".format(
            "https://github.com/SebastianoF/bruker2nifti",
            "https://github.com/SebastianoF/bruker2nifti/wiki",
        )
        sys.exit(msg)

    if not args.pfo_input or not args.pfo_output:
        sys.exit("Input bruker study [-i] and output folder [-o] required")

    # Instantiate a converter:
    bruconv = Bruker2Nifti(args.pfo_input, args.pfo_output, study_name=args.study_name)

    if scan_list is not None:
        bruconv.scans_list = scan_list
    if args.list_new_name_each_scan is not None:
        bruconv.list_new_name_each_scan = args.list_new_name_each_scan
    elif scan_list is not None:
        # This list of output scan names is populated during object instantiation
        # which causes problems when updating the list of scans to convert after
        # object instantiation (the only way to do it). The following work-around
        # replaces the list of output file names if a list is not explicitly provided.
        # TODO: Restructure the Bruker2Nifti class so that this is not necessary.
        bruconv.list_new_name_each_scan = [
            bruconv.study_name + "_" + ls for ls in scan_list
        ]

    # Basics
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

    print("\nConverter input parameters: ")
    print("-------------------------------------------------------- ")
    print("Study name           : {}".format(bruconv.study_name))
    print("List of scans        : {}".format(bruconv.scans_list))
    print("List of scans names  : {}".format(bruconv.list_new_name_each_scan))
    print("Output NifTi version : {}".format(bruconv.nifti_version))
    print("Output NifTi q-form  : {}".format(bruconv.qform_code))
    print("Output NifTi s-form  : {}".format(bruconv.sform_code))
    print("Save human readable  : {}".format(bruconv.save_human_readable))
    print("Correct the slope    : {}".format(bruconv.correct_slope))
    print("Correct the offset   : {}".format(bruconv.correct_offset))
    print("-------------------------------------------------------- ")
    print("Sample upside down         : {}".format(bruconv.sample_upside_down))
    print("Frame body as frame head   : {}".format(bruconv.frame_body_as_frame_head))
    print("-------------------------------------------------------- ")
    bruconv.convert()

    # Print a warning message for paths with whitespace as it may interfere
    # with subsequent steps in an image analysis pipeline
    if utils.path_contains_whitespace(
        bruconv.pfo_study_nifti_output, bruconv.study_name
    ):
        print("INFO: Output path/filename contains whitespace")


def list_scans(pfo_study):
    study = BrukerMetadata(pfo_study)
    study.parse_subject()
    study.parse_scans()

    # Print study details to the console
    print()
    print("Subject: {}".format(study.subject_data["SUBJECT_name_string"]))
    print(
        "Study Date: {:%Y-%m-%d %H:%M}".format(
            datetime.strptime(
                study.subject_data["SUBJECT_date"], "%Y-%m-%dT%H:%M:%S,%f%z"
            )
        )
    )
    print("-------------------------------------------------------- ")
    print()
    for scan, value in study.scan_data.items():
        print("Scan {}".format(scan))
        print(
            "Protocol: {}".format(value["acqp"]["ACQ_protocol_name"]).ljust(30)
            + "Method: {}".format(value["acqp"]["ACQ_method"]).ljust(30)
            + "Scan Time: {}".format(
                timedelta(seconds=int(round(value["method"]["ScanTime"] / 1000)))
            ).ljust(30)
        )
        print()


if __name__ == "__main__":
    main()
