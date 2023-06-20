# particle_image_analysis_wcph_lab

Use the official GitHub as a reference: https://github.com/facebookresearch/segment-anything

Go to:
notebooks --> automatic_mask_generator_example.ipynb and predictor_example.ipynb

Download the following images from the shared Google Drive:
Undergraduate Research --> IMAGES --> AE2124_November 2021 --> AE2124_150m_B --> Layer 1 --> field 1.tiff and 1umScale.tiff

Rename these 2 files:
field 1.tiff --> Nov21_150B_L1_F1.tiff
1umScale.tiff --> Nov21_150B_L1_F1_Scale.tiff

If those names don't match, this will still work, as long as those names are also changed in the code as needed

### INSTRUCTIONS FOR RUNNING PROGRAM: ###

To run the program perform the following steps in this order:

1) Git this clone repo

2) Run the command:

pip install -r requirements.txt

in the terminal

3) Run the command:

streamlit run automatic_mask_generator.py

in the terminal

2) Go to:

https://localhost:8501

or whatever url the terminal says to go to
