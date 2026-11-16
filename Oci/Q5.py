
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.metrics import recall_score, f1_score, confusion_matrix


# Global column definitions

fill_num = [
    "DurationSec", "SrcBytes", "DstBytes",
    "FailedLogins", "ConnCount", "SameSrvRate",
    "ErrorRate"
]

num_cols = [
    "DurationSec", "LogSrcBytes", "LogDstBytes",
    "FailedLogins", "ConnCount", "SameSrvRate",
    "ErrorRate"
]

cat_cols = ["Protocol", "Service", "Flag"]

FEATURES = num_cols + cat_cols


# Function 1: Load and clean data
def load_and_clean_data(filepath):

    df = pd.read_csv(filepath)

    # Remove duplicate ConnectionIDs
    df = df.drop_duplicates(subset="ConnectionID", keep="first")

    # Remove invalid rows
    valid_duration = (
        df["DurationSec"].isna() |
        (df["DurationSec"] >= 0)
    )

    valid_src = (df["SrcBytes"].isna() |(df["SrcBytes"] >= 0))

    valid_dst = (
        df["DstBytes"].isna() |(df["DstBytes"] >= 0)
    )

    valid_same_srv = (
        df["SameSrvRate"].isna() | df["SameSrvRate"].between(0, 1)
    )

    valid_error = (
        df["ErrorRate"].isna() | df["ErrorRate"].between(0, 1)
    )

    df = df[
        valid_duration &
        valid_src &
        valid_dst &
        valid_same_srv &
        valid_error
    ]

    # Fill missing numerical values with median
    for col in fill_num:
        df[col] = df[col].fillna(df[col].median())

    # Fill missing categorical values with mode
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Reset index
    df = df.reset_index(drop=True)

    # Save cleaned data
    df.to_csv("cleaned_traffic.csv", index=False)

    return df


# Function 2: Add features
def add_features(df):

    df = df.copy()

    df["LogSrcBytes"] = np.log1p(df["SrcBytes"]).round(3)

    df["LogDstBytes"] = np.log1p(df["DstBytes"]).round(3)

    return df


# Function 3: Build pipeline
def build_pipeline(C=1.0, gamma="scale"):

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore"),
            cat_cols
        )
    ])

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        (
            "model",
            SVC(
                kernel="rbf",
                C=C,
                gamma=gamma,
                class_weight="balanced"
            )
        )
    ])

    return pipeline


# Function 4: Split data
def split_data(df):

    X = df[num_cols + cat_cols]

    y = df["Label"].map({
        "Attack": 1,
        "Normal": 0
    })

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    return X_train, X_test, y_train, y_test


# Function 5: Tune hyperparameters
def tune_hyperparameters(X_train, y_train):

    pipeline = build_pipeline()

    param_grid = {
        "model__C": [0.5, 1, 5],
        "model__gamma": ["scale", 0.05]
    }

    grid = GridSearchCV(
        pipeline,
        param_grid,
        cv=3,
        scoring="f1"
    )

    grid.fit(X_train, y_train)

    return {
        "C": grid.best_params_["model__C"],
        "gamma": grid.best_params_["model__gamma"],
        "CV_F1": round(float(grid.best_score_), 2)
    }


# Function 6: Train model
def train_model(X_train, y_train, C, gamma):

    model = build_pipeline(C=C, gamma=gamma)

    model.fit(X_train, y_train)

    # Save model
    joblib.dump(model, "intrusion_model.joblib")

    return model


# Function 7: Evaluate model
def evaluate_model(model, X_test, y_test):

    y_pred = model.predict(X_test)

    recall = recall_score(y_test, y_pred)

    f1 = f1_score(y_test, y_pred)

    cm = confusion_matrix(y_test, y_pred)

    # False positives: Normal predicted as Attack
    false_positives = int(cm[0, 1])

    return {
        "Recall": round(float(recall), 2),
        "F1": round(float(f1), 2),
        "FalsePositives": false_positives
    }


# Function 8: Predict connections
def predict_connections(model_path, filepath):

    model = joblib.load(model_path)

    df = pd.read_csv(filepath)

    df = add_features(df)

    # Get decision scores
    scores = model.decision_function(df[num_cols + cat_cols])

    df["AttackScore"] = np.round(scores, 2)

    # Predicted labels
    df["PredictedLabel"] = np.where(scores >= 0,"Attack","Normal")

    # Assign alert levels using original scores
    df["AlertLevel"] = np.where(scores >= 0.5,"Critical",
        np.where(scores >= -0.5,"Suspicious","Normal")
    )

    # Save predictions
    df.to_csv("flagged_connections.csv", index=False)

    return df


# Main execution
if __name__ == "__main__":

    df = load_and_clean_data("network_traffic.csv")

    print("Rows after cleaning:", len(df))

    df = add_features(df)

    X_train, X_test, y_train, y_test = split_data(df)

    best_params = tune_hyperparameters(X_train, y_train)

    print("Best Parameters:", best_params)

    model = train_model(
        X_train,
        y_train,
        best_params["C"],
        best_params["gamma"]
    )

    print(
        "Evaluation Metrics:",
        evaluate_model(model, X_test, y_test)
    )

    result = predict_connections(
        "intrusion_model.joblib",
        "live_connections.csv"
    )

    # Count alert levels
    counts = {
        "Critical": int((result["AlertLevel"] == "Critical").sum()),
        "Suspicious": int((result["AlertLevel"] == "Suspicious").sum()),
        "Normal": int((result["AlertLevel"] == "Normal").sum())
    }

    print("Alert Level Counts:", counts)

    print("Top 5 Predictions:")

    print(result[["ConnectionID","AttackScore","PredictedLabel","AlertLevel"]].head(5))
