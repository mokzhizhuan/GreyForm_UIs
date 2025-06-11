import os, sys, math, argparse


def validate_file(path, ext):
    if not path.lower().endswith(ext) or not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"Invalid or missing file: {path}")
    return path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("mainui", type=lambda p: validate_file(p, ".ui"))
    parser.add_argument("output_stl", type=lambda p: validate_file(p, ".stl"))
    parser.add_argument("floor_stl", type=lambda p: validate_file(p, ".stl"))
    parser.add_argument("excel_file", type=lambda p: validate_file(p, ".xlsx"))
    parser.add_argument("output_excel", type=str)
    return parser.parse_args()
