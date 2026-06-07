# Homework 4 - Apache Airflow Recommendation Pipeline

## Team Members

* Yash Fadia
* Margaret Silva

## MWAA Environment

de300-airflow-yash-margaret

## S3 Bucket

de300-airflow-yash-margaret

## Project Description

This project implements a movie recommendation pipeline using Apache Airflow (MWAA) and the MovieLens 1M dataset.

Two DAGs were created:

### hw4_movie_embeddings

* Loads movie data from MovieLens 1M
* Creates BERT input text
* Generates and stores movie embeddings

Outputs:

* movies_full.csv
* movie_embeddings_full.npy

### hw4_recommendations

* Loads ratings data
* Splits ratings into four timestamp partitions
* Simulates observations arriving at 0, 10, 20, and 30 hours
* Samples 30% of available users
* Generates recommendations for cold users and top users

Outputs:

* recommendations_iteration_1_hour_0.csv
* recommendations_iteration_2_hour_10.csv
* recommendations_iteration_3_hour_20.csv
* recommendations_iteration_4_hour_30.csv

## How to Run

1. Upload the DAG files to the MWAA DAG folder.
2. Enable the DAGs in Airflow.
3. Trigger:

   * hw4_movie_embeddings
   * hw4_recommendations
4. Verify outputs are written to the S3 bucket.

## Repository Structure

```text
homework_4/
├── info.txt
├── README.md
├── dags/
│   ├── hw4_movie_embeddings_dag.py
│   └── hw4_recommendations_dag.py
└── outputs/
```
