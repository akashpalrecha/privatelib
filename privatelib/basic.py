from pathlib import Path
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