# DATA_ENG 300 Homework 3: NYC Taxi Analytics with PySpark, EC2, and S3

## Overview

This project analyzes New York City Taxi & Limousine Commission (TLC) trip data using PySpark on AWS EC2. The analysis includes data cleaning, exploratory analytics, and fare prediction using a Random Forest regression model. Results and visualizations are written to Amazon S3.

Dataset month used:

- January 2026
- Yellow Taxi: `yellow_tripdata_2026-01.parquet`
- Green Taxi: `green_tripdata_2026-01.parquet`

---

## Project Structure

```text
homework3/
├── homework3.ipynb
├── README.md
├── summary.pdf
```

---

## EC2 Environment

The project was developed and executed on an AWS EC2 instance running Amazon Linux 2023.

Required packages:

```bash
pip install pyspark pandas pyarrow matplotlib
```

Verify installation:

```bash
java -version
python3 -c "import pyspark; print(pyspark.__version__)"
```

---

## Data Acquisition

Create a local data directory:

```bash
mkdir -p data
```

Download the datasets:

```bash
aws s3 cp s3://de300-hw3-nyctlc-549787090008-us-east-1-an/yellow_tripdata_2026-01.parquet data/

aws s3 cp s3://de300-hw3-nyctlc-549787090008-us-east-1-an/green_tripdata_2026-01.parquet data/
```

---

## Running the Analysis

Launch Jupyter Notebook:

```bash
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser
```

Run all cells in:

```text
homework3.ipynb
```

The notebook performs:

1. Spark initialization
2. Data loading
3. Schema standardization
4. Data cleaning
5. Exploratory analytics
6. Random Forest fare prediction
7. Plot generation
8. Writing results to S3

---

## Data Cleaning Rules

The following records are removed:

- Missing pickup timestamps
- Missing drop-off timestamps
- Non-positive trip distances
- Negative fare amounts
- Negative total amounts
- Trips longer than 24 hours
- Trips with drop-off times before pickup times

---

## Outputs

The following result tables are generated:

- Average fare by taxi type
- Average trip distance by taxi type
- Pickups by hour

The following plot is generated:

- Predicted fare amount vs actual fare amount

---

## S3 Output Location

Results are written to:

```text
s3://yash-hw3/nyc-taxi-assignment/
```

Contents include:

```text
average_fare_by_taxi_type/
average_distance_by_taxi_types/
pickups_by_hour/
predicted_vs_actual_fare.png
```