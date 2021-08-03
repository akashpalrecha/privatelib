from argparse import Namespace
from pathlib import Path
import zipfile
import os
import json
import mimetypes
from pdb import set_trace
import gc

try:
    import numpy as np
except:
    print("NumPy not available.")
    pass
try:
    import matplotlib.pyplot as plt
except:
    print("Matplotlib not available.")
    pass


Path.ls = lambda x: list(x.iterdir())
Path.str = lambda x: str(x)

def get_files_by_ext(path:Path, ext:str, check_if_valid_file:bool=True, size_thresh=5):
    """
    gets all the files in a `path` ending in `ext`
    path: Path to folder containing files
    ext: extension to filter files by
    """
    path = Path(path)
    return filter(lambda x: x.suffix.lower().endswith(ext) and (is_valid_file(x, thresh=size_thresh) if check_if_valid_file else True), 
                  path.iterdir())
    

def zipdir(path, zipname):
    """
    adds files in `path` to a compressed zip `zipname`
    path: path containing files to add to zip
    zipname: path to output zip file
    """
    path = str(path)
    zipf = zipfile.ZipFile(str(zipname), 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()
    

def is_image(path:Path):
    res = mimetypes.guess_type(str(path))[0]
    return res is not None and 'image' in res

def is_valid_file(path:Path, thresh=5):
    """
    Checks if file at `path` exists and has minimum size of `thresh`
    """
    path = Path(path)
    if path.exists() and path.lstat().st_size > thresh:
        return True
    else: return False

def get_file_type(x):
    return mimetypes.guess_type(str(x))[0]

def describe_array(x:np.ndarray):
    print("Shape:", x.shape)
    print(f"(min, max): {x.min(), x.max()}")
    print(f"(mean, std, var): {x.mean(), x.std(), x.var()}")
    print(f"Quartiles -- (0, 0.25, 0.5, 0.75, 1.0): {np.quantile(x, [0, 0.25, 0.5, 0.75, 1.0])}")