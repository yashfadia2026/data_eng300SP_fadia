from airflow import DAG
from airflow.operators.python import PythonOperator

import pendulum
import pandas as pd
import numpy as np
from io import BytesIO
import urllib.request


WORKFLOW_SCHEDULE = None

MOVIES_URL = "https://ynf0058-de300-lab3.s3.amazonaws.com/ml-1m/movies.dat"

EMBEDDINGS_CSV_URL = "https://de300-airflow-yash-margaret.s3.amazonaws.com/hw/embeddings/movies_full.csv"
EMBEDDINGS_NPY_URL = "https://de300-airflow-yash-margaret.s3.amazonaws.com/hw/embeddings/movie_embeddings_full.npy"

default_args = {"owner": "yash","depends_on_past": False,"start_date": pendulum.today("UTC").add(days=-1),"retries": 1,
}


def load_movies(**context):
    movies = pd.read_csv(MOVIES_URL,sep="::",engine="python",names=["MovieID", "Title", "Genres"],encoding="latin-1")
    print("Loaded movies.dat")
    print("Shape:", movies.shape)
    print(movies.head())
    return int(movies.shape[0])


def create_bert_text(**context):
    movies = pd.read_csv(MOVIES_URL,sep="::",engine="python",names=["MovieID", "Title", "Genres"],encoding="latin-1")
    movies["Year"] = movies["Title"].str.extract(r"\((\d{4})\)")
    movies["bert_text"] = (
        "Movie title: " + movies["Title"] + ". Genres: " + movies["Genres"]
    )
    print("Created BERT text using same logic from HW2.")
    print(movies[["MovieID", "Title", "Genres", "Year", "bert_text"]].head())
    return int(movies.shape[0])

def verify_embedding_outputs(**context):
    movies_embedded = pd.read_csv(EMBEDDINGS_CSV_URL)
    with urllib.request.urlopen(EMBEDDINGS_NPY_URL) as response:
        npy_bytes = response.read()
    embeddings = np.load(BytesIO(npy_bytes))
    print("Verified uploaded embedding outputs.")
    print("movies_full.csv shape:", movies_embedded.shape)
    print("movie_embeddings_full.npy shape:", embeddings.shape)
    assert movies_embedded.shape[0] == embeddings.shape[0], ("Number of movie rows does not match number of embeddings.")
    assert embeddings.shape[1] == 768, ("Expected BERT embedding dimension of 768.")
    print("Embedding files are valid and aligned.")


with DAG(
    dag_id="hw4_movie_embeddings",
    default_args=default_args,
    description="HW4 offline embedding verification DAG",
    schedule=WORKFLOW_SCHEDULE,
    catchup=False,
    tags=["de300", "hw4", "bert", "embeddings"],
) as dag:

    t_load_movies = PythonOperator(
        task_id="load_movies",
        python_callable=load_movies,
    )

    t_create_bert_text = PythonOperator(
        task_id="create_bert_text",
        python_callable=create_bert_text,
    )

    t_verify_embeddings = PythonOperator(
        task_id="verify_embedding_outputs",
        python_callable=verify_embedding_outputs,
    )

    t_load_movies >> t_create_bert_text >> t_verify_embeddings