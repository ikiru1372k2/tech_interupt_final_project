#!/usr/bin/env python3
"""
CatBoost-based ML model for effort expense prediction
"""

import pandas as pd
import numpy as np
import logging
import os
from typing import Dict, Any, List
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

class CatBoostEffortModel:
    """CatBoost model for effort expense prediction."""
    
    def __init__(self, effort_limit: float = 30.0):
        """Initialize the CatBoost model."""
        self.effort_limit = effort_limit
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.categorical_columns = []
        self.target_column = 'effortExpense'
        self.is_trained = False
        self.model_metrics = {}
        
        # CatBoost parameters optimized for fast training
        self.catboost_params = {
            'iterations': 200,  # Reduced from 1000 for faster training
            'depth': 6,  # Reduced from 10 for faster training
            'learning_rate': 0.1,  # Increased for faster convergence
            'loss_function': 'RMSE',
            'eval_metric': 'RMSE',
            'random_seed': 42,
            'verbose': False,
            'early_stopping_rounds': 20,  # Reduced for faster training
            'l2_leaf_reg': 1,  # Reduced regularization
            'bootstrap_type': 'Bernoulli',  # Simple and fast
            'thread_count': -1,  # Use all available cores
            'task_type': 'CPU'  # Explicitly use CPU
        }
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for CatBoost model training."""
        df_processed = df.copy()
        
        # Extract time-based features from effortDate
        if 'effortDate' in df_processed.columns:
            df_processed['effortDate'] = pd.to_datetime(df_processed['effortDate'])
            df_processed['year'] = df_processed['effortDate'].dt.year
            df_processed['month'] = df_processed['effortDate'].dt.month
            df_processed['day'] = df_processed['effortDate'].dt.day
            df_processed['dayofweek'] = df_processed['effortDate'].dt.dayofweek
            df_processed['weekofyear'] = df_processed['effortDate'].dt.isocalendar().week
        
        # Define categorical columns
        self.categorical_columns = [
            'msg_JobTitle', 'msg_Community', 'taskType', 
            'CountryManagerForProject', 'Email'
        ]
        
        # Define numerical columns
        numerical_columns = [
            'effortTimeCosts', 'billingRate_hourlyRate',
            'year', 'month', 'day', 'dayofweek', 'weekofyear'
        ]
        
        # Combine all feature columns
        self.feature_columns = [col for col in numerical_columns + self.categorical_columns 
                              if col in df_processed.columns]
        
        # Handle missing values in numerical features
        for col in numerical_columns:
            if col in df_processed.columns:
                df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
                df_processed[col] = df_processed[col].fillna(df_processed[col].median())
        
        # Handle missing values in categorical features
        for col in self.categorical_columns:
            if col in df_processed.columns:
                df_processed[col] = df_processed[col].fillna('Unknown')
        
        logger.info(f"Prepared {len(self.feature_columns)} features for training")
        logger.info(f"Categorical features: {[col for col in self.categorical_columns if col in df_processed.columns]}")
        
        return df_processed
    
    def train_model(self, df: pd.DataFrame, test_size: float = 0.2, 
                   hyperparameter_tuning: bool = True, fast_mode: bool = True) -> Dict[str, Any]:
        """Train the CatBoost model on the provided data."""
        logger.info("Starting CatBoost model training...")
        
        # Prepare features
        df_processed = self.prepare_features(df)
        
        # Remove rows with missing target values for training
        train_data = df_processed.dropna(subset=[self.target_column])
        
        if len(train_data) < 10:
            raise ValueError("Not enough training data. Need at least 10 rows with effort expense values.")
        
        # Prepare features and target
        X = train_data[self.feature_columns].copy()
        y = train_data[self.target_column].copy()
        
        # Add constraints to target variable to improve accuracy
        # Cap extreme values at the effort limit (30 hours max)
        y_capped = y.copy()
        y_capped = y_capped.clip(upper=self.effort_limit)  # Cap at 30 hours max
        
        # Remove outliers that might confuse the model
        Q1 = y_capped.quantile(0.25)
        Q3 = y_capped.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Keep only reasonable values
        outlier_mask = (y_capped >= lower_bound) & (y_capped <= upper_bound)
        X = X[outlier_mask]
        y_capped = y_capped[outlier_mask]
        
        logger.info(f"Training data: {len(X)} rows after outlier removal")
        logger.info(f"Target range: {y_capped.min():.2f} - {y_capped.max():.2f} hours")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_capped, test_size=test_size, random_state=42
        )
        
        # Scale numerical features (CatBoost handles categorical automatically)
        numerical_features = [col for col in self.feature_columns 
                            if col not in self.categorical_columns]
        
        if numerical_features:
            X_train_scaled = X_train.copy()
            X_test_scaled = X_test.copy()
            
            # Scale numerical features
            X_train_scaled[numerical_features] = self.scaler.fit_transform(X_train[numerical_features])
            X_test_scaled[numerical_features] = self.scaler.transform(X_test[numerical_features])
        else:
            X_train_scaled = X_train.copy()
            X_test_scaled = X_test.copy()
        
        # Hyperparameter tuning (skip if fast mode)
        if hyperparameter_tuning and not fast_mode:
            best_params = self._hyperparameter_tuning(X_train_scaled, y_train)
            self.catboost_params.update(best_params)
        elif fast_mode:
            logger.info("Fast mode enabled - skipping hyperparameter tuning for speed")
        
        # Train CatBoost model
        self.model = CatBoostRegressor(**self.catboost_params)
        
        # Get categorical feature indices for CatBoost
        cat_features = [i for i, col in enumerate(self.feature_columns) 
                       if col in self.categorical_columns]
        
        # Train the model
        self.model.fit(
            X_train_scaled, y_train,
            cat_features=cat_features,
            eval_set=(X_test_scaled, y_test),
            use_best_model=True
        )
        
        # Make predictions
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        # Calculate metrics
        self.model_metrics = {
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_importance': self._get_feature_importance()
        }
        
        self.is_trained = True
        
        logger.info(f"Model training completed!")
        logger.info(f"Test R²: {self.model_metrics['test_r2']:.4f}")
        logger.info(f"Test RMSE: {self.model_metrics['test_rmse']:.2f}")
        
        return self.model_metrics
    
    def _hyperparameter_tuning(self, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """Perform fast hyperparameter tuning using a smaller grid."""
        logger.info("Performing fast hyperparameter tuning...")
        
        # Smaller, faster parameter grid
        param_grid = {
            'iterations': [100, 200],  # Reduced options
            'depth': [4, 6],  # Reduced options
            'learning_rate': [0.05, 0.1],  # Reduced options
            'l2_leaf_reg': [1, 3],  # Reduced options
            'bootstrap_type': ['Bernoulli', 'Bayesian'],  # Simple options
            'early_stopping_rounds': [10, 20]  # Reduced options
        }
        
        model = CatBoostRegressor(**{k: v for k, v in self.catboost_params.items() 
                                   if k not in param_grid})
        
        # Get categorical feature indices
        cat_features = [i for i, col in enumerate(self.feature_columns) 
                       if col in self.categorical_columns]
        
        # Use fewer CV folds for faster tuning
        grid_search = GridSearchCV(
            model, param_grid, cv=2, scoring='neg_mean_squared_error', 
            n_jobs=-1, verbose=0
        )
        
        grid_search.fit(X_train, y_train, cat_features=cat_features)
        
        logger.info(f"Best parameters: {grid_search.best_params_}")
        return grid_search.best_params_
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the trained model."""
        if self.model is None:
            return {}
        
        importance = self.model.get_feature_importance()
        feature_names = self.feature_columns
        
        return dict(zip(feature_names, importance))
    
    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """Make predictions for missing and over-limit effort expenses."""
        logger.info("Making predictions with CatBoost model...")
        
        df_processed = self.prepare_features(df)
        
        # Identify missing and over-limit values first
        df_processed['is_missing_effort'] = df_processed[self.target_column].isna()
        df_processed['is_over_limit'] = df_processed[self.target_column] > self.effort_limit
        df_processed['needs_prediction'] = df_processed['is_missing_effort'] | df_processed['is_over_limit']
        
        # Initialize prediction columns with original values
        df_processed['effortExpense_predicted'] = df_processed[self.target_column].copy()
        df_processed['effortExpense_final'] = df_processed[self.target_column].copy()
        
        # Only predict for rows that need prediction
        if df_processed['needs_prediction'].any():
            # Get rows that need prediction
            prediction_rows = df_processed[df_processed['needs_prediction']].copy()
            
            # Prepare features for prediction
            X = prediction_rows[self.feature_columns].copy()
            
            # Handle numerical features
            numerical_features = [col for col in self.feature_columns 
                                if col not in self.categorical_columns]
            
            if numerical_features:
                # Scale numerical features
                X_scaled = X.copy()
                X_scaled[numerical_features] = self.scaler.transform(X[numerical_features])
            else:
                X_scaled = X.copy()
            
            # Make predictions
            predictions = self.model.predict(X_scaled)
            
            # Post-process predictions to ensure they NEVER exceed the effort limit
            # Cap predictions at the effort limit (30 hours max)
            predictions = np.clip(predictions, 0, self.effort_limit)
            
            # Apply predictions only to rows that need prediction
            for i, (idx, row) in enumerate(prediction_rows.iterrows()):
                predicted_value = predictions[i]
                
                if row['is_missing_effort']:
                    # For missing values, use the predicted value but NEVER exceed effort limit
                    capped_prediction = min(predicted_value, self.effort_limit)
                    df_processed.at[idx, 'effortExpense_predicted'] = capped_prediction
                    df_processed.at[idx, 'effortExpense_final'] = capped_prediction
                elif row['is_over_limit']:
                    # For over-limit values, cap at the limit (30 hours max)
                    df_processed.at[idx, 'effortExpense_predicted'] = min(predicted_value, self.effort_limit)
                    df_processed.at[idx, 'effortExpense_final'] = self.effort_limit
        
        logger.info(f"Predictions completed for {len(df_processed)} rows")
        logger.info(f"Missing values: {df_processed['is_missing_effort'].sum()}")
        logger.info(f"Over-limit values: {df_processed['is_over_limit'].sum()}")
        logger.info(f"Rows needing prediction: {df_processed['needs_prediction'].sum()}")
        
        # Debug: Show which rows were actually predicted
        predicted_rows = df_processed[df_processed['needs_prediction']]
        if len(predicted_rows) > 0:
            logger.info("Rows that were predicted:")
            for idx, row in predicted_rows.iterrows():
                original = row[self.target_column]
                predicted = row['effortExpense_predicted']
                final = row['effortExpense_final']
                issue_type = "missing" if row['is_missing_effort'] else "over_limit"
                logger.info(f"  Row {idx}: {issue_type} - Original: {original}, Predicted: {predicted:.2f}, Final: {final:.2f}")
            
            # Validate predictions NEVER exceed effort limit
            high_predictions = predicted_rows[predicted_rows['effortExpense_predicted'] > self.effort_limit]
            if len(high_predictions) > 0:
                logger.error(f"❌ ERROR: {len(high_predictions)} predictions exceed {self.effort_limit} hours - this should never happen!")
                # Force cap these predictions
                for idx in high_predictions.index:
                    df_processed.at[idx, 'effortExpense_predicted'] = self.effort_limit
                    df_processed.at[idx, 'effortExpense_final'] = self.effort_limit
                logger.info(f"✅ Fixed: Capped {len(high_predictions)} predictions to {self.effort_limit} hours")
        
        # Final validation: Ensure NO values exceed effort limit
        final_high_values = df_processed[df_processed['effortExpense_final'] > self.effort_limit]
        if len(final_high_values) > 0:
            logger.error(f"❌ CRITICAL ERROR: {len(final_high_values)} final values exceed {self.effort_limit} hours!")
            # Force cap ALL final values
            df_processed['effortExpense_final'] = df_processed['effortExpense_final'].clip(upper=self.effort_limit)
            logger.info(f"✅ EMERGENCY FIX: Capped ALL final values to {self.effort_limit} hours")
        
        return df_processed
    
    def save_model(self, filepath: str) -> None:
        """Save the trained model and scaler."""
        if self.model is None:
            raise ValueError("No trained model to save")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'categorical_columns': self.categorical_columns,
            'target_column': self.target_column,
            'effort_limit': self.effort_limit,
            'model_metrics': self.model_metrics,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load a trained model and scaler."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.categorical_columns = model_data['categorical_columns']
        self.target_column = model_data['target_column']
        self.effort_limit = model_data['effort_limit']
        self.model_metrics = model_data['model_metrics']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {filepath}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            'model_type': 'CatBoost',
            'is_trained': self.is_trained,
            'effort_limit': self.effort_limit,
            'feature_count': len(self.feature_columns),
            'categorical_features': len(self.categorical_columns),
            'metrics': self.model_metrics
        }
    
    def cross_validate(self, df: pd.DataFrame, cv_folds: int = 5) -> Dict[str, float]:
        """Perform K-fold cross-validation."""
        from sklearn.model_selection import cross_val_score
        
        df_processed = self.prepare_features(df)
        train_data = df_processed.dropna(subset=[self.target_column])
        
        X = train_data[self.feature_columns]
        y = train_data[self.target_column]
        
        # Cap target values at the effort limit (30 hours max)
        y_capped = y.clip(upper=self.effort_limit)
        
        # Scale numerical features
        numerical_features = [col for col in self.feature_columns 
                            if col not in self.categorical_columns]
        
        if numerical_features:
            X_scaled = X.copy()
            X_scaled[numerical_features] = self.scaler.fit_transform(X[numerical_features])
        else:
            X_scaled = X.copy()
        
        # Perform cross-validation
        model = CatBoostRegressor(**self.catboost_params)
        
        # Get categorical feature indices for training
        cat_features = [i for i, col in enumerate(self.feature_columns) 
                       if col in self.categorical_columns]
        
        # For cross-validation, we need to create a custom scorer that handles categorical features
        from sklearn.model_selection import KFold
        from sklearn.metrics import make_scorer
        
        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
        cv_scores = []
        
        for train_idx, val_idx in kf.split(X_scaled):
            X_train_fold, X_val_fold = X_scaled.iloc[train_idx], X_scaled.iloc[val_idx]
            y_train_fold, y_val_fold = y_capped.iloc[train_idx], y_capped.iloc[val_idx]
            
            # Train model on fold
            fold_model = CatBoostRegressor(**self.catboost_params)
            fold_model.fit(X_train_fold, y_train_fold, cat_features=cat_features, verbose=False)
            
            # Predict on validation set
            y_pred_fold = fold_model.predict(X_val_fold)
            
            # Calculate MSE
            mse = mean_squared_error(y_val_fold, y_pred_fold)
            cv_scores.append(-mse)  # Negative for consistency with cross_val_score
        
        cv_scores = np.array(cv_scores)
        
        return {
            'cv_rmse_mean': np.sqrt(-cv_scores.mean()),
            'cv_rmse_std': np.sqrt(cv_scores.std()),
            'cv_scores': np.sqrt(-cv_scores)
        }
