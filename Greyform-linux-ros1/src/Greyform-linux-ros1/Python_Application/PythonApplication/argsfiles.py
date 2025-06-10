import os, sys, math, argparse


def validate_file(path, ext):
    if not path.lower().endswith(ext) or not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Invalid or missing file: {path}")
    return path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "excel_file_allocation", type=lambda p: validate_file(p, ".xlsx")
    )
    parser.add_argument(
        "excel_file_checklist", type=lambda p: validate_file(p, ".xlsx")
    )
    parser.add_argument("output_excel", type=str)
    parser.add_argument(
        "--usb_path",
        dest="usb_path",
        type=str,
        default="/mnt/usb/",
        help="Path to the mounted USB directory"
    )
    return parser.parse_args()
