
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score



fill_num=["RAM_GB", "Storage_GB", "ScreenSize",
    "AgeYears", "BatteryHealth"]

num_cols = fill_num + ["PerformanceScore"]

cat_cols= [
    "Brand", "Processor", "StorageType", "Condition"
    ]

# Function 1: Load and clean data
def load_and_clean_data(filepath):

    df = pd.read_csv(filepath)

    # Remove duplicate LaptopIDs
    df = df.drop_duplicates(subset="LaptopID", keep="first")

    valid_price = df["ResalePrice"] > 0
    
    valid_battery = (
        df["BatteryHealth"].isna() |
        df["BatteryHealth"].between(0, 100)
    )

    df = df[valid_price & valid_battery]

    # Fill missing numerical values with median
    for col in fill_num:
        df[col] = df[col].fillna(df[col].median())

    # Fill missing categorical values with mode
    for col in cat_cols:
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

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"),cat_cols)
    ])

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", LinearRegression())
    ])

    return pipeline 


# Function 4: Train model
def train_model(df):

    X = df[num_cols + cat_cols]
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

    y_pred = model.predict(X_test)

    return {
        "MAE": round(float(mean_absolute_error(y_test, y_pred)), 2),
        "RMSE": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 2),
        "R2": round(float(r2_score(y_test, y_pred)), 2)
    }


# Function 6: Predict prices
def predict_prices(model_path, filepath):

    model = joblib.load(model_path)
    df = pd.read_csv(filepath)
    df = add_features(df)
    predictions = model.predict(df[num_cols + cat_cols])
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

    print("Evaluation Metrics:", evaluate_model(model, X_test, y_test))

    result = predict_prices(
        "laptop_price_model.joblib",
        "new_laptops.csv"
    )

    print("Top 5 Predictions:")
    print(result[["LaptopID", "PredictedPrice"]].head(5))
