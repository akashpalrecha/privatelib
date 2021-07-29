from privatelib.basic import *
from PIL import Image
try:
    import tifffile
except:
    print("`tifffile` not available")
try: 
    import rasterio
except:
    print("`rasterio` not available")
try:
    import cv2
except:
    print("`opencv` not available")
          
def project_mask_to_tif(mask:Path, tiff:Path, output_file:Path="./output.tif"):
    mask = cv2.imread(mask, cv2.IMREAD_GRAYSCALE)
    if len(mask.shape) == 3:
        mask = mask[:,:,0]
    tile = rasterio.open(tiff)
    with rasterio.open(
        output_file,
        'w',
        driver='GTiff',
        height=tile.shape[0],
        width=tile.shape[1],
        count=1,
        dtype=mask.dtype,
        crs=tile.crs,
        transform=tile.transform,
    ) as dst:
        dst.write(mask, 1)