import numpy as np
import math
from skimage.morphology import reconstruction
import matplotlib.pyplot as plt
from PIL import Image

from skimage.segmentation import watershed
from scipy import ndimage
from scipy.ndimage import grey_dilation, generate_binary_structure, \
        maximum_filter, minimum_filter, \
        gaussian_filter

from collections import Counter

def bandPassSegm(img, lowSigm, highSigm, coeff, thresh):

    img = img - img.min()
    img =img/ img.max()

    img_sm = gaussian_filter(img, sigma = lowSigm, mode = 'reflect', radius = int((np.ceil(3*lowSigm)-1)/2))
    img_bg = gaussian_filter(img, sigma = highSigm, mode = 'reflect', radius = int((np.ceil(3*highSigm)-1)/2))

    img_sample = img_sm - img_bg * coeff

    im_mask = img_sample > thresh

    return im_mask.astype(float)

######GALA FUNCTIONS###################################
def complement(a):
    return a.max()-a

def hminima(a, thresh):

    maxval = a.max()
    ainv = maxval - a

    return maxval - morphological_reconstruction(ainv-thresh, ainv)

def morphological_reconstruction(marker, mask, connectivity=1):

    sel = generate_binary_structure(marker.ndim, connectivity)
    marker = reconstruction(marker, mask, footprint = sel)

    return marker

def regional_minima(a, connectivity=1):
    """Find the regional minima in an ndarray."""
    values = np.unique(a)
    delta = (values - minimum_filter(values, footprint=np.ones(3)))[1:].min()
    marker = complement(a)
    mask = marker+delta
    return (marker == morphological_reconstruction(marker, mask, connectivity)).astype(float)
#######################################################


def remove_false_positives(img, labels, FalsePositBrightness_k, MinNucleusArea):

    """Find and remove all segmented areas with intensity below FalsePositBrightness_k*img.mean
    where img.mean is mean intensity of segmeneted masked image."""
    binary_mask = labels.copy()
    binary_mask[binary_mask != 0] = 1

    masked_img = np.multiply(binary_mask, img)
    masked_img_thresholded = masked_img - (FalsePositBrightness_k*img.mean())

    masked_img_thresholded[masked_img_thresholded < 0] = 0
    masked_img_thresholded[masked_img_thresholded != 0] = 1

    new_labels_ = np.multiply(labels, masked_img_thresholded)

    labels[np.isin(labels, np.unique(new_labels_).astype(int)) == False] = 0

    """Find and remove all segmented areas less than MinNucleusArea."""
    labels_tmp = labels.copy()
    labels_tmp = labels_tmp[labels_tmp!=0].flatten()
    labels_dict = Counter(tuple(labels_tmp))
    keys = np.array(list(labels_dict.keys()))
    values = list(labels_dict.values())
    values = np.array(list(map(int, values)))
    keys[values <= MinNucleusArea] = 0

    labels[np.isin(labels, np.unique(keys).astype(int)) == False] = 0

    return labels

def watershedSegm(mask):

    dist = -ndimage.distance_transform_edt(mask)
    local   = hminima(dist, 2)
    local   = regional_minima(local, 8)
    markers = ndimage.label(local)[0]
    labels = watershed(dist, markers, mask=mask)

    return labels

def main(img, lowSigm, highSigm, coeff, thresh, removeFalsePosit=True, FalsePositBrightness_k=1.5, MinNucleusArea=1000):

    if img.ndim!=2 and img.ndim==3:
        RGB_channel = np.flatnonzero(img.reshape(-1, img.shape[-1]).sum(axis=0))[0]
        img = img[:,:,RGB_channel]
#         raise Exception("'img' must be a 2-D grayscale array.")

    assert type(removeFalsePosit)==bool, 'removeFalsePosit must be Bool'

    print('Segmenting cells with Banpass filter High Std %2d, Low Std %2d' % (highSigm, lowSigm))
    segmented_image = bandPassSegm(img, lowSigm, highSigm, coeff, thresh)

    #return segmented_image

    print('<========== Performing Watershed segmentation ==========>')
    new_segmented_image = watershedSegm(segmented_image)

    if removeFalsePosit:
        print('<========== Removing false positive segmented areas ==========>')
        new_segmented_image = remove_false_positives(img, new_segmented_image, FalsePositBrightness_k, MinNucleusArea)

    return new_segmented_image