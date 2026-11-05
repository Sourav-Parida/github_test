
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score


# Function 1: Load and clean data
def load_and_clean_data(filepath):

    df = pd.read_csv(filepath)

    # Remove duplicate FieldIDs
    df = df.drop_duplicates(subset="FieldID", keep="first")

    # Remove records with missing Crop
    df = df.dropna(subset=["Crop"])

    # Convert SoilPH to numeric
    df["SoilPH"] = (
        df["SoilPH"].astype(str)
        .str.replace("pH", "", regex=False)
        .str.replace(" ", "", regex=False)
    )

    df["SoilPH"] = pd.to_numeric(df["SoilPH"], errors="coerce")

    df = df[
    (df["SoilPH"].isna() | df["SoilPH"].between(0, 14)) &
    (df["HumidityPct"].isna() | df["HumidityPct"].between(0, 100)) &
    (df["Nitrogen"].isna() | (df["Nitrogen"] >= 0)) &
    (df["Phosphorus"].isna() | (df["Phosphorus"] >= 0)) &
    (df["Potassium"].isna() | (df["Potassium"] >= 0))
    ]

    # Categorical columns: fill with mode
    categorical_cols = [
        "Region", "SoilType", "IrrigationAvailable"
    ]

    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Numeric columns: fill with region-wise median
    numerical_cols = [
        "Nitrogen", "Phosphorus", "Potassium",
        "SoilPH", "RainfallMM", "TemperatureC",
        "HumidityPct"
    ]

    for col in numerical_cols:
        df[col] = df[col].fillna(
            df.groupby("Region")[col].transform("median")
        )

        # Fallback if a region has no available median
        df[col] = df[col].fillna(df[col].median())

    # Reset index
    df = df.reset_index(drop=True)

    # Save cleaned data
    df.to_csv("cleaned_crop_data.csv", index=False)

    return df


# Function 2: Add features
def add_features(df):

    df = df.copy()

    df["NutrientIndex"] = (
        (df["Nitrogen"] + df["Phosphorus"] + df["Potassium"]) / 3
    ).round(1)

    return df


# Function 3: Build pipeline
def build_pipeline():

    numerical_features = [
        "Nitrogen", "Phosphorus", "Potassium",
        "SoilPH", "RainfallMM", "TemperatureC",
        "HumidityPct", "NutrientIndex"
    ]

    categorical_features = [
        "Region", "SoilType", "IrrigationAvailable"
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
                DecisionTreeClassifier(
                    criterion="entropy",
                    max_depth=6,
                    min_samples_leaf=5,
                    class_weight="balanced",
                    random_state=42
                )
            )
        ]
    )

    return pipeline


# Feature columns
FEATURES = [
    "Nitrogen", "Phosphorus", "Potassium",
    "SoilPH", "RainfallMM", "TemperatureC",
    "HumidityPct", "NutrientIndex",
    "Region", "SoilType", "IrrigationAvailable"
]


# Function 4: Train model
def train_model(df):

    X = df[FEATURES]
    y = df["Crop"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = build_pipeline()

    model.fit(X_train, y_train)

    # Save model
    joblib.dump(model, "crop_model.joblib")

    return model, X_test, y_test


# Function 5: Evaluate model
def evaluate_model(model, X_test, y_test):

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro"
    )

    return {
        "Accuracy": round(float(accuracy), 2),
        "Macro_F1": round(float(macro_f1), 2)
    }


# Function 6: Get tree summary
def get_tree_summary(model):

    tree = model.named_steps["model"]

    return {
        "Depth": int(tree.get_depth()),
        "Leaves": int(tree.get_n_leaves())
    }


# Function 7: Predict crops
def predict_crops(model_path, filepath):

    model = joblib.load(model_path)
    df = pd.read_csv(filepath)
    df = add_features(df)

    # Get probabilities for each crop
    probabilities = model.predict_proba(df[FEATURES])

    # Get highest probability
    best_indices = np.argmax(probabilities, axis=1)
    recommended_crops = model.named_steps["model"].classes_[best_indices]
    confidence = probabilities.max(axis=1)
    df["RecommendedCrop"] = recommended_crops
    df["Confidence"] = np.round(confidence, 2)
    # Assign review status using unrounded confidence
    df["Review"] = np.where(
        confidence >= 0.6,
        "Auto Approve",
        "Expert Review"
    )

    # Save predictions
    df.to_csv("recommended_crops.csv", index=False)

    return df


# Main execution
if __name__ == "__main__":

    df = load_and_clean_data("crop_field_data.csv")

    print("Rows after cleaning:", len(df))

    df = add_features(df)

    model, X_test, y_test = train_model(df)

    metrics = evaluate_model(model, X_test, y_test)

    print("Evaluation Metrics:", metrics)

    summary = get_tree_summary(model)

    print("Tree Summary:", summary)

    result = predict_crops(
        "crop_model.joblib",
        "new_fields.csv"
    )

    expert_count = (
        result["Review"] == "Expert Review"
    ).sum()

    print("Fields sent for Expert Review:", int(expert_count))

    print("Top 5 Predictions:")

    print(
        result[
            [
                "FieldID",
                "RecommendedCrop",
                "Confidence",
                "Review"
            ]
        ].head(5)
    )
