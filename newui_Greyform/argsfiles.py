import os,argparse


def _validate_file(path, exts):
    if isinstance(exts, str):
        exts = (exts,)
    p = os.path.expanduser(os.path.expandvars(path))
    ok_ext = any(p.lower().endswith(ext) for ext in exts)
    if not ok_ext or not os.path.isfile(p):
        raise argparse.ArgumentTypeError(f"Invalid or missing file: {path}")
    return p


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("mainui",      type=lambda p: _validate_file(p, ".ui"),                help="Qt Designer .ui")
    parser.add_argument("ifc_file",    type=lambda p: _validate_file(p, ".ifc"),               help="Input IFC")
    parser.add_argument("excel_checklist",  type=lambda p: _validate_file(p, (".xlsx", ".xlsm")),   help="Checklist Excel")
    parser.add_argument("output_excel", type=str,                                              help="Output Excel path (created/overwritten)")
    return parser.parse_args()