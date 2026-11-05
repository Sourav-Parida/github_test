
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# Function 1: Load and clean data
def load_and_clean_data(filepath):

    df = pd.read_csv(filepath)

    # Remove duplicate LaptopIDs
    df = df.drop_duplicates(subset="LaptopID", keep="first")

    # Remove invalid rows
    # df = df[(df["ResalePrice"] > 0) & 
    #         (df["BatteryHealth"].isna() | ((df["BatteryHealth"] >= 0) & (df["BatteryHealth"] <= 100)))
    # ]

    valid_price = df["ResalePrice"] > 0
    
    valid_battery = (
        df["BatteryHealth"].isna() |
        df["BatteryHealth"].between(0, 100)
    )

    df = df[valid_price & valid_battery]

    # Numerical columns
    numerical_cols = [
        "RAM_GB", "Storage_GB", "ScreenSize",
        "AgeYears", "BatteryHealth"
    ]

    # Categorical columns
    categorical_cols = [
        "Brand", "Processor", "StorageType", "Condition"
    ]

    # Fill missing numerical values with median
    for col in numerical_cols:
        df[col] = df[col].fillna(df[col].median())

    # Fill missing categorical values with mode
    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Reset index
    df = df.reset_index(drop=True)

    # Save cleaned data
    df.to_csv("cleaned_laptop_data.csv", index=False)

    return df


# Function 2: Add features
def add_features(df):

    df = df.copy()

    df["PerformanceScore"] = (df["RAM_GB"] / 4 + df["Storage_GB"] / 256).round(2)

    return df


# Function 3: Build pipeline
def build_pipeline():

    numerical_features = [
        "RAM_GB", "Storage_GB", "ScreenSize",
        "AgeYears", "BatteryHealth", "PerformanceScore"
    ]

    categorical_features = [
        "Brand", "Processor", "StorageType", "Condition"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"),
            categorical_features)
        ]
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", LinearRegression())
        ]
    )

    return pipeline


# Function 4: Train model
def train_model(df):

    features = [
        "RAM_GB", "Storage_GB", "ScreenSize",
        "AgeYears", "BatteryHealth", "PerformanceScore",
        "Brand", "Processor", "StorageType", "Condition"
    ]

    X = df[features]
    y = df["ResalePrice"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = build_pipeline()

    model.fit(X_train, y_train)

    # Save model
    joblib.dump(model, "laptop_price_model.joblib")

    return model, X_test, y_test


# Function 5: Evaluate model
def evaluate_model(model, X_test, y_test):

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    return {
        "MAE": round(float(mae), 2),
        "RMSE": round(float(rmse), 2),
        "R2": round(float(r2), 2)
    }


# Function 6: Predict prices
def predict_prices(model_path, filepath):

    model = joblib.load(model_path)

    df = pd.read_csv(filepath)

    df = add_features(df)

    features = [
        "RAM_GB", "Storage_GB", "ScreenSize",
        "AgeYears", "BatteryHealth", "PerformanceScore",
        "Brand", "Processor", "StorageType", "Condition"
    ]

    predictions = model.predict(df[features])

    df["PredictedPrice"] = np.round(predictions, 2)

    # Save predictions
    df.to_csv("predicted_laptop_prices.csv", index=False)

    return df


# Main execution
if __name__ == "__main__":

    df = load_and_clean_data("laptop_resale_data.csv")

    print("Rows after cleaning:", len(df))

    df = add_features(df)

    model, X_test, y_test = train_model(df)

    metrics = evaluate_model(model, X_test, y_test)

    print("Evaluation Metrics:", metrics)

    result = predict_prices(
        "laptop_price_model.joblib",
        "new_laptops.csv"
    )

    print("Top 5 Predictions:")
    print(result[["LaptopID", "PredictedPrice"]].head(5))
