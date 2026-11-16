
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, roc_auc_score


# Global column definitions

fill_num = [
    "Nights", "Adults", "AvgDailyRate",
    "SpecialRequests", "PreviousCancellations"
]

num_cols = fill_num + ["LeadDays"]

cat_cols = [
    "HotelType", "BookingChannel",
    "MealPlan", "DepositType"
]


# Function 1: Load and clean data
def load_and_clean_data(filepath):

    df = pd.read_csv(filepath)

    # Convert dates
    df["BookingDate"] = pd.to_datetime(df["BookingDate"])
    df["ArrivalDate"] = pd.to_datetime(df["ArrivalDate"])

    # Remove duplicate BookingIDs
    df = df.drop_duplicates(subset="BookingID", keep="first")

    # Remove invalid bookings
    valid_arrival = df["ArrivalDate"] >= df["BookingDate"]

    valid_nights = ( df["Nights"].isna() | (df["Nights"] > 0))

    valid_guests = (
        df["Adults"].isna() |
        df["Children"].isna() |
        ((df["Adults"] + df["Children"]) > 0)
    )

    valid_rate = (
        df["AvgDailyRate"].isna() | (df["AvgDailyRate"] >= 0)
    )

    df = df [valid_arrival & valid_nights & valid_guests & valid_rate]

    # Fill missing Children with 0
    df["Children"] = df["Children"].fillna(0)

    # Fill missing numerical values with median
    for col in fill_num:
        df[col] = df[col].fillna(df[col].median())

    # Fill missing categorical values with mode
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Reset index
    df = df.reset_index(drop=True)

    # Save cleaned data
    df.to_csv("cleaned_bookings.csv", index=False)

    return df


# Function 2: Add features
def add_features(df):

    df = df.copy()

    df["BookingDate"] = pd.to_datetime(df["BookingDate"])
    df["ArrivalDate"] = pd.to_datetime(df["ArrivalDate"])

    # Calculate lead days
    df["LeadDays"] = (df["ArrivalDate"] - df["BookingDate"]).dt.days

    # Calculate total guests
    df["TotalGuests"] = df["Adults"] + df["Children"]

    return df


# Function 3: Build pipeline
def build_pipeline():

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat",OneHotEncoder(handle_unknown="ignore"),cat_cols)
    ])

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(max_iter=1000))
    ])

    return pipeline


# Function 4: Train model
def train_model(df):

    X = df[num_cols + cat_cols]

    y = df["IsCanceled"].map({"Yes": 1,"No": 0})

    X_train, X_test, y_train, y_test = train_test_split(
        X,y,test_size=0.2,random_state=42,stratify=y)

    model = build_pipeline()

    model.fit(X_train, y_train)

    # Save model
    joblib.dump(model, "cancellation_model.joblib")

    return model, X_test, y_test


# Function 5: Evaluate model
def evaluate_model(model, X_test, y_test):

    y_pred = model.predict(X_test)

    probabilities = model.predict_proba(X_test)[:, 1]

    return {
        "Precision": round(float(precision_score(y_test, y_pred)),2),
        "Recall": round(float(recall_score(y_test, y_pred)), 2),
        "ROC_AUC": round(float(roc_auc_score(y_test, probabilities)), 2)
    }


# Function 6: Predict cancellations
def predict_cancellations(model_path, filepath):

    model = joblib.load(model_path)

    df = pd.read_csv(filepath)

    df = add_features(df)

    probabilities = model.predict_proba(
        df[num_cols + cat_cols]
    )[:, 1]

    df["CancelProbability"] = np.round(probabilities, 2)

    # Assign risk levels using original probabilities
    df["RiskLevel"] = np.where(probabilities >= 0.7,"High",
                                np.where(probabilities >= 0.4,"Medium","Low")
    )

    # Save predictions
    df.to_csv("predicted_cancellations.csv", index=False)

    return df


# Main execution
if __name__ == "__main__":

    df = load_and_clean_data("hotel_bookings.csv")
    print("Rows after cleaning:", len(df))

    df = add_features(df)

    model, X_test, y_test = train_model(df)

    print(
        "Evaluation Metrics:",
        evaluate_model(model, X_test, y_test)
    )

    result = predict_cancellations(
        "cancellation_model.joblib",
        "new_bookings.csv"
    )

    # Count risk levels
    counts = {
        "High": int((result["RiskLevel"] == "High").sum()),
        "Medium": int((result["RiskLevel"] == "Medium").sum()),
        "Low": int((result["RiskLevel"] == "Low").sum())
    }

    print("Risk Level Counts:", counts)

    print("Top 5 Predictions:")

    print(
        result[
            ["BookingID", "CancelProbability", "RiskLevel"]
        ].head(5)
    )
