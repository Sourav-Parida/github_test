
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# Function 1: Load and clean data
def load_and_clean_data(filepath):

    df = pd.read_csv(filepath)

    # Remove duplicate records
    df = df.drop_duplicates(subset="RecordID", keep="first")

    # Convert Fahrenheit to Celsius
    mask = df["AmbientTempC"] > 60

    df.loc[mask, "AmbientTempC"] = (
        (df.loc[mask, "AmbientTempC"] - 32) * 5 / 9
    ).round(1)

    # Remove invalid rows

    df = df[
    (df["CloudCoverPct"].isna() | df["CloudCoverPct"].between(0, 100)) &
    (df["SunshineHours"].isna() | df["SunshineHours"].between(0, 14)) &
    (df["CapacityKW"].isna() | (df["CapacityKW"] > 0))
    ]

    # Numerical columns
    numerical_cols = [
        "CapacityKW", "SunshineHours", "CloudCoverPct",
        "AmbientTempC", "DustIndex", "DaysSinceCleaning"
    ]

    for col in numerical_cols:
        df[col] = df[col].fillna(df[col].median())

    # Categorical columns
    categorical_cols = ["Plant", "PanelType", "TrackerType"]

    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Reset index
    df = df.reset_index(drop=True)

    # Save cleaned data
    df.to_csv("cleaned_solar_data.csv", index=False)

    return df


# Function 2: Add features
def add_features(df):

    df = df.copy()

    df["EffectiveSunHours"] = (
        df["SunshineHours"] *
        (1 - df["CloudCoverPct"] / 100)
    ).round(2)

    return df


# Function 3: Build pipeline
def build_pipeline(max_depth=8, min_samples_leaf=10):

    numerical_features = [
        "CapacityKW", "SunshineHours", "CloudCoverPct",
        "AmbientTempC", "DustIndex", "DaysSinceCleaning",
        "EffectiveSunHours"
    ]

    categorical_features = [
        "Plant", "PanelType", "TrackerType"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numerical_features),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features
            )
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                DecisionTreeRegressor(
                    max_depth=max_depth,
                    min_samples_leaf=min_samples_leaf,
                    random_state=42
                )
            )
        ]
    )

    return pipeline


# Feature columns
FEATURES = [
    "CapacityKW", "SunshineHours", "CloudCoverPct",
    "AmbientTempC", "DustIndex", "DaysSinceCleaning",
    "EffectiveSunHours", "Plant", "PanelType", "TrackerType"
]


# Function 4: Train model
def train_model(df):

    X = df[FEATURES]
    y = df["EnergyKWh"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = build_pipeline()

    model.fit(X_train, y_train)

    # Save model
    joblib.dump(model, "solar_energy_model.joblib")

    return model, X_test, y_test


# Function 5: Evaluate model
def evaluate_model(model, X_test, y_test):

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    return {
        "MAE": round(float(mae), 2),
        "R2": round(float(r2), 2)
    }


# Function 6: Compare tree depths
def compare_depths(df):

    X = df[FEATURES]
    y = df["EnergyKWh"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    results = []

    for depth in [2, 8, None]:

        model = build_pipeline(
            max_depth=depth,
            min_samples_leaf=1
        )

        model.fit(X_train, y_train)

        train_r2 = model.score(X_train, y_train)
        test_r2 = model.score(X_test, y_test)

        results.append({
            "MaxDepth": str(depth),
            "TrainR2": round(float(train_r2), 2),
            "TestR2": round(float(test_r2), 2)
        })

    return pd.DataFrame(results)


# Function 7: Get feature importance
def get_feature_importance(model):

    feature_names = (
        model.named_steps["preprocessor"].get_feature_names_out()
    )

    # Remove num__ and cat__ prefixes
    feature_names = [
        name.split("__", 1)[-1] for name in feature_names
    ]

    importances = model.named_steps["model"].feature_importances_

    df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importances
    })

    df = df.sort_values(
        by="Importance",
        ascending=False
    ).head(5)

    df["Importance"] = df["Importance"].round(3)

    return df.reset_index(drop=True)


# Function 8: Predict energy
def predict_energy(model_path, filepath):

    model = joblib.load(model_path)

    df = pd.read_csv(filepath)

    df = add_features(df)

    predictions = model.predict(df[FEATURES])

    df["PredictedEnergyKWh"] = np.round(predictions, 1)

    # Save predictions
    df.to_csv("predicted_energy_output.csv", index=False)

    return df


# Main execution
if __name__ == "__main__":

    df = load_and_clean_data("solar_plant_data.csv")

    print("Rows after cleaning:", len(df))

    df = add_features(df)

    model, X_test, y_test = train_model(df)

    metrics = evaluate_model(model, X_test, y_test)

    print("Evaluation Metrics:", metrics)

    print("Depth Comparison:")
    depth_results = compare_depths(df)
    print(depth_results)

    print("Top 5 Features:")
    importance = get_feature_importance(model)
    print(importance)

    result = predict_energy(
        "solar_energy_model.joblib",
        "forecast_days.csv"
    )

    print("Top 5 Predictions:")
    print(
        result[
            ["RecordID", "PredictedEnergyKWh"]
        ].head(5)
    )
