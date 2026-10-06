import os
import boto3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

raw_path = "data/raw/covid_data.csv"
processed_path = "data/processed/covid_processed.csv"

df = pd.read_csv(raw_path)

df["Day"] = pd.to_datetime(df["Day"])
df = df.dropna(subset=["Entity", "Day", "Weekly cases"])
df = df.drop_duplicates()
df = df.sort_values(["Entity", "Day"])

df["Year"] = df["Day"].dt.year
df["Month"] = df["Day"].dt.month

df.to_csv(processed_path, index=False)

print("Data processed successfully!")
print("Rows:", len(df))

s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

bucket = os.getenv("S3_BUCKET_NAME")

s3.upload_file(
    processed_path,
    bucket,
    "processed_data/covid_processed.csv"
)

print("Processed data uploaded to S3 successfully!")
print("Path: processed_data/covid_processed.csv")