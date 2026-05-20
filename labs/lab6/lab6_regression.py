from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum
import pandas as pd
import boto3
import json
import pickle
from io import StringIO, BytesIO
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


WORKFLOW_SCHEDULE = "@daily"

SOURCE_BUCKET = "de300-airflow-yash-margaret"
SOURCE_KEY = "lab6/inputs/cars.csv"

OUTPUT_BUCKET = "de300-airflow-yash-margaret"
FEATURE_COLS = ["Weight", "Drive Ratio", "Horsepower", "Displacement", "Cylinders"]
TARGET_COL = "MPG"

default_args = {
    "owner": "yash",
    "depends_on_past": False,
    "start_date": pendulum.today("UTC").add(days=-1),
    "retries": 1,
}
def read_data(**context):
    s3 = boto3.client("s3")
    obj = s3.get_object(Bucket=SOURCE_BUCKET, Key=SOURCE_KEY)
    csv_text = obj["Body"].read().decode("utf-8")
    df = pd.read_csv(StringIO(csv_text))
    df = df[FEATURE_COLS + [TARGET_COL]].dropna()
    print("Rows after cleaning:", len(df))
    print(df.head())
    return df.to_json(orient="records")

def split_data(**context):
    ti = context["ti"]
    load = ti.xcom_pull(task_ids="read_data")
    df = pd.read_json(StringIO(load), orient="records")
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    split_load = {
        "X_train": X_train.to_json(orient="records"),
        "X_test": X_test.to_json(orient="records"),
        "y_train": y_train.to_json(orient="records"),
        "y_test": y_test.to_json(orient="records"),
    }

    return split_load


def train_and_evaluate_model(**context):
    ti = context["ti"]
    split_load = ti.xcom_pull(task_ids="split_data")
    X_tr = pd.read_json(StringIO(split_load["X_train"]), orient="records")
    X_t = pd.read_json(StringIO(split_load["X_test"]), orient="records")
    y_tr = pd.Series(json.loads(split_load["y_train"]))
    y_t = pd.Series(json.loads(split_load["y_test"]))

    model = LinearRegression()
    model.fit(X_tr, y_tr)

    pred = model.predict(X_t)

    mse = mean_squared_error(y_t, pred)
    rmse = mse ** 0.5
    r2 = r2_score(y_t, pred)

    metrics = {
        "rmse": float(rmse),
        "r2": float(r2),
        "num_test_rows": int(len(y_t)),
        "features": FEATURE_COLS,
        "target": TARGET_COL,
    }

    print("METRICS_JSON_START")
    print(json.dumps(metrics, indent=2))
    print("METRICS_JSON_END")
    return metrics
with DAG(
    dag_id="lab6_linear_regression",
    default_args=default_args,
    description="Lab 6 DAG for linear regression on cars.csv",
    schedule=WORKFLOW_SCHEDULE,
    catchup=False,
    tags=["de300", "lab6", "linear-regression"],
) as dag:
    t_read = PythonOperator(
        task_id="read_data",
        python_callable=read_data,
    )
    t_split = PythonOperator(
        task_id="split_data",
        python_callable=split_data,
    )
    t_train_eval = PythonOperator(
    task_id="train_and_evaluate_model",
    python_callable=train_and_evaluate_model,
) 
    t_read >> t_split >> t_train_eval


