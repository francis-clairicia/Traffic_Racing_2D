# -*- coding: Utf-8 -*

import os
import sys

def set_constant_directory(path, *paths, special_msg=None) -> str:
    all_path = os.path.join(path, *paths)
    if not os.path.isabs(all_path):
        all_path = os.path.join(sys.path[0], all_path)
    if not os.path.isdir(all_path):
        if special_msg is not None:
            raise FileNotFoundError(special_msg)
        raise FileNotFoundError(f"{all_path} folder not found")
    return all_path

def set_constant_file(path, *paths, special_msg=None) -> str:
    all_path = os.path.join(path, *paths)
    if not os.path.isabs(all_path):
        all_path = os.path.join(sys.path[0], all_path)
    if not os.path.isfile(all_path):
        if special_msg is not None:
            raise FileNotFoundError(special_msg)
        raise FileNotFoundError(f"{all_path} not found")
    return all_path