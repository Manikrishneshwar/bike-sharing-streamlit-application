An interactive Streamlit web application for exploring and visualizing bike sharing in Torronto.<br>

This project collects open data from Toronto's  Open Data Portal (linked below), performs data cleaning and processing, and presents insights throught an interactive streamlit dashboard.

## Motivation
Toronto Bike Share publishes extensive open data, but it can be difficult to explore without technical tools. This project provides a simple, interactive way to analyze ridership trends and uncover insights about how Toronto moves. 

## Data Source
Toronto Bike Share open datasets from the official Toronto Open Data portal.<br>
Open Data portal of Toronto: [https://open.toronto.ca](https://open.toronto.ca)<br>
Bike share Toronto: [https://open.toronto.ca/dataset/bike-share-toronto/](https://open.toronto.ca/dataset/bike-share-toronto/)<br>
Bike share Toronto Ridership Data:[https://open.toronto.ca/dataset/bike-share-toronto-ridership-data/](https://open.toronto.ca/dataset/bike-share-toronto-ridership-data/)<br>
The ridership data consists data from numerous years. The ones used in this project are all files corresponding to years 2020-2023 (both included) and the 1st file of 2024.

## How to run
Download the necessary data sets from the links above. <br>
- Change the prefix in [environment.yml](environment.yml)
- Run `conda env create -f environment.yml` to create a new environment. This may take a while.
- Activate the new environment with `conda activate bike_sharing`.
- Run the StreamLit web app with `streamlit run app.py`.
- Open [StreamLit application on local host](http://localhost:8501)
