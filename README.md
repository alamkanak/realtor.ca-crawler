# Scrap realtor.ca rental properties

```bash
cp .env.example .env
nano .env # edit .env file
conda create -n realtor python=3.11
conda activate realtor
pip install -r requirements.txt
python src/fetch_property_list.py
python src/calculate_distance.py
```