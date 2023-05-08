# Scrap realtor.ca rental properties

This repository scraps a search result of realtor.ca, calculates the transit and driving duration of the properties from a pre-specified point and puts the results in a csv file.

- `fetch_property_list.py`: this file scraps the results by navigating each search result page. It also contains the URL of the starting page
- `calculate_distance.py`: this file calculates transit and driving duration of the properties.

## Setup

```bash
cp .env.example .env
nano .env # edit .env file
conda create -n realtor python=3.11
conda activate realtor
pip install -r requirements.txt
python src/fetch_property_list.py
python src/calculate_distance.py
```
