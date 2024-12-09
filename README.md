# FireEye: Predicting Wildfire Spread with Deep Learning

## Overview
FireEye is a deep learning project designed to predict the day-to-day progression of wildfires using satellite imagery and advanced Convolutional Neural Networks (CNNs). By leveraging publicly available datasets, this project aims to provide a computationally efficient tool for assessing wildfire risk and aiding resource allocation. Project based off of the "Next Day Wildfire Spread: A Machine Learning Data Set to Predict Wildfire Spreading from Remote-Sensing Data” paper. This project showcases both supervised machine learning techniques, as well as deep learning approaches.

## Key Features
- Utilizes a diverse range of geospatial datasets, including:
  - Fire masks
  - Elevation data
  - Weather conditions
  - Drought indices
  - Vegetation indices
  - Population density
- Processes data into standardized 64 km × 64 km patches with a resolution of 1 km × 1 km per pixel.
- Implements CNN architectures to predict wildfire spread based on spatial features.
- Addresses dataset filtering, data augmentation, and preprocessing challenges.

## Goals
1. Evaluate and compare multiple CNN architectures to identify the most effective model for wildfire prediction.
2. Enhance model robustness by incorporating regularization techniques like Dropout layers.

## Future Improvements
- **Physics-Informed Machine Learning (PIML):** Incorporate physical constraints into loss functions for more realistic predictions.
- **Data Refinement:** Improve data filtering to exclude outliers, such as spontaneous fire events, to enhance prediction accuracy.
- **Edge Handling in CNNs:** Use valid padding in Conv2D layers to improve predictions at image boundaries.

## Dataset
The project utilizes satellite imagery from the following sources:
- [Google Earth Engine](https://earthengine.google.com/)
- [Kaggle Dataset](https://www.kaggle.com/datasets/fantineh/next-day-wildfire-spread) (TensorFlow Record format)

Features include:
- Fire mask (2-bit mask for uncertainty and fire presence)
- Elevation (meters)
- Weather (temperature, precipitation, wind, etc.)
- Drought indices (Palmer Drought Severity Index)
- Vegetation (NDVI)
- Population density (persons/km²)

## Results
The trained models demonstrated strong spatial prediction capabilities but highlighted the limitations of pure data-driven approaches compared to physics-based simulations. Detailed results and visualizations are available in the project's deep learning report.
