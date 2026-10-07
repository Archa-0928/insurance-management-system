# import pandas as pd
# from sklearn.model_selection import train_test_split
# from sklearn.tree import DecisionTreeClassifier
# from sklearn.preprocessing import OneHotEncoder
# from sklearn.impute import SimpleImputer
# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline
# from sklearn.metrics import accuracy_score, classification_report
# import joblib
#
# # Load the dataset
# # file_path = r'C:\Users\cssre\OneDrive\Desktop\insurance claim\insurance\static\Worksheet in Case Study question 2.xlsx'
# file_path = r'C:\Users\GAYATHRI\Music\insurance\insurance claim\insurance\static\Worksheet in Case Study question 2.xlsx'
# df = pd.read_excel(file_path, sheet_name='Fraud_Detection_decsion tree')
#
# # Replace '?' with pd.NA for missing values
# df.replace('?', pd.NA, inplace=True)
#
# # Map target 'fraud_reported' to binary (Y=1, N=0)
# df['fraud_reported'] = df['fraud_reported'].map({'Y': 1, 'N': 0})
#
# # Convert datetime columns to numerical (days since a reference date)
# date_cols = ['policy_bind_date', 'incident_date']
# for col in date_cols:
#     if not pd.api.types.is_datetime64_any_dtype(df[col]):
#         df[col] = pd.to_datetime(df[col], origin='1899-12-30', unit='D')
#     df[col] = (df[col] - df[col].min()).dt.days.astype('float64')
#
# # Identify categorical and numerical columns
# categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
# numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
# numerical_cols = [col for col in numerical_cols if col != 'fraud_reported']  # Exclude target
#
# # Debug: Check for mixed types in categorical columns
# print("Checking categorical columns for mixed types:")
# for col in categorical_cols:
#     types = df[col].apply(lambda x: type(x).__name__).unique()
#     print(f"Column '{col}' has types: {types}")
#
# # Convert all categorical columns to strings to ensure uniformity
# for col in categorical_cols:
#     df[col] = df[col].astype(str).replace('nan', None)  # Convert to string, handle NA explicitly
#
# # Separate features and target
# X = df.drop('fraud_reported', axis=1)
# y = df['fraud_reported']
#
# # Preprocessing pipeline
# preprocessor = ColumnTransformer(
#     transformers=[
#         ('num', SimpleImputer(strategy='median'), numerical_cols),
#         ('cat', Pipeline(steps=[
#             ('imputer', SimpleImputer(strategy='most_frequent', missing_values=None)),
#             ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
#         ]), categorical_cols)
#     ])
#
# # Split data into train and test sets (80/20)
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#
# # Create full pipeline
# model_pipeline = Pipeline(steps=[
#     ('preprocessor', preprocessor),
#     ('classifier', DecisionTreeClassifier(random_state=42))
# ])
#
# # Train the model
# model_pipeline.fit(X_train, y_train)
#
# # Evaluate on test set
# y_pred = model_pipeline.predict(X_test)
# print("Accuracy:", accuracy_score(y_test, y_pred))
# print("Classification Report:\n", classification_report(y_test, y_pred))
#
# # Save the trained model
# joblib.dump(model_pipeline, 'fraud_detection_model.pkl')
# print("Model saved as 'fraud_detection_model.pkl'")








import os
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = r"C:\Users\GAYATHRI\Music\insurance\insurance claim\insurance"

DATASET_PATH = os.path.join(
    BASE_DIR,
    "static",
    "Worksheet in Case Study question 2.xlsx"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "myapp",
    "fraud_detection_model.pkl"
)


# ============================================================
# 2. LOAD DATASET
# ============================================================

print("=" * 70)
print("LOADING DATASET")
print("=" * 70)

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(
        f"Dataset not found:\n{DATASET_PATH}"
    )

df = pd.read_excel(
    DATASET_PATH,
    sheet_name="Fraud_Detection_decsion tree"
)

df.columns = df.columns.str.strip()

print("Dataset loaded successfully")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])


# ============================================================
# 3. TARGET
# ============================================================

TARGET = "fraud_reported"

if TARGET not in df.columns:
    raise ValueError(
        f"Target column '{TARGET}' not found."
    )


# ============================================================
# 4. REPLACE MISSING VALUES
# ============================================================

df = df.replace(
    [
        "?",
        "NA",
        "N/A",
        "na",
        "null",
        "NULL",
        ""
    ],
    np.nan
)


# ============================================================
# 5. TARGET CONVERSION
# ============================================================

print("\nOriginal target values:")
print(
    df[TARGET].value_counts(
        dropna=False
    )
)

df[TARGET] = (
    df[TARGET]
    .astype(str)
    .str.strip()
    .str.upper()
    .map({
        "Y": 1,
        "N": 0
    })
)

df = df.dropna(
    subset=[TARGET]
)

df[TARGET] = df[TARGET].astype(int)

print("\nTarget distribution:")
print(
    df[TARGET].value_counts()
)


# ============================================================
# 6. DATE COLUMNS
# ============================================================

DATE_COLS = [
    "policy_bind_date",
    "incident_date"
]

REFERENCE_DATE = pd.Timestamp(
    "1899-12-30"
)

print("\nConverting dates...")

for col in DATE_COLS:

    if col in df.columns:

        df[col] = pd.to_datetime(
            df[col],
            errors="coerce"
        )

        df[col] = (
            df[col] - REFERENCE_DATE
        ).dt.days

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        print(
            f"{col} converted"
        )


# ============================================================
# 7. SEPARATE FEATURES AND TARGET
# ============================================================

X = df.drop(
    columns=[TARGET]
)

y = df[TARGET]


# ============================================================
# 8. IDENTIFY COLUMNS
# ============================================================

categorical_cols = X.select_dtypes(
    include=[
        "object",
        "category",
        "string"
    ]
).columns.tolist()

numerical_cols = X.select_dtypes(
    include=[
        "int64",
        "int32",
        "int16",
        "float64",
        "float32"
    ]
).columns.tolist()


print("\n" + "=" * 70)
print("COLUMNS")
print("=" * 70)

print("\nNumerical columns:")
for col in numerical_cols:
    print(
        " -", col
    )

print("\nCategorical columns:")
for col in categorical_cols:
    print(
        " -", col
    )


# ============================================================
# 9. IMPORTANT:
#    CONVERT ALL CATEGORICAL VALUES TO STRINGS
# ============================================================

print("\nCleaning categorical columns...")

for col in categorical_cols:

    # First replace missing values
    X[col] = X[col].replace(
        [
            pd.NA,
            np.nan,
            "nan",
            "None",
            "NaN"
        ],
        np.nan
    )

    # Convert non-missing values to string
    X[col] = X[col].apply(
        lambda value:
        str(value)
        if pd.notna(value)
        else np.nan
    )


# ============================================================
# 10. CHECK FOR MIXED TYPES
# ============================================================

print("\nChecking categorical columns...")

for col in categorical_cols:

    non_null_values = X[col].dropna()

    types = (
        non_null_values
        .apply(
            lambda x: type(x).__name__
        )
        .unique()
    )

    print(
        f"{col}: {types}"
    )


# ============================================================
# 11. NUMERICAL COLUMNS
# ============================================================

for col in numerical_cols:

    X[col] = pd.to_numeric(
        X[col],
        errors="coerce"
    )


# ============================================================
# 12. TRAIN TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\n" + "=" * 70)
print("DATA SPLIT")
print("=" * 70)

print(
    "Training records:",
    len(X_train)
)

print(
    "Testing records:",
    len(X_test)
)


# ============================================================
# 13. NUMERICAL PIPELINE
# ============================================================

numerical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        )
    ]
)


# ============================================================
# 14. CATEGORICAL PIPELINE
# ============================================================

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            )
        )
    ]
)


# ============================================================
# 15. COLUMN TRANSFORMER
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            numerical_pipeline,
            numerical_cols
        ),
        (
            "cat",
            categorical_pipeline,
            categorical_cols
        )
    ],
    remainder="drop"
)


# ============================================================
# 16. DECISION TREE
# ============================================================

classifier = DecisionTreeClassifier(
    random_state=42,
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight="balanced"
)


# ============================================================
# 17. COMPLETE PIPELINE
# ============================================================

model_pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            classifier
        )
    ]
)


# ============================================================
# 18. TRAIN
# ============================================================

print("\n" + "=" * 70)
print("TRAINING MODEL")
print("=" * 70)

model_pipeline.fit(
    X_train,
    y_train
)

print(
    "\nModel training completed successfully!"
)


# ============================================================
# 19. PREDICTION
# ============================================================

y_pred = model_pipeline.predict(
    X_test
)


# ============================================================
# 20. ACCURACY
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

print("\n" + "=" * 70)
print("MODEL EVALUATION")
print("=" * 70)

print(
    f"Accuracy: {accuracy:.4f}"
)

print(
    f"Accuracy Percentage: {accuracy * 100:.2f}%"
)


# ============================================================
# 21. CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "No Fraud",
            "Fraud"
        ],
        zero_division=0
    )
)


# ============================================================
# 22. CONFUSION MATRIX
# ============================================================

print("\nConfusion Matrix:")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# 23. SAVE MODEL
# ============================================================

print("\n" + "=" * 70)
print("SAVING MODEL")
print("=" * 70)

os.makedirs(
    os.path.dirname(MODEL_PATH),
    exist_ok=True
)

joblib.dump(
    model_pipeline,
    MODEL_PATH
)

print(
    "\nModel saved successfully!"
)

print(
    "Location:"
)

print(
    MODEL_PATH
)


# ============================================================
# 24. TEST SAVED MODEL
# ============================================================

print("\n" + "=" * 70)
print("TESTING SAVED MODEL")
print("=" * 70)

try:

    loaded_model = joblib.load(
        MODEL_PATH
    )

    print(
        "Model loaded successfully!"
    )

    test_row = X_test.iloc[[0]]

    prediction = (
        loaded_model.predict(
            test_row
        )
    )

    probability = (
        loaded_model.predict_proba(
            test_row
        )
    )

    print(
        "Test prediction:",
        prediction[0]
    )

    print(
        "Test probability:",
        probability[0]
    )

except Exception as e:

    print(
        "Error loading saved model:"
    )

    print(e)


# ============================================================
# 25. COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("TRAINING COMPLETED SUCCESSFULLY")
print("=" * 70)

print(
    "\n0 = No Fraud"
)

print(
    "1 = Fraud"
)

print(
    "\nModel file:"
)

print(
    MODEL_PATH
)