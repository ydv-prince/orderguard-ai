import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, precision_recall_curve, auc, confusion_matrix
import joblib
import os
import json

def load_data(filepath='data/synthetic_orders.csv'):
    df = pd.read_csv(filepath)
    # Chronological sort for splitting
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values('created_at')
    return df

def train_and_evaluate():
    print("Loading data...")
    df = load_data()
    
    # Feature engineering / selection
    target = 'is_rto'
    numeric_features = ['order_value', 'items_count', 'address_length', 'name_length', 'past_orders_from_ip']
    categorical_features = ['phone_valid', 'email_valid'] # Treating these as categorical/binary
    
    X = df[numeric_features + categorical_features]
    y = df[target]
    
    # Chronological split (80% train, 20% test)
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples.")
    print(f"Class imbalance (Train): {y_train.mean():.4f} RTO rate")
    
    # Preprocessing
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # Models to compare
    models = {
        'LogisticRegression': LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000),
        'RandomForest': RandomForestClassifier(class_weight='balanced', random_state=42, n_estimators=100)
    }
    
    best_model = None
    best_pr_auc = 0
    best_name = ""
    results = {}
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        clf = Pipeline(steps=[('preprocessor', preprocessor),
                              ('classifier', model)])
        
        clf.fit(X_train, y_train)
        
        # Predict probabilities
        y_probs = clf.predict_proba(X_test)[:, 1]
        y_pred = clf.predict(X_test)
        
        # Calculate PR-AUC
        precision, recall, _ = precision_recall_curve(y_test, y_probs)
        pr_auc = auc(recall, precision)
        
        print(f"--- {name} Results ---")
        print(f"PR-AUC: {pr_auc:.4f}")
        print(classification_report(y_test, y_pred))
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        results[name] = {
            'pr_auc': pr_auc,
            'report': classification_report(y_test, y_pred, output_dict=True)
        }
        
        if pr_auc > best_pr_auc:
            best_pr_auc = pr_auc
            best_model = clf
            best_name = name
            
    print(f"\nBest model selected: {best_name} with PR-AUC: {best_pr_auc:.4f}")
    
    # Save the best model
    os.makedirs('models', exist_ok=True)
    model_path = f'models/best_model_{best_name}.joblib'
    joblib.dump(best_model, model_path)
    
    # Save a metadata file
    metadata = {
        'model_name': best_name,
        'features': numeric_features + categorical_features,
        'pr_auc': best_pr_auc,
        'metrics': results[best_name]['report']
    }
    with open('models/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print(f"Saved model to {model_path} and metadata to models/metadata.json")

if __name__ == "__main__":
    train_and_evaluate()
