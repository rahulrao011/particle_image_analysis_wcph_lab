import numpy as np
import torch
import matplotlib.pyplot as plt
from streamlit_image_coordinates import streamlit_image_coordinates
import streamlit as st
from PIL import Image
from transformers import SamModel, SamProcessor
import cv2
import os
import shutil


# Delete directory if it exsits and create a new one
shutil.rmtree('images', ignore_errors=True)
os.mkdir('images')

# Define global constants
MAX_WIDTH = 700



# Define helpful functions
def show_mask(mask, ax, random_color=False):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)
    
def show_points(coords, labels, ax, marker_size=20):
    pos_points = coords[labels==1]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='.', s=marker_size, edgecolor='white', linewidth=0.2)

def show_points_on_image(raw_image, input_point, ax, input_labels=None):
    ax.imshow(raw_image)
    input_point = np.array(input_point)
    if input_labels is None:
      labels = np.ones_like(input_point[:, 0])
    else:
      labels = np.array(input_labels)
    show_points(input_point, labels, ax)
    ax.axis('on')



# Get SAM
if torch.cuda.is_available():
    device = 'cuda'
else:
    device = 'cpu'
model = SamModel.from_pretrained("facebook/sam-vit-huge").to(device)
processor = SamProcessor.from_pretrained("facebook/sam-vit-huge")



# Get uploaded files from user
scale = st.file_uploader('Upload Scale Image')
image = st.file_uploader('Upload Particle Image')



# Runs when scale image is uploaded
if scale:
    scale_np = np.asarray(bytearray(scale.read()), dtype=np.uint8)
    scale_np = cv2.imdecode(scale_np, 1)

    # Save image if it isn't already saved
    if not os.path.exists(os.path.join("images/", scale.name)):
        with open(os.path.join("images/", scale.name), "wb") as f:
            f.write(scale.getbuffer())
    scale_pil = Image.open(os.path.join("images/", scale.name))

    #inputs = processor(raw_image, return_tensors="pt").to(device)
    inputs = processor(scale_np, return_tensors="pt").to(device)
    image_embeddings = model.get_image_embeddings(inputs["pixel_values"])
    
    scale_factor = scale_np.shape[1] / MAX_WIDTH # how many times larger scale_np is than the image shown for each dimension
    #clicked_point = streamlit_image_coordinates(Image.open(scale.name), height=scale_np.shape[0] // scale_factor, width=MAX_WIDTH)
    clicked_point = streamlit_image_coordinates(scale_pil, height=scale_np.shape[0] // scale_factor, width=MAX_WIDTH)
    if clicked_point:
        input_point_np = np.array([[clicked_point['x'], clicked_point['y']]]) * scale_factor
        input_point_list = [input_point_np.astype(int).tolist()]

        #inputs = processor(raw_image, input_points=input_point, return_tensors="pt").to(device)
        inputs = processor(scale_np, input_points=input_point_list, return_tensors="pt").to(device)
        inputs.pop("pixel_values", None)
        inputs.update({"image_embeddings": image_embeddings})
        with torch.no_grad():
            outputs = model(**inputs)
        masks = processor.image_processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"].cpu(), inputs["reshaped_input_sizes"].cpu())
        mask = torch.squeeze(masks[0])[0] # mask.shape: (1,x,y) --> (x,y)

        mask = mask.to(torch.int)
        input_label = np.array([1])

        fig, ax = plt.subplots()
        ax.imshow(scale_np)
        show_mask(mask, ax)
        #show_points_on_image(scale_np, input_point, input_label, ax)
        show_points(input_point_np, input_label, ax)
        ax.axis('off')
        st.pyplot(fig)

        # Get pixels per millimeter
        pixels_per_unit = torch.sum(mask, axis=1)
        pixels_per_unit = pixels_per_unit[pixels_per_unit > 0]
        pixels_per_unit = torch.mean(pixels_per_unit, dtype=torch.float).item()

    # Remove file when done
    scale_pil.close()
    os.remove(os.path.join("images/", scale.name))



# Runs when image is uploaded
if image:
    image_np = np.asarray(bytearray(image.read()), dtype=np.uint8)
    image_np = cv2.imdecode(image_np, 1)

    # Save image if it isn't already saved
    if not os.path.exists(os.path.join("images/", image.name)):
        with open(os.path.join("images/", image.name), "wb") as f:
            f.write(image.getbuffer())
    image_pil = Image.open(os.path.join("images/", image.name))

    #inputs = processor(raw_image, return_tensors="pt").to(device)
    inputs = processor(image_np, return_tensors="pt").to(device)
    image_embeddings = model.get_image_embeddings(inputs["pixel_values"])
    
    scale_factor = image_np.shape[1] / MAX_WIDTH # how many times larger scale_np is than the image shown for each dimension
    clicked_point = streamlit_image_coordinates(image_pil, height=image_np.shape[0] // scale_factor, width=MAX_WIDTH)
    if clicked_point:
        input_point_np = np.array([[clicked_point['x'], clicked_point['y']]]) * scale_factor
        input_point_list = [input_point_np.astype(int).tolist()]

        #inputs = processor(raw_image, input_points=input_point, return_tensors="pt").to(device)
        inputs = processor(image_np, input_points=input_point_list, return_tensors="pt").to(device)
        inputs.pop("pixel_values", None)
        inputs.update({"image_embeddings": image_embeddings})
        with torch.no_grad():
            outputs = model(**inputs)
        masks = processor.image_processor.post_process_masks(outputs.pred_masks.cpu(), inputs["original_sizes"].cpu(), inputs["reshaped_input_sizes"].cpu())
        mask = torch.squeeze(masks[0])[0] # mask.shape: (1,x,y) --> (x,y)

        mask = mask.to(torch.int)
        input_label = np.array([1])

        fig, ax = plt.subplots()
        ax.imshow(image_np)
        show_mask(mask, ax)
        #show_points_on_image(scale_np, input_point, input_label, ax)
        show_points(input_point_np, input_label, ax)
        ax.axis('off')
        st.pyplot(fig)



        # Get the area in square millimeters
        st.write(f'Area: {torch.sum(mask, dtype=torch.float).item() / pixels_per_unit ** 2} μm^2')


    
    # Remove file when done
    image_pil.close()
    os.remove(os.path.join("images/", image.name))
