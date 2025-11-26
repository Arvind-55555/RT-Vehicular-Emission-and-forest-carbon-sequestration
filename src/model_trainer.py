"""
This module contains the ModelTrainer class, which is responsible for training the model.
"""
import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, r2_score
import lightgbm as lgb
import shap
from typing import Dict, Any, Tuple, List
from src.config import MODEL_CONFIG
from src.utils import save_model, calculate_metrics

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    A class to train the model.
    """

    def __init__(self) -> None:
        """
        Initializes the ModelTrainer.
        """
        self.config: Dict[str, Any] = MODEL_CONFIG
        self.model: MultiOutputRegressor = None
        self.scaler: StandardScaler = StandardScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: List[str] = []

    def prepare_features(
        self, x_features: pd.DataFrame, y_features: pd.DataFrame = None
    ) -> pd.DataFrame:
        """
        Prepare features for training with proper encoding and scaling.

        Args:
            x_features (pd.DataFrame): The input features.
            y_features (pd.DataFrame, optional): The target features. Defaults to None.

        Returns:
            pd.DataFrame: The processed features.
        """
        logger.info("Preparing features for model training...")

        x_processed = x_features.copy()

        # Encode categorical variables
        categorical_columns = ["city_id", "ward_id"]
        for col in categorical_columns:
            if col in x_processed.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    if y_features is not None:  # Training mode
                        x_processed[f"{col}_encoded"] = self.label_encoders[
                            col
                        ].fit_transform(x_processed[col])
                    else:  # Prediction mode
                        # Handle unseen labels
                        x_processed[f"{col}_encoded"] = 0
                else:
                    try:
                        x_processed[f"{col}_encoded"] = self.label_encoders[
                            col
                        ].transform(x_processed[col])
                    except ValueError:
                        # Handle unseen labels during prediction
                        x_processed[f"{col}_encoded"] = 0

                x_processed = x_processed.drop(columns=[col])

        # Store feature names
        self.feature_names = x_processed.columns.tolist()

        # Scale numerical features
        if y_features is not None:  # Training mode
            x_processed = pd.DataFrame(
                self.scaler.fit_transform(x_processed),
                columns=self.feature_names,
                index=x_processed.index,
            )
        else:  # Prediction mode
            x_processed = pd.DataFrame(
                self.scaler.transform(x_processed),
                columns=self.feature_names,
                index=x_processed.index,
            )

        return x_processed

    def train(
        self, x_features: pd.DataFrame, y_features: pd.DataFrame
    ) -> Tuple[MultiOutputRegressor, Dict[str, Any], Dict[str, Any]]:
        """
        Train the multi-output LightGBM model.

        Args:
            x_features (pd.DataFrame): The input features.
            y_features (pd.DataFrame): The target features.

        Returns:
            Tuple[MultiOutputRegressor, Dict[str, Any], Dict[str, Any]]: The trained model, training metrics, and test metrics.
        """
        logger.info("Starting model training...")

        # Prepare features
        x_processed = self.prepare_features(x_features, y_features)

        # Split data
        x_train, x_test, y_train, y_test = train_test_split(
            x_processed,
            y_features,
            test_size=self.config["test_size"],
            random_state=self.config["random_state"],
        )

        # Initialize LightGBM with better parameters
        lgb_params = {
            "objective": "regression",
            "metric": "rmse",
            "num_leaves": 31,
            "learning_rate": self.config["learning_rate"],
            "feature_fraction": 0.8,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
            "random_state": self.config["random_state"],
        }

        # Create multi-output regressor
        self.model = MultiOutputRegressor(
            lgb.LGBMRegressor(**lgb_params, n_estimators=self.config["n_estimators"])
        )

        # Train model with early stopping
        self.model.fit(
            x_train,
            y_train,
            eval_set=[(x_test, y_test)],
            eval_metric="rmse",
            early_stopping_rounds=self.config["early_stopping_rounds"],
            verbose=False,
        )

        # Evaluate model
        train_metrics = self.evaluate_model(x_train, y_train, "Training")
        test_metrics = self.evaluate_model(x_test, y_test, "Test")

        # Feature importance
        self.calculate_feature_importance(x_processed.columns)

        logger.info("Model training completed successfully")
        return self.model, train_metrics, test_metrics

    def evaluate_model(
        self, x_features: pd.DataFrame, y_features: pd.DataFrame, dataset_name: str
    ) -> Dict[str, Any]:
        """
        Evaluate model performance.

        Args:
            x_features (pd.DataFrame): The input features.
            y_features (pd.DataFrame): The target features.
            dataset_name (str): The name of the dataset.

        Returns:
            Dict[str, Any]: The evaluation metrics.
        """
        y_pred = self.model.predict(x_features)

        metrics = {}
        for i, target in enumerate(["Net_CO2", "Net_PM25", "Net_NOX"]):
            metrics[target] = calculate_metrics(y_features.iloc[:, i], y_pred[:, i])

        # Overall metrics
        overall_rmse = np.sqrt(mean_squared_error(y_features, y_pred))
        overall_r2 = r2_score(y_features, y_pred)

        logger.info(
            f"{dataset_name} Metrics - RMSE: {overall_rmse:.2f}, R²: {overall_r2:.3f}"
        )

        return {
            "overall_rmse": overall_rmse,
            "overall_r2": overall_r2,
            "target_metrics": metrics,
        }

    def calculate_feature_importance(self, feature_names: List[str]) -> None:
        """
        Calculate and log feature importance.

        Args:
            feature_names (List[str]): The names of the features.
        """
        if hasattr(self.model, "estimators_"):
            importance_df = pd.DataFrame(
                {
                    "feature": feature_names,
                    "importance": np.mean(
                        [est.feature_importances_ for est in self.model.estimators_],
                        axis=0,
                    ),
                }
            ).sort_values("importance", ascending=False)

            logger.info("Top 10 most important features:")
            for _, row in importance_df.head(10).iterrows():
                logger.info(f"  {row['feature']}: {row['importance']:.4f}")

    def predict(self, x_features: pd.DataFrame) -> pd.DataFrame:
        """
        Make predictions with the trained model.

        Args:
            x_features (pd.DataFrame): The input features.

        Returns:
            pd.DataFrame: The predictions.
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        x_processed = self.prepare_features(x_features)
        predictions = self.model.predict(x_processed)

        return pd.DataFrame(
            predictions, columns=["Net_CO2_kg", "Net_PM25_kg", "Net_NOX_kg"]
        )

    def explain_prediction(self, x_features: pd.DataFrame, sample_index: int = 0) -> Dict[str, Any]:
        """
        Generate SHAP explanations for predictions.

        Args:
            x_features (pd.DataFrame): The input features.
            sample_index (int): The index of the sample to explain.

        Returns:
            Dict[str, Any]: A dictionary of SHAP values.
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        x_processed = self.prepare_features(x_features)

        # Calculate SHAP values for each target
        explainers = []
        shap_values_list = []

        for i, estimator in enumerate(self.model.estimators_):
            explainer = shap.TreeExplainer(estimator)
            shap_values = explainer.shap_values(
                x_processed.iloc[sample_index : sample_index + 1]
            )
            explainers.append(explainer)
            shap_values_list.append(shap_values)

        return {
            "shap_values": shap_values_list,
            "expected_values": [explainer.expected_value for explainer in explainers],
            "feature_names": self.feature_names,
        }


def train_lgbm_model(
    x_features: pd.DataFrame, y_features: pd.DataFrame
) -> Tuple[ModelTrainer, Dict[str, Any], Dict[str, Any]]:
    """
    Main function to train the LightGBM model.

    Args:
        x_features (pd.DataFrame): The input features.
        y_features (pd.DataFrame): The target features.

    Returns:
        Tuple[ModelTrainer, Dict[str, Any], Dict[str, Any]]: The trainer, training metrics, and test metrics.
    """
    trainer = ModelTrainer()
    model, train_metrics, test_metrics = trainer.train(x_features, y_features)

    # Save model and preprocessing objects
    save_model(trainer, "models/trained_model.pkl")

    return trainer, train_metrics, test_metrics
