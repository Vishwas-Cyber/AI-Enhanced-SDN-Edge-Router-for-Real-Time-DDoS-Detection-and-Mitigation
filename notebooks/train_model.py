import json
import joblib
import pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

DATA_PATH = Path('data/final1.csv')
MODEL_PATH = Path('model.pkl')
RESULTS_DIR = Path('results')
RESULTS_DIR.mkdir(exist_ok=True)


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
    drop_cols = [c for c in ['flow_id', 'ip_src', 'ip_dst'] if c in df.columns]

    if target_col not in df.columns:
        raise KeyError("Missing target column 'label'")

    feature_df = df.drop(columns=[target_col] + drop_cols, errors='ignore')

    categorical_cols = [
        c for c in ['ip_proto', 'flags', 'icmp_code', 'icmp_type',
                    'datapath_id', 'tp_src', 'tp_dst']
        if c in feature_df.columns
    ]
    numeric_cols = [c for c in feature_df.columns if c not in categorical_cols]
    return feature_df, numeric_cols, categorical_cols


def make_preprocessor(numeric_cols, categorical_cols):
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median'))
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    return ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_cols),
            ('cat', categorical_transformer, categorical_cols)
        ],
        remainder='drop'
    )


def evaluate_model(name, pipeline, X_train, X_test, y_train, y_test):
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    if hasattr(pipeline, 'predict_proba'):
        y_proba = pipeline.predict_proba(X_test)[:, 1]
    else:
        y_proba = None

    result = {
        'model': name,
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1_score': f1_score(y_test, y_pred, zero_division=0),
        'roc_auc': roc_auc_score(y_test, y_proba) if y_proba is not None else None,
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'classification_report': classification_report(y_test, y_pred, digits=4, output_dict=True)
    }
    return result, pipeline


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f'Dataset not found: {DATA_PATH}')

    df = pd.read_csv(DATA_PATH)
    df = add_time_features(df)

    X, numeric_cols, categorical_cols = build_feature_lists(df)
    y = df['label'].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    preprocessor = make_preprocessor(numeric_cols, categorical_cols)

    models = {
        'logistic_regression': LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            random_state=42
        ),
        'decision_tree': DecisionTreeClassifier(
            max_depth=12,
            min_samples_leaf=5,
            class_weight='balanced',
            random_state=42
        ),
        'random_forest': RandomForestClassifier(
            n_estimators=200,
            max_depth=18,
            min_samples_leaf=5,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
    }

    results = []
    trained_pipelines = {}

    for name, model in models.items():
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', model)
        ])
        result, trained = evaluate_model(name, pipeline, X_train, X_test, y_train, y_test)
        results.append(result)
        trained_pipelines[name] = trained

    results_df = pd.DataFrame([
        {
            'model': r['model'],
            'accuracy': r['accuracy'],
            'precision': r['precision'],
            'recall': r['recall'],
            'f1_score': r['f1_score'],
            'roc_auc': r['roc_auc']
        }
        for r in results
    ]).sort_values(by=['f1_score', 'roc_auc', 'accuracy'], ascending=False)

    best_model_name = results_df.iloc[0]['model']
    best_pipeline = trained_pipelines[best_model_name]

    results_df.to_csv(RESULTS_DIR / 'model_comparison.csv', index=False)
    joblib.dump(best_pipeline, MODEL_PATH)

    full_report = {r['model']: r for r in results}
    with open(RESULTS_DIR / 'evaluation_report.json', 'w') as f:
        json.dump(full_report, f, indent=2)

    if best_model_name == 'random_forest':
        pre = best_pipeline.named_steps['preprocessor']
        rf = best_pipeline.named_steps['model']
        feature_names = pre.get_feature_names_out()
        importances = rf.feature_importances_
        fi = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)
        fi.to_csv(RESULTS_DIR / 'feature_importance.csv', index=False)

    print('\nModel comparison:')
    print(results_df.to_string(index=False))
    print(f'\nBest model: {best_model_name}')
    print(f'Saved best pipeline to: {MODEL_PATH}')
    print(f'Saved results to: {RESULTS_DIR}')


if __name__ == '__main__':
    main()
