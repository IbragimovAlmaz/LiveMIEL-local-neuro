# LiveMIEL-local-NGN2

This repository is a modified, locally optimized fork of the original **LiveMIEL** pipeline developed by Alexandra Shuvaeva under cviaai (Original repository: [cviaai/LiveMIEL](https://github.com/cviaai/LiveMIEL)).

# Distinctive Features of this Version:
* **Infrastructure Optimization:** Unlike the baseline pipeline which is configured exclusively for Google Colab and Google Drive integration, this version has been completely refactored for **standalone local execution** (removing all `google.colab` and `drive.mount` cloud dependencies) to support offline processing.
* **Datasets Compatibility:** Adapted to process heavy laboratory imaging datasets (totaling 132 GB of images only, with single sensor runs ranging between 30-50 GB) locally, avoiding cloud storage limitations.
* **Task-Specific Application:** Tailored for only automated segmentation, feature extraction and processing of NGN2-driven neural differentiation datasets. Also contains scripts to install the data and scripts remotely if needed. Additionally, we added statistical comparison between Hopkins values of each sensor and final histogram plotting.
* **Reproducibility:** Tailored specifically for the reproducible processing of the dataset published on Zenodo (DOI: 10.5281/zenodo.20648952).

# LiveMIEL Pipeline
**Live Microscopic Imaging of the Epigenetic Landscape (MIEL)** serves as a platform developed to work with differentiating cells, to track epigenetic processes of the pool of living cells. 

The pipeline includes the following sequential analytical blocks:
* **Tuning parameters for image segmentation:** lowSigm, highSigm, thresh and FalsePositBrightness_k parameters should be tuned for further segmentation and cropping. We listed our applied parameters and key segmentation heuristic.
* **Nucleus Segmentation & Cropping:** Automated localization and masking of individual cellular nuclei, followed by image extraction to generate single-nuclei image datasets.
* **Feature Extraction:** Quantitative profiling of nuclear morphometrics, textures, and spatial distributions from single-nuclei images, including:
  - *Texture Features:* Haralick texture features (GLCM) and Threshold Adjacency Statistics (TAS).
  - *Shape & Geometry:* Zernike moments and Center of Mass (centroid tracking).
  - *Epigenetic/Chromatin Architecture:* Higher-order chromatin intensity features and signal distribution patterns.
* **Dimensionality Reduction:** Principal Component Analysis (PCA) to reduce the high-dimensional feature vectors while preserving maximum biological variance.
* **Clustering:** Unsupervised clustering of the obtained feature vectors to identify distinct nuclear/epigenetic states across the differentiation timeline.
* **Downstream Analysis:** Statistical evaluation and structural profiling of the resulting cluster data distributions.

---

## Dataset Availability

The complete dataset (174 GB raw / 35 GB compressed) supporting this pipeline is hosted on Zenodo. 

* **Zenodo Repository:** DOI: 10.5281/zenodo.20648952

To run the full pipeline, download the required sensor archives and extract them into a centralized root directory to match the local path syntax (e.g., `./IPSC/nuclei_images/AF9-Red_NGN2/0d/` and `./IPSC/single_nuclei_images/AF9-Red_NGN2/0d/`, for example).

*Note: If you want to skip the raw image preprocessing and nucleus extraction phase, you can download only the preprocessed single-nuclei dataset (`single_nuclei_images.zip`), extract it to `./IPSC/single_nuclei_images/`, and comment out/ignore the segmentation part in the main script.*

---

### Repository Structure & Execution Guide
To replicate the findings or process similar data, ensure all files remain in the same root folder. Run the scripts in the following logical sequence via the main Jupyter Notebook:

1. `My_segmentation_ Segmentation,_features_extraction_and_clustering.ipynb` — **Master Pipeline**. Open this notebook to control the entire workflow.
2. `bandpass_segmentation.py` — Image preprocessing and bandpass filtering (can be installed automatically in-.ipynb file or manually from 'additional' folder).
3. `cropping_single_cells.py` — Region of interest (ROI) extraction and single-cell isolation (can be installed automatically in-.ipynb file or manually from 'additional' folder).
4. `features_extraction.py` — Morphological and signal feature extraction from segmented cells (can be installed automatically in-.ipynb file or manually from 'additional' folder).
5. `classification.py` — Downstream data classification and clustering analysis (can be installed automatically in-.ipynb file or manually from 'additional' folder).

## Getting Started

### 1. Environment Setup
We recommend using **Conda** to manage an isolated environment with **Python 3.10**:

```bash
# Create a new conda environment
conda create -n livemiel python=3.10 pip -y

# Activate the environment
conda activate livemiel
```

### 2. Installing Dependencies
Install the core image processing, machine learning, and data analysis libraries via `pip`:

```bash
pip install numpy pandas scikit-learn tqdm scikit-image opencv-python Pillow mahotas scipy pingouin scikit-posthocs statannotations matplotlib seaborn plotly
```
Before running the pipeline, ensure you have Python installed and install all the required dependencies at once using this mentioned command.

### 3. Installing PyTorch
Depending on your hardware configuration (CPU vs GPU), choose **one** of the following options:

* **Option A: Standard PyTorch installation via Conda**
  ```bash
  conda install pytorch torchvision torchaudio -c pytorch
  ```
* **Option B: PyTorch with CUDA 12.1 support via Pip (Recommended for NVIDIA GPUs)**
  ```bash
  pip install torch torchvision torchaudio --index-url https://pytorch.org
  ```

---

## Usage

1. Activate your environment: `conda activate livemiel`
2. Open the main execution notebook:
   ```bash
   jupyter notebook "My_segmentation_Segmentation,_features_extraction_and_clustering.ipynb"
   ```
3. **Segmentation Tuning:** If you are processing your own or raw datasets, you can adjust the core segmentation parameters in the script execution line:
   * `lowSigm` (optimal range `5`-`12`, up to `40` to prevent irregular nuclei from splitting).
   * `highSigm` (optimal range `30`-`70`, lower values like `40` speed up processing).
   * `thresh` (`0.003`-`0.05` intensity threshold).
   * `FalsePositBrightness_k` (`1.2`-`2.5` coefficient to filter out artifacts and dim/dying nuclei).
The exact and detailed information you can find in `My_segmentation_ Segmentation,_features_extraction_and_clustering.ipynb` file.


## Tunable Parameters

The segmentation pipeline is highly configurable to adapt to different image qualities and magnifications. It consists of three stages:

1.  **Bandpass Segmentation:** `(image * big_gaussian_kernel) - coeff x (image * small_gaussian_kernel) > thresh`
2.  **Watershed Segmentation:** Separates adjacent or touching nuclei.
3.  **False Positive Removal:** Filters out objects that do not correspond to true nuclei.

### Core Parameters

| Parameter | Description | Typical Range (60x, 1360x1024 px) |
| :--- | :--- | :--- |
| **`lowSigm`** | Std. dev. of the `small_gaussian_kernel`. Smoothes noise and defines object detail. Lower values preserve more detail; higher values smooth outlines. <br><br> <img src="./figures/lowSigm.png" style="width:350px; height:auto;">  | `[5, 15]` |
| **`highSigm`** | Std. dev. of the `big_gaussian_kernel`. Removes background. Lower values remove more background fragments. <br><br><img src="./figures/highSigm.png" style="width:350px; height:auto;"> | `[20, 70]` |
| **`thresh`** | Intensity threshold for the bandpass filter. Pixels above this value are considered potential objects. | `[0.003, 0.05]` |
| **`FalsePositBrightness_k`** | Brightness coefficient `k`. Objects with mean fluorescence < `k * average_image_fluorescence` are removed. <br><br><img src="./figures/FalsePositBrightness_k.png" style="width:550px; height:auto;"> | `[1.0, 2.5]` |
| **`MinNucleusArea`** | Minimum area (in pixels). Objects smaller than this are discarded. | `[500, 1500]` |
The exact and detailed information you can find in `My_segmentation_ Segmentation,_features_extraction_and_clustering.ipynb` file.

### Scaling Parameters for Different Magnifications/Resolutions

The parameters `lowSigm`, `highSigm`, and `MinNucleusArea` **scale linearly** with the image dimensions.

**Example:** For a **60x** image with a resolution of **4080 x 3072 px** (3x larger in each dimension than the base 1360x1024):

- **Scale Factor:** `(4080 / 1360) = 3`
- **Area Scale Factor:** `3 * 3 = 9`

| Parameter | Scaled Value / Range |
| :--- | :--- |
| **`lowSigm`** | `[5*3, 15*3]` = `[15, 45]` |
| **`highSigm`** | `[20*3, 70*3]` = `[60, 210]` |
| **`MinNucleusArea`** | `1000 * 9` = `9000` |


**Tips for Parameter Tuning:**
- Start with the scaled base values and adjust incrementally
- Use the example images above as visual references for expected outcomes

---

## Associated Manuscript
This repository is supplementary to the manuscript:  
*“Novel fluorescent sensor for H3K36me2/3 provides high precision live-cell tracking of epigenetic changes during neuronal differentiation ”*.

## Contacts
* **Original Pipeline Author:** Alexandra Shuvaeva ; https://github.com/cviaai/LiveMIEL
* **Current Work Author:** Almaz Ibragimov
* **Email:** Almaz.Ibragimov@skoltech.ru ; ibragimov_al@bk.ru


## **Citing**

The core tracking logic and baseline architecture of the LiveMIEL pipeline were originally conceptualized, developed and published by *“Stepanov et al”*.
The complete raw and processed datasets generated and analyzed during this study are publicly available repository on Zenodo at DOI: 10.5281/zenodo.20648952. 

The computational pipeline used for data processing, image segmentation, and feature extraction is a customized, locally deployable version of the LiveMIEL framework (originally developed by cviaai: https://github.com/cviaai/LiveMIEL). To ensure full reproducibility of the results without cloud infrastructure dependencies, the specific standalone source code optimized for local handling these large-scale datasets has been deposited in a public GitHub repository at https://github.com/IbragimovAlmaz/LiveMIEL-local-neuro/.

If you use this package in your publications or in other work, please cite it as follows:
   ```bibtex
   @article{stepanov2024iPSC,
     title={Tracking induced pluripotent stem cell differentiation with a fluorescent genetically encoded epigenetic probe},
     author={Stepanov, A. I. and Shuvaeva, A. A. and Putlyaeva, L. V. and Lukyanov, D. K. and Galiakberova, A. A. and Gorbachev, D. A. and Maltsev, D. I. and Pronina, V. and Dylov and D. V. and Terskikh, A. V. and Lukyanov, K. A. and Gurskaya, N. G.},
     journal={Cellular and Molecular Life Sciences},
     number = {1},
     pages = {381},
     volume = {81},
     doi = {/10.1007/s00018-024-05359-0},
     url = {https://link.springer.com/article/10.1007/s00018-024-05359-0}
     year = {2024}
   }
   

