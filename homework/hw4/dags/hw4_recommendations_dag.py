from airflow import DAG
from airflow.operators.python import PythonOperator

import pendulum
import pandas as pd
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity


WORKFLOW_SCHEDULE = None

BUCKET = "ynf0058-de300-lab3"
RATINGS_URL = f"https://{BUCKET}.s3.amazonaws.com/ml-1m/ratings.dat"

LOCAL_MOVIES_PATH = "/usr/local/airflow/dags/hw4_cache/movies_full.csv"
LOCAL_EMBEDDINGS_PATH = "/usr/local/airflow/dags/hw4_cache/movie_embeddings_full.npy"

default_args = {
    "owner": "yash",
    "depends_on_past": False,
    "start_date": pendulum.today("UTC").add(days=-1),
    "retries": 1,
}
def load_and_partition_ratings(**context):
    ratings = pd.read_csv(RATINGS_URL,sep="::",engine="python",names=["UserID", "MovieID", "Rating", "Timestamp"],encoding="latin-1")
    ratings["Datetime"] = pd.to_datetime(ratings["Timestamp"], unit="s")
    part1 = ratings[
        (ratings["Datetime"] >= "2000-04-25") &
        (ratings["Datetime"] <= "2000-08-03")].copy()
    part2 = ratings[
        (ratings["Datetime"] >= "2000-08-04") &
        (ratings["Datetime"] <= "2000-10-31")].copy()
    part3 = ratings[
        (ratings["Datetime"] >= "2000-11-01") &
        (ratings["Datetime"] < "2000-11-26")].copy()
    part4 = ratings[
        ratings["Datetime"] >= "2000-11-26"].copy()
    os.makedirs("/tmp/hw4", exist_ok=True)
    for i, part in enumerate([part1, part2, part3, part4], start=1):
        path = f"/tmp/hw4/ratings_part_{i}.csv"
        part.to_csv(path, index=False)
        print(f"Saved partition {i}: {part.shape}")
    return "ratings partitioned"

def cold_user_recommendation(movies, embeddings, top_k=5):
    average_embedding = embeddings.mean(axis=0).reshape(1, -1)
    similarity = cosine_similarity(average_embedding, embeddings)[0]
    top_indices = similarity.argsort()[-top_k:][::-1]
    recs = movies.iloc[top_indices][["MovieID", "Title", "Genres", "Year"]].copy()
    recs["Similarity"] = similarity[top_indices]
    return recs

def select_top_user(ratings):
    count_per_user = ratings.groupby("UserID").size().reset_index(name="Interaction_Count")
    upper_threshold = count_per_user["Interaction_Count"].quantile(0.95)
    top_users = count_per_user[count_per_user["Interaction_Count"] >= upper_threshold]
    chosen_user = top_users.sample(1, random_state=42).iloc[0]
    return int(chosen_user["UserID"]), int(chosen_user["Interaction_Count"])

def top_user_recommendation(user_id, ratings, movies, embeddings, top_k=5, min_rating=4):
    movie_id_to_index = {movie_id: i for i, movie_id in enumerate(movies["MovieID"])}
    user_ratings = ratings[
        (ratings["UserID"] == user_id) &
        (ratings["Rating"] >= min_rating)].copy()
    user_ratings = user_ratings[user_ratings["MovieID"].isin(movie_id_to_index.keys())]
    rated_indices = [movie_id_to_index[movie_id]for movie_id in user_ratings["MovieID"]]
    user_embedding = embeddings[rated_indices].mean(axis=0).reshape(1, -1)
    similarity = cosine_similarity(user_embedding, embeddings)[0]
    already_rated = set(user_ratings["MovieID"])
    candidate_indices = [
        i for i, movie_id in enumerate(movies["MovieID"])
        if movie_id not in already_rated]
    ranked_indices = sorted(
        candidate_indices,
        key=lambda i: similarity[i],
        reverse=True
    )
    top_indices = ranked_indices[:top_k]
    recs = movies.iloc[top_indices][["MovieID", "Title", "Genres", "Year"]].copy()
    recs["Similarity"] = similarity[top_indices]
    return recs

def generate_recommendations(**context):
    movies = pd.read_csv(LOCAL_MOVIES_PATH)
    embeddings = np.load(LOCAL_EMBEDDINGS_PATH)

    if "Year" not in movies.columns:
        movies["Year"] = movies["Title"].str.extract(r"\((\d{4})\)")

    simulated_hours = [0, 10, 20, 30]
    observed_ratings = pd.DataFrame()

    os.makedirs("/tmp/hw4/recommendations", exist_ok=True)

    for i in range(1, 5):
        part = pd.read_csv(f"/tmp/hw4/ratings_part_{i}.csv")
        part["Datetime"] = pd.to_datetime(part["Datetime"])

        simulated_hour = simulated_hours[i - 1]

        observed_ratings = pd.concat(
            [observed_ratings, part],
            ignore_index=True
        )

        sampled_users = pd.Series(observed_ratings["UserID"].unique()).sample(
            frac=0.30,
            random_state=42 + i
        )

        sampled_ratings = observed_ratings[
            observed_ratings["UserID"].isin(sampled_users)
        ].copy()

        cold_recs = cold_user_recommendation(
            movies,
            embeddings,
            top_k=5
        )

        top_user_id, top_user_interactions = select_top_user(sampled_ratings)

        top_recs = top_user_recommendation(
            top_user_id,
            observed_ratings,
            movies,
            embeddings,
            top_k=5
        )

        top_user_history = observed_ratings[
            observed_ratings["UserID"] == top_user_id
        ]

        output_rows = []

        for _, row in cold_recs.iterrows():
            output_rows.append({
                "Iteration": i,
                "Simulated_Hour": simulated_hour,
                "User_Type": "Cold User",
                "User_ID": None,
                "Last_Interaction_Time": None,
                "Number_Of_Ratings_Observed": 0,
                "Recommended_MovieID": row["MovieID"],
                "Recommended_Title": row["Title"],
                "Recommended_Genres": row["Genres"],
                "Similarity": row["Similarity"]
            })

        for _, row in top_recs.iterrows():
            output_rows.append({
                "Iteration": i,
                "Simulated_Hour": simulated_hour,
                "User_Type": "Top User",
                "User_ID": top_user_id,
                "Last_Interaction_Time": top_user_history["Datetime"].max(),
                "Number_Of_Ratings_Observed": len(top_user_history),
                "Recommended_MovieID": row["MovieID"],
                "Recommended_Title": row["Title"],
                "Recommended_Genres": row["Genres"],
                "Similarity": row["Similarity"]
            })

        results = pd.DataFrame(output_rows)

        output_path = f"/tmp/hw4/recommendations/recommendations_iteration_{i}_hour_{simulated_hour}.csv"
        results.to_csv(output_path, index=False)

        print(f"Generated {output_path}")
        print(results)

    return "recommendations generated"


with DAG(
    dag_id="hw4_recommendations",
    default_args=default_args,
    description="HW4 recommendation DAG using MovieLens partitions and BERT embeddings",
    schedule=WORKFLOW_SCHEDULE,
    catchup=False,
    tags=["de300", "hw4", "recommendations"],
) as dag:

    t_partition = PythonOperator(
        task_id="load_and_partition_ratings",
        python_callable=load_and_partition_ratings,
    )

    t_generate = PythonOperator(
        task_id="generate_recommendations",
        python_callable=generate_recommendations,
    )

    t_partition >> t_generate