import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor



# Global variables
IMG_NAME = 'Nov21_150B_L1_F1'
EXT = '.tiff'
IMG_PATH = IMG_NAME + EXT
SCALE_PATH = IMG_NAME + '_Scale' + EXT



# Get all images
img = cv2.imread(IMG_PATH)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#scale = cv2.imread(SCALE_PATH, cv2.IMREAD_GRAYSCALE)
scale = cv2.imread(SCALE_PATH)
scale = cv2.cvtColor(scale, cv2.COLOR_BGR2RGB)



# Get model
sam_checkpoint = 'sam_vit_h_4b8939.pth'
model_type = 'vit_h'
device = 'cuda' if torch.cuda.is_available() else 'cpu'

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

mask_generator = SamAutomaticMaskGenerator(
    model=sam,
    #points_per_side=32,
    #pred_iou_thresh=0.86,
    #stability_score_thresh=0.92,
    #crop_n_layers=1,
    #crop_n_points_downscale_factor=2,
    min_mask_region_area=100,  # Requires open-cv to run post-processing
)



# Generate masks for images
masks = mask_generator.generate(img)
'''
masks[i] = {
    'segmentation': bool np array same shape as img with each each entry either True or False (T if that ppx is in the mask and F if it is not),
    'area': area of mask in ppxs (equivalent to summing over entire array (T is 1 and F is 0)),
    'bbox': boundary box of the mask in (x, y, width, height) format,
    'predicted_iou': the model's own prediction for the quality of the mask,
    'point_coords': the sampled input point that generated this mask,
    'stability_score': an additional measure of mask quality,
    'crop_box': the crop of the img used to generate this mask in (x, y, width, height) format
}
'''



# Get scale
predictor = SamPredictor(sam)
predictor.set_image(scale)
scale_center = np.array([[scale.shape[0] // 2, scale.shape[1] // 2]])
in_label = np.array([1])



# Generate mask for scale
mask, scores, logits = predictor.predict(
    point_coords=scale_center,
    point_labels=in_label,
    multimask_output=False,
)
# mask is a bool np array same shape as img with each each entry either True or False (T if that ppx is in the mask and F if it is not)



# Get pixels per millimeter
ppx_per_mm = np.sum(mask, axis=1)
ppx_per_mm = ppx_per_mm[ppx_per_mm > 0]
ppx_per_mm = np.mean(ppx_per_mm)



# Get area in square milimeters
for mask in masks:
    area_ppx = mask.pop('area')
    mask['area_ppx'] = area_ppx
    mask['area_mm^2'] = area_ppx / ppx_per_mm ** 2