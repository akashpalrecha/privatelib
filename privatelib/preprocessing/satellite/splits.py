from privatelib.basic import *
from PIL import Image
try:
    import tifffile
except:
    print("`tifffile` not available")

SPLIT = Namespace(list=1, save_to_dir=2, generator=3)

def split_image_to_grid(im, chunk_height=None, chunk_width=None, rows=None, cols=None, results=SPLIT.list, out_dir=None, 
                        pad=False, verbose=True, save_as_rgb=True, bands=[0,1,2], prefix=None, suffix=None, mask=False):
    """
    splits `im` into a grid according to specifications and returns results according to `results` param
    im: image [numpy array: h x w x c] to split
    chunk_height: height of resultant splits in pixels. if only `chunk_height` is provided, `chunk_width` takes the same value
        `chunk_height` takes precedence over `rows` and `cols`
    chunk_width: width of resultant splits in pixels.
    rows: number of rows to divide the image into. if only `rows` is provided, `cols` takes the same value
    cols: number of columns to divide image into
    results: set to SPLIT.list to get the function to return a list of the resultant grid items
             set to SPLIT.save_to_dir to save the outputs to `out_dir`
             set to SPLIT.generator to return a generator for the resultant items. The generator returns (im_split, top, left, height, width) for each item
    out_dir: output directory in case SPLIT.save_to_dir is passed
    pad: whether to pad incomplete / edge tiles with 0s for consistent size
    verbose: prints status messages if set to True
    save_as_rgb: save 3 band RGB imagery in PNG format
    bands: bands to use when saving as RGB imagery
    prefix: prefix for saved chunks
    suffix: suffix for saved chunks
    mask: save image as a single channel uint8 mask
    #TODO: generator, better band selection, merge function
    """
    if len(im.shape) == 2: 
        im = im[:,:,np.newaxis]
    if prefix is None: 
        prefix = "img"
    if suffix is None: 
        suffix = ""
    else:
        suffix = f"_{suffix}"
    if chunk_height is not None:
        if chunk_width is not None: pass
        else: chunk_width = chunk_height
        split_h = chunk_height
        split_w = chunk_width
    elif rows is not None:
        if cols is not None: pass
        else: cols = rows
        split_h = im.shape[0] // rows
        split_w = im.shape[1] // cols
    out_shape = (split_h, split_w, im.shape[-1])
    h_idx = 0
    w_idx = 0
    vertical_splits   = int(np.ceil(im.shape[0] / split_h))
    horizontal_splits = int(np.ceil(im.shape[1] / split_w))
    
    if results == SPLIT.save_to_dir:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        info = {
            "height": int(im.shape[1]),
            "width": int(im.shape[0]),
            "chunk_height": split_h,
            "chunk_width": split_w,
            "vertical_splits": vertical_splits,
            "horizontal_splits": horizontal_splits,
            "padded": pad,
            "save_as_rgb": save_as_rgb,
            "bands": bands
        }
        out_f = out_dir/"info.json"
        with out_f.open("w") as f:
            json.dump(info, f)
    
    out_list = []
    
    while h_idx < im.shape[0]:
        cur_list = []
        w_idx = 0
        while w_idx < im.shape[1]:
            res = im[h_idx:h_idx+split_h, w_idx:w_idx+split_w, :]
            h, w = res.shape[:2]
            if pad:
                if res.shape != out_shape:
                    tmp = np.zeros_like(res, shape=out_shape)
                    tmp[:res.shape[0], :res.shape[1], :] = res
                    res = tmp
            if results == SPLIT.list:
                if verbose: print(f"processed {h_idx // split_h}_{w_idx // split_w} image")
                cur_list.append(res)
            elif results == SPLIT.save_to_dir:
                if save_as_rgb:
                    out_f = out_dir/f"{prefix}_{h_idx // split_h}_{w_idx // split_w}{suffix}.png"
                    if mask:
                        mask = Image.fromarray(res[:,:,0].astype(np.uint8))
                        mask.save(str(out_f))
                    else:
                        plt.imsave(out_f, res[:,:,bands])
                else:
                    out_f = out_dir/f"{prefix}_{h_idx // split_h}_{w_idx // split_w}{suffix}.tif"
                    tifffile.imsave(out_f, res)
                if verbose: print(f"Saved split to: {out_f}")
            elif results == SPLIT.generator:
                raise NotImplementedError("Not that straightforward. Will do later")
                # yield (res, h_idx, w_idx, h, w)
            w_idx += split_w
        h_idx += split_h
        if results == SPLIT.list:
            out_list.append(cur_list)
    
    if results == SPLIT.list:
        return out_list
    
    
def merge_images(path:Path, out="output.png", result=SPLIT.save_to_dir, ext=None, debug=False):
    """
    path: path containing images with naming convention of split using split_image_to_grid function
    out: output file path
    result: SPLIT.save_to_dir will save merge result to `out`
            SPLIT.list will return merged image #TODO: change this
    ext: extension of images to look for. if not provided, function will infer ext from files
    debug: run set_trace at the start of function
    """
    if debug: set_trace()
    path = Path(path)
    if ext is None:
        images = sorted(filter(lambda x: is_image(x), 
                               path.ls()))
    else:
        images = sorted(list(get_files_by_ext(path, ext)))
        
    suffix = images[0].stem.split("_")[-1]
    try:
        int(suffix) # if this is possible, then there is no suffix
        # adding trailing `_` to image paths
        images = [image.parent/f"{image.stem}_{image.suffix}" for image in images]
        suffix = ""
    except:
        suffix = f"_{suffix}"
    prefix = "_".join(images[0].stem.split("_")[:-3])
    ext = images[0].suffix
    stems = [tuple(map(int, img.stem.split("_")[-3:-1])) for img in images] # last split after _ is suffix
    rows = set([stem[0] for stem in stems])
    cols = set([stem[1] for stem in stems])
    row_ims = []
    if 'tifffile' in dir() and ext.lower().endswith('tif'):
        open_func = lambda x: tifffile.imread(str(x))
        def save_func(fname, arr): tifffile.imsave(fname, arr)
    else:
        open_func = lambda x: plt.imread(str(x))
        def save_func(fname, arr): plt.imsave(fname, arr)
    output = "".join(str(out).split(".")[:-1]) + ext
    image_rows = []
    for row in rows:
        images = []
        gc.collect()
        for col in cols:
            images.append(open_func(path/f"{prefix}_{row}_{col}{suffix}{ext}"))
        image_rows.append(np.concatenate(images, axis=1))
    image = np.concatenate(image_rows, axis=0)
    if result == SPLIT.save_to_dir:
        save_func(output, image)
    elif result == SPLIT.list:
        return image
    else:
        raise NotImplementedError(f"No implementation for provided result format: {result}")