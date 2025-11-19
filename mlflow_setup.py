import mlflow

mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_registry_uri("s3://autocare-ml-bucket/mlflow")

print("MLflow configured successfully!")
