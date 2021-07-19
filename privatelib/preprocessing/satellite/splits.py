from privatelib.basic import *

def split_image_to_grid(im, chunk_height=None, chunk_width=None, rows=None, cols=None, results=SPLIT.list, out_dir=None, 
                        pad=False, verbose=True, save_as_rgb=True, bands=[0,1,2]):
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
    
    #TODO: generator, better band selection, merge function
    """
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
                    out_f = out_dir/f"{h_idx // split_h}_{w_idx // split_w}.png"
                    plt.imsave(out_f, res[:,:,bands])
                else:
                    out_f = out_dir/f"{h_idx // split_h}_{w_idx // split_w}.tif"
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