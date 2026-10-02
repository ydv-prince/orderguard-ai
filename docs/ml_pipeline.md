# Machine Learning Pipeline

OrderGuard AI uses a Random Forest classifier to predict the risk of Cash-on-Delivery (COD) orders being returned to origin (RTO).

## Data & Preprocessing
- **Source**: Currently trained on synthetic e-commerce data generated via `generate_synthetic_data.py`.
- **Features**: Features like `num__address_length`, `num__name_length`, and `num__order_value` are extracted dynamically.
- **Preprocessing**: Managed via a scikit-learn `Pipeline` utilizing `StandardScaler` for numeric values.

## Model
- **Algorithm**: `RandomForestClassifier`.
- **Training**: Executed in `train_models.py` which serializes the fitted pipeline and model to `backend/model_artifacts/`.

## Explainability
The inference pipeline generates per-order feature contributions.
- We utilize the trained model's underlying structure (or tree-based methods) to derive the primary statistical correlations impacting the specific order.
- **Note**: The explanation highlights statistical correlations (e.g., "high order value relative to the norm"), which does not establish direct causation.

## Versioning & Artifacts
Models are persisted as `.joblib` files in the `model_artifacts` directory, containing both the scaler pipeline and the random forest instance. Ensure these artifacts are present before starting the backend server.
