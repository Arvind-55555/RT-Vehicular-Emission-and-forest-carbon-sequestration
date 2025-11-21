# src/model_trainer.py
import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import lightgbm as lgb
import shap
from src.config import MODEL_CONFIG
from src.utils import save_model, calculate_metrics

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.config = MODEL_CONFIG
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        
    def prepare_features(self, X, Y=None):
        """Prepare features for training with proper encoding and scaling."""
        logger.info("Preparing features for model training...")
        
        X_processed = X.copy()
        
        # Encode categorical variables
        categorical_columns = ['city_id', 'ward_id']
        for col in categorical_columns:
            if col in X_processed.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    if Y is not None:  # Training mode
                        X_processed[f'{col}_encoded'] = self.label_encoders[col].fit_transform(X_processed[col])
                    else:  # Prediction mode
                        # Handle unseen labels
                        X_processed[f'{col}_encoded'] = 0
                else:
                    try:
                        X_processed[f'{col}_encoded'] = self.label_encoders[col].transform(X_processed[col])
                    except ValueError:
                        # Handle unseen labels during prediction
                        X_processed[f'{col}_encoded'] = 0
                
                X_processed = X_processed.drop(columns=[col])
        
        # Store feature names
        self.feature_names = X_processed.columns.tolist()
        
        # Scale numerical features
        if Y is not None:  # Training mode
            X_processed = pd.DataFrame(
                self.scaler.fit_transform(X_processed),
                columns=self.feature_names,
                index=X_processed.index
            )
        else:  # Prediction mode
            X_processed = pd.DataFrame(
                self.scaler.transform(X_processed),
                columns=self.feature_names,
                index=X_processed.index
            )
        
        return X_processed
    
    def train(self, X, Y):
        """Train the multi-output LightGBM model."""
        logger.info("Starting model training...")
        
        # Prepare features
        X_processed = self.prepare_features(X, Y)
        
        # Split data
        X_train, X_test, Y_train, Y_test = train_test_split(
            X_processed, Y, 
            test_size=self.config['test_size'], 
            random_state=self.config['random_state']
        )
        
        # Initialize LightGBM with better parameters
        lgb_params = {
            'objective': 'regression',
            'metric': 'rmse',
            'num_leaves': 31,
            'learning_rate': self.config['learning_rate'],
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'random_state': self.config['random_state']
        }
        
        # Create multi-output regressor
        self.model = MultiOutputRegressor(
            lgb.LGBMRegressor(**lgb_params, n_estimators=self.config['n_estimators'])
        )
        
        # Train model with early stopping
        self.model.fit(
            X_train, Y_train,
            eval_set=[(X_test, Y_test)],
            eval_metric='rmse',
            early_stopping_rounds=self.config['early_stopping_rounds'],
            verbose=False
        )
        
        # Evaluate model
        train_metrics = self.evaluate_model(X_train, Y_train, "Training")
        test_metrics = self.evaluate_model(X_test, Y_test, "Test")
        
        # Feature importance
        self.calculate_feature_importance(X_processed.columns)
        
        logger.info("Model training completed successfully")
        return self.model, train_metrics, test_metrics
    
    def evaluate_model(self, X, Y, dataset_name):
        """Evaluate model performance."""
        Y_pred = self.model.predict(X)
        
        metrics = {}
        for i, target in enumerate(['Net_CO2', 'Net_PM25', 'Net_NOX']):
            metrics[target] = calculate_metrics(Y.iloc[:, i], Y_pred[:, i])
        
        # Overall metrics
        overall_rmse = np.sqrt(mean_squared_error(Y, Y_pred))
        overall_r2 = r2_score(Y, Y_pred)
        
        logger.info(f"{dataset_name} Metrics - RMSE: {overall_rmse:.2f}, R²: {overall_r2:.3f}")
        
        return {
            'overall_rmse': overall_rmse,
            'overall_r2': overall_r2,
            'target_metrics': metrics
        }
    
    def calculate_feature_importance(self, feature_names):
        """Calculate and log feature importance."""
        if hasattr(self.model, 'estimators_'):
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': np.mean([est.feature_importances_ for est in self.model.estimators_], axis=0)
            }).sort_values('importance', ascending=False)
            
            logger.info("Top 10 most important features:")
            for _, row in importance_df.head(10).iterrows():
                logger.info(f"  {row['feature']}: {row['importance']:.4f}")
            
            self.feature_importance = importance_df
    
    def predict(self, X):
        """Make predictions with the trained model."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X_processed = self.prepare_features(X)
        predictions = self.model.predict(X_processed)
        
        return pd.DataFrame(predictions, columns=['Net_CO2_kg', 'Net_PM25_kg', 'Net_NOX_kg'])
    
    def explain_prediction(self, X, sample_index=0):
        """Generate SHAP explanations for predictions."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X_processed = self.prepare_features(X)
        
        # Calculate SHAP values for each target
        explainers = []
        shap_values_list = []
        
        for i, estimator in enumerate(self.model.estimators_):
            explainer = shap.TreeExplainer(estimator)
            shap_values = explainer.shap_values(X_processed.iloc[sample_index:sample_index+1])
            explainers.append(explainer)
            shap_values_list.append(shap_values)
        
        return {
            'shap_values': shap_values_list,
            'expected_values': [explainer.expected_value for explainer in explainers],
            'feature_names': self.feature_names
        }

def train_lgbm_model(X, Y):
    """Main function to train the LightGBM model."""
    trainer = ModelTrainer()
    model, train_metrics, test_metrics = trainer.train(X, Y)
    
    # Save model and preprocessing objects
    save_model(trainer, 'models/trained_model.pkl')
    
    return trainer, train_metrics, test_metrics