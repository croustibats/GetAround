import argparse
import os
import pandas as pd
import time
import mlflow
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split 
from sklearn.preprocessing import  StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline


if __name__ == "__main__":

    ### MLFLOW Experiment setup
    experiment_name="pricing_optimization"
    mlflow.set_experiment(experiment_name)
    experiment = mlflow.get_experiment_by_name(experiment_name)

    client = mlflow.tracking.MlflowClient()
    #mlflow.set_tracking_uri(os.environ["BACKEND_STORE_URI"])

    run = client.create_run(experiment.experiment_id)

    print("training model...")
    print(mlflow.tracking.get_tracking_uri())
    
    # Time execution
    start_time = time.time()

    # Call mlflow autolog
    mlflow.sklearn.autolog(log_models=False) # We won't log models right away

    # Parse arguments given in shell script
    parser = argparse.ArgumentParser()
    parser.add_argument("--n_estimators", default=1)
    parser.add_argument("--min_samples_split", default=2)
    args = parser.parse_args()

    # Import dataset
    df = pd.read_csv("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv")

    df = df.drop(columns='Unnamed: 0')

    # X, y split 
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    # Train / test split 
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2)

    print(df.columns)

    # Preprocessing

    for col in df.select_dtypes('bool'):
        df[col] = df[col].apply(lambda x: 1 if x else 0)

    # Preprocessing 
    categorical_features = X_train.select_dtypes("object").columns # Select all the columns containing strings
    categorical_transformer = OneHotEncoder(drop='first', handle_unknown='error', sparse=False)

    numerical_features = X_train.select_dtypes("int").columns
    numerical_transformer = StandardScaler()

    feature_preprocessor = ColumnTransformer(
        transformers=[
            ("categorical_transformer", categorical_transformer, categorical_features),
            ("numerical_transformer", numerical_transformer, numerical_features)
        ]
    )

    # Pipeline 
    n_estimators = int(args.n_estimators)
    min_samples_split=int(args.min_samples_split)

    model = Pipeline(steps=[
        ('features_preprocessing', feature_preprocessor),
        ("Regressor",RandomForestRegressor(n_estimators=n_estimators, min_samples_split=min_samples_split))
    ])

    #mlflow.sklearn.autolog()
    print(os.environ["ARTIFACT_ROOT"])

    # Log experiment to MLFlow
    with mlflow.start_run() as run:
        print(mlflow.get_artifact_uri())
        model.fit(X_train, y_train)
        predictions = model.predict(X_train)
        # Log model seperately to have more flexibility on setup 

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="pricing_optimization",
            registered_model_name="pricing_optimization_RF",
            signature=infer_signature(X_train, predictions)
        )

    print("...Done!")
    print(f"---Total training time: {time.time()-start_time}")