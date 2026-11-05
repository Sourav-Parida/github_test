
import pandas as pd
import numpy as np
import joblib

from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


NUMERIC_FEATURES = [
    "PM25", "PM10", "NO2", "CO",
    "TemperatureC", "HumidityPct",
    "WindSpeedKmph", "TrafficIndex"
]

CATEGORICAL_FEATURES = ["City", "Season"]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


# Function 1: Load and clean data
def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)

    # Remove duplicate records
    df = df.drop_duplicates(subset="RecordID", keep="first")

    # Replace sensor error codes with NaN
    pollutant_columns = ["PM25", "PM10", "NO2", "CO"]
    df[pollutant_columns] = df[pollutant_columns].replace(-999, np.nan)

    # Remove invalid rows (retain missing values)
    df = df[
        ~(
            (df["HumidityPct"] < 0) |
            (df["HumidityPct"] > 100) |
            (df["WindSpeedKmph"] < 0) |
            (df["AQI"] <= 0)
        )
    ].copy()

    # Sort by city and date
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(
        by=["City", "Date"]
    ).reset_index(drop=True)

    # Forward fill within each city, then fill remaining NaNs with median
    for col in NUMERIC_FEATURES:
        df[col] = df.groupby("City")[col].ffill()
        df[col] = df[col].fillna(df[col].median())

    # Save cleaned data
    df.to_csv("cleaned_air_quality.csv", index=False)

    return df


# Function 2: Add season feature
def add_features(df):
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])

    month = df["Date"].dt.month

    conditions = [
        month.isin([12, 1, 2]),
        month.isin([3, 4, 5]),
        month.isin([6, 7, 8, 9]),
        month.isin([10, 11])
    ]

    choices = [
        "Winter",
        "Summer",
        "Monsoon",
        "PostMonsoon"
    ]

    df["Season"] = np.select(conditions, choices)

    return df


# Function 3: Build SVR model
def build_model(kernel="rbf", C=10, epsilon=0.1):
    numeric_transformer = StandardScaler()

    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore"
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERIC_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", SVR(
                kernel=kernel,
                C=C,
                epsilon=epsilon
            ))
        ]
    )

    model = TransformedTargetRegressor(
        regressor=pipeline,
        transformer=StandardScaler()
    )

    return model


# Function 4: Train model
def train_model(df):
    X = df[FEATURES]
    y = df["AQI"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = build_model()
    model.fit(X_train, y_train)

    joblib.dump(model, "aqi_model.joblib")

    return model, X_test, y_test


# Function 5: Evaluate model
def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    return {
        "MAE": round(float(mae), 2),
        "RMSE": round(float(rmse), 2)
    }


# Function 6: Compare SVR kernels
def compare_kernels(df):
    X = df[FEATURES]
    y = df["AQI"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    results = []

    for kernel in ["linear", "rbf", "poly"]:
        model = build_model(kernel=kernel)
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        score = r2_score(y_test, predictions)

        results.append({
            "Kernel": kernel,
            "TestR2": round(float(score), 2)
        })

    return pd.DataFrame(results)


# Function 7: Predict AQI
def predict_aqi(model_path, filepath):
    model = joblib.load(model_path)

    df = pd.read_csv(filepath)
    df = add_features(df)

    predictions = model.predict(df[FEATURES])

    # Round to whole number and replace negative values with 0
    df["PredictedAQI"] = np.maximum(
        np.round(predictions), 0
    ).astype(int)

    # Assign AQI categories
    def get_category(aqi):
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Satisfactory"
        elif aqi <= 200:
            return "Moderate"
        elif aqi <= 300:
            return "Poor"
        elif aqi <= 400:
            return "Very Poor"
        else:
            return "Severe"

    df["AQICategory"] = df["PredictedAQI"].apply(get_category)

    df.to_csv("predicted_aqi.csv", index=False)

    return df


# Main execution block
if __name__ == "__main__":

    # Load and clean data
    cleaned_df = load_and_clean_data("city_air_quality.csv")
    print("Rows after cleaning:", len(cleaned_df))

    # Add features
    featured_df = add_features(cleaned_df)

    # Train model
    model, X_test, y_test = train_model(featured_df)

    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test)
    print("Evaluation Metrics:", metrics)

    # Compare kernels
    print("Kernel Comparison:")
    comparison = compare_kernels(featured_df)
    print(comparison)

    # Predict AQI
    predictions_df = predict_aqi(
        "aqi_model.joblib",
        "forecast_inputs.csv"
    )

    # Print category counts in required order
    categories = [
        "Good",
        "Satisfactory",
        "Moderate",
        "Poor",
        "Very Poor",
        "Severe"
    ]

    category_counts = (
        predictions_df["AQICategory"]
        .value_counts()
        .reindex(categories, fill_value=0)
        .to_dict()
    )

    print("AQI Category Counts:", category_counts)

    # Print top 5 predictions
    print("Top 5 Predictions:")
    print(
        predictions_df[
            ["RecordID", "City", "PredictedAQI", "AQICategory"]
        ].head(5)
    )
