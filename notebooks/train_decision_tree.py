import pandas as pd
import numpy as np
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    roc_auc_score
)

DATA_PATH = Path('data/final1.csv')
MODEL_PATH = Path('dt_model.pkl')


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if 'timestamp' in df.columns:
        ts = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
        df['hour_of_day'] = ts.dt.hour
        df['day_of_week'] = ts.dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df = df[ts.notna()].copy()
        df = df.drop(columns=['timestamp'])
    return df


def build_feature_lists(df: pd.DataFrame):
    target_col = 'label'

    drop_cols = []
    for col in ['flow_id', 'ip_src', 'ip_dst']:
        if col in df.columns:
            drop_cols.append(col)

    if target_col not in df.columns:
        raise KeyError(f"Missing target column '{target_col}' in dataframe.")

    feature_df = df.drop(columns=[target_col] + drop_cols, errors='ignore')

    categorical_cols = []
    for col in ['ip_proto', 'flags', 'icmp_code', 'icmp_type', 'datapath_id',
                'tp_src', 'tp_dst']:
        if col in feature_df.columns:
            categorical_cols.append(col)

    numeric_cols = [c for c in feature_df.columns if c not in categorical_cols]

    return feature_df, numeric_cols, categorical_cols


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f'Dataset not found: {DATA_PATH}')

    df = pd.read_csv(DATA_PATH)
    print('Loaded data shape:', df.shape)

    if 'label' not in df.columns:
        raise KeyError("Missing required target column: 'label'")

    print('\nOriginal label distribution:')
    print(df['label'].value_counts(dropna=False))

    df = add_time_features(df)

    X, numeric_cols, categorical_cols = build_feature_lists(df)
    y = df['label'].astype(int)

    print('\nFinal feature matrix shape:', X.shape)
    print('\nNumeric columns:')
    print(numeric_cols)
    print('\nCategorical columns:')
    print(categorical_cols)

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median'))
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_cols),
            ('cat', categorical_transformer, categorical_cols)
        ],
        remainder='drop'
    )

    # Decision Tree model
    model = DecisionTreeClassifier(
        max_depth=None,
        class_weight='balanced',
        random_state=42
    )

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model)
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print('\nFitting Decision Tree model...')
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, digits=4)
    roc = roc_auc_score(y_test, y_proba)

    print(f'\nAccuracy: {acc:.4f}')
    print(f'ROC-AUC: {roc:.4f}')
    print('\nConfusion Matrix:\n', cm)
    print('\nClassification Report:\n')
    print(report)

    joblib.dump(pipeline, MODEL_PATH)
    print(f'\nSaved Decision Tree model to: {MODEL_PATH}')


if __name__ == '__main__':
    main()
