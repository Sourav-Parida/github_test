
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# Global column definitions

fill_num = [
    "CapacityKW", "SunshineHours", "CloudCoverPct",
    "AmbientTempC", "DustIndex", "DaysSinceCleaning"
]

num_cols = ["EffectiveSunHours"]+fill_num

cat_cols = [
    "Plant", "PanelType", "TrackerType"
]

FEATURES = num_cols + cat_cols


# Function 1: Load and clean data
def load_and_clean_data(filepath):

    df = pd.read_csv(filepath)

    # Remove duplicate RecordIDs
    df = df.drop_duplicates(subset="RecordID", keep="first")

    # Convert Fahrenheit to Celsius
    mask = df["AmbientTempC"] > 60

    df.loc[mask, "AmbientTempC"] = ((df.loc[mask, "AmbientTempC"] - 32) * 5 / 9).round(1)

    # Remove invalid rows
    valid_cloud = (
        df["CloudCoverPct"].isna() |
        df["CloudCoverPct"].between(0, 100)
    )

    valid_sunshine = (
        df["SunshineHours"].isna() |
        df["SunshineHours"].between(0, 14)
    )

    valid_capacity = (
        df["CapacityKW"].isna() |
        (df["CapacityKW"] > 0)
    )

    df = df[
        valid_cloud &
        valid_sunshine &
        valid_capacity
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
    df.to_csv("cleaned_solar_data.csv", index=False)

    return df


# Function 2: Add features
def add_features(df):

    df = df.copy()

    df["EffectiveSunHours"] = (df["SunshineHours"] *(1 - df["CloudCoverPct"] / 100)).round(2)

    return df


# Function 3: Build pipeline
def build_pipeline(max_depth=8, min_samples_leaf=10):

    preprocessor = ColumnTransformer([
        ("num", "passthrough", num_cols),
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
            DecisionTreeRegressor(
                max_depth=max_depth,
                min_samples_leaf=min_samples_leaf,
                random_state=42
            )
        )
    ])

    return pipeline


# Function 4: Train model
def train_model(df):

    X = df[num_cols + cat_cols]
    y = df["EnergyKWh"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,y,test_size=0.2,random_state=42
    )

    model = build_pipeline()

    model.fit(X_train, y_train)

    # Save model
    joblib.dump(model, "solar_energy_model.joblib")

    return model, X_test, y_test


# Function 5: Evaluate model
def evaluate_model(model, X_test, y_test):

    y_pred = model.predict(X_test)

    return {
        "MAE": round(float(mean_absolute_error(y_test, y_pred)), 2),
        "R2": round(float(r2_score(y_test, y_pred)), 2)
    }


# Function 6: Compare tree depths
def compare_depths(df):

    X = df[num_cols + cat_cols]
    y = df["EnergyKWh"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
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
        model.named_steps["preprocessor"]
        .get_feature_names_out()
    )

    # Remove num__ and cat__ prefixes
    feature_names = [
        name.split("__", 1)[-1]
        for name in feature_names
    ]

    importances = (
        model.named_steps["model"].feature_importances_
    )

    df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importances
    })

    # Sort by importance and get top 5
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

    print(
        "Evaluation Metrics:",
        evaluate_model(model, X_test, y_test)
    )

    print("Depth Comparison:")
    print(compare_depths(df))

    print("Top 5 Features:")
    print(get_feature_importance(model))

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
