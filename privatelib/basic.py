from argparse import Namespace
from pathlib import Path
import json
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

def get_files_by_ext(path:Path, ext):
    return filter(lambda x: x.suffix.lower().endswith(ext), 
                  path.iterdir())