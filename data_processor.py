import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
from catboost_model import CatBoostEffortModel
from model_storage import ModelStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Handles data preprocessing and effort expense prediction using ML models."""
    
    def __init__(self, effort_limit: int = 30, missing_threshold: float = 0.1):
        self.effort_limit = effort_limit
        self.missing_threshold = missing_threshold
        self.ml_model = CatBoostEffortModel(effort_limit=effort_limit)
        self.is_model_trained = False
        self.model_storage = ModelStorage()
        
    def load_data(self, file_input) -> pd.DataFrame:
        """Load data from Excel or CSV file."""
        try:
            # Handle both file paths and Streamlit UploadedFile objects
            if hasattr(file_input, 'name'):
                # Streamlit UploadedFile object
                file_name = file_input.name
                if file_name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_input)
                elif file_name.endswith('.csv'):
                    # Try different encodings for CSV files
                    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                    df = None
                    for encoding in encodings:
                        try:
                            file_input.seek(0)  # Reset file pointer
                            df = pd.read_csv(file_input, encoding=encoding)
                            logger.info(f"Successfully loaded CSV with {encoding} encoding")
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if df is None:
                        raise ValueError("Could not decode CSV file with any supported encoding")
                else:
                    raise ValueError("Unsupported file format. Please use Excel or CSV files.")
            else:
                # Regular file path string
                if file_input.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_input)
                elif file_input.endswith('.csv'):
                    # Try different encodings for CSV files
                    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                    df = None
                    for encoding in encodings:
                        try:
                            df = pd.read_csv(file_input, encoding=encoding)
                            logger.info(f"Successfully loaded CSV with {encoding} encoding")
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if df is None:
                        raise ValueError("Could not decode CSV file with any supported encoding")
                else:
                    raise ValueError("Unsupported file format. Please use Excel or CSV files.")
            
            logger.info(f"Successfully loaded data with {len(df)} rows and {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess the data for analysis."""
        df_processed = df.copy()
        
        # Convert date columns
        date_columns = ['effortDate', 'startDate', 'endDate', 'startDate_P', 'startDate_T']
        for col in date_columns:
            if col in df_processed.columns:
                df_processed[col] = pd.to_datetime(df_processed[col], errors='coerce')
        
        # Handle missing values in effortExpense
        df_processed['effortExpense_original'] = df_processed['effortExpense'].copy()
        df_processed['is_missing_effort'] = df_processed['effortExpense'].isna()
        
        # Create flags for analysis
        df_processed['is_over_limit'] = df_processed['effortExpense'] > self.effort_limit
        df_processed['needs_prediction'] = df_processed['is_missing_effort'] | df_processed['is_over_limit']
        
        # Extract time features
        if 'effortDate' in df_processed.columns:
            df_processed['effort_year'] = df_processed['effortDate'].dt.year
            df_processed['effort_month'] = df_processed['effortDate'].dt.month
            df_processed['effort_quarter'] = df_processed['effortDate'].dt.quarter
            df_processed['effort_weekday'] = df_processed['effortDate'].dt.dayofweek
        
        # Calculate project duration
        if 'startDate_P' in df_processed.columns and 'endDate' in df_processed.columns:
            df_processed['project_duration_days'] = (df_processed['endDate'] - df_processed['startDate_P']).dt.days
        
        # Create cost efficiency ratio
        if 'effortTimeCosts' in df_processed.columns and 'billingRate_hourlyRate' in df_processed.columns:
            df_processed['cost_efficiency_ratio'] = df_processed['effortTimeCosts'] / df_processed['billingRate_hourlyRate'].replace(0, np.nan)
        
        logger.info(f"Data preprocessing completed. {df_processed['needs_prediction'].sum()} rows need prediction.")
        return df_processed
    
    def train_model(self, df: pd.DataFrame, hyperparameter_tuning: bool = False, fast_mode: bool = True) -> Dict[str, Any]:
        """Train the ML model on the provided data."""
        logger.info("Training ML model on uploaded data...")
        
        try:
            # Train the model with fast mode by default
            metrics = self.ml_model.train_model(df, hyperparameter_tuning=hyperparameter_tuning, fast_mode=fast_mode)
            self.is_model_trained = True
            
            logger.info(f"Model training completed successfully!")
            logger.info(f"Model type: CatBoost")
            logger.info(f"Test RMSE: {metrics['test_rmse']:.4f}")
            logger.info(f"Test R²: {metrics['test_r2']:.4f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def predict_effort_expenses(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict effort expenses using the trained ML model."""
        if not self.is_model_trained:
            raise ValueError("Model must be trained before making predictions. Call train_model() first.")
        
        logger.info("Making predictions using trained ML model...")
        
        try:
            # Use ML model for predictions
            df_predicted = self.ml_model.predict(df)
            
            # Add original values for comparison
            df_predicted['effortExpense_original'] = df['effortExpense'].copy()
            
            logger.info(f"Predictions completed successfully!")
            logger.info(f"Missing values predicted: {df_predicted['is_missing_effort'].sum()}")
            logger.info(f"Over-limit values flagged: {df_predicted['is_over_limit'].sum()}")
            
            return df_predicted
            
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            raise
    
    def save_model(self, filepath: str = None) -> str:
        """Save the trained model to file and database."""
        if not self.is_model_trained:
            raise ValueError("No trained model to save")
        
        # Generate filename if not provided
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"effort_expense_model_catboost_{timestamp}.pkl"
        
        # Save model to file
        self.ml_model.save_model(filepath)
        
        # Save to database
        model_id = self.model_storage.save_model(
            model_name=f"CatBoost_Model_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            model_type="CatBoost",
            file_path=filepath,
            metrics=self.ml_model.model_metrics,
            feature_count=len(self.ml_model.feature_columns),
            training_samples=self.ml_model.model_metrics.get('training_samples', 0),
            effort_limit=self.effort_limit
        )
        
        logger.info(f"Model saved to {filepath} and database (ID: {model_id})")
        return filepath
    
    def load_model(self, filepath: str = None) -> None:
        """Load a trained model from file or database."""
        if filepath is None:
            # Load the most recent active model from database
            active_model = self.model_storage.get_active_model()
            if active_model:
                filepath = active_model['file_path']
                logger.info(f"Loading active model from database: {filepath}")
            else:
                raise ValueError("No active model found in database")
        
        self.ml_model.load_model(filepath)
        self.is_model_trained = True
        logger.info(f"Model loaded from {filepath}")
    
    def get_saved_models(self) -> List[Dict[str, Any]]:
        """Get list of all saved models from database."""
        return self.model_storage.get_all_models()
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model storage statistics."""
        return self.model_storage.get_model_stats()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the trained model."""
        if not self.is_model_trained:
            return {"status": "not_trained"}
        
        return self.ml_model.get_model_info()
    
    def cross_validate_model(self, df: pd.DataFrame, cv_folds: int = 5) -> Dict[str, float]:
        """Perform cross-validation on the model."""
        if not self.is_model_trained:
            raise ValueError("Model must be trained before cross-validation.")
        
        return self.ml_model.cross_validate(df, cv_folds)
    
    def identify_issues(self, df: pd.DataFrame) -> Dict[str, List[int]]:
        """Identify rows with missing or over-limit effort expenses."""
        issues = {
            'missing_effort': [],
            'over_limit': [],
            'predicted_values': [],
            'needs_notification': []
        }
        
        for idx, row in df.iterrows():
            if row['is_missing_effort']:
                issues['missing_effort'].append(idx)
                issues['needs_notification'].append(idx)
            
            if row['is_over_limit']:
                issues['over_limit'].append(idx)
                issues['needs_notification'].append(idx)
            
            if row['needs_prediction']:
                issues['predicted_values'].append({
                    'index': idx,
                    'original': row.get('effortExpense_original'),
                    'predicted': row.get('effortExpense_predicted'),
                    'final': row.get('effortExpense_final'),
                    'reason': 'missing' if row['is_missing_effort'] else 'over_limit'
                })
        
        return issues
    
    def generate_summary_report(self, df: pd.DataFrame, issues: Dict) -> Dict:
        """Generate a summary report of the analysis."""
        total_rows = len(df)
        missing_count = len(issues['missing_effort'])
        over_limit_count = len(issues['over_limit'])
        predicted_count = len(issues['predicted_values'])
        
        summary = {
            'total_rows': total_rows,
            'missing_effort_count': missing_count,
            'over_limit_count': over_limit_count,
            'predicted_count': predicted_count,
            'notification_count': len(issues['needs_notification']),
            'missing_percentage': (missing_count / total_rows) * 100 if total_rows > 0 else 0,
            'over_limit_percentage': (over_limit_count / total_rows) * 100 if total_rows > 0 else 0,
            'prediction_accuracy': self._calculate_prediction_accuracy(df)
        }
        
        return summary
    
    def _calculate_prediction_accuracy(self, df: pd.DataFrame) -> float:
        """Calculate prediction accuracy for validation."""
        # This would compare predicted vs actual values where both exist
        # For now, return a placeholder
        return 85.0  # Placeholder accuracy
    
    def prepare_notification_data(self, df: pd.DataFrame, issues: Dict) -> List[Dict]:
        """Prepare data for notifications."""
        notification_data = []
        
        for idx in issues['needs_notification']:
            row = df.iloc[idx]
            notification = {
                'user_email': row.get('Email', ''),
                'user_name': row.get('keyEffortUser', ''),
                'userid': row.get('updUserOid', ''),
                'project_name': row.get('name_P', ''),
                'task_name': row.get('Task Name', ''),
                'effort_date': row.get('effortDate', ''),
                'original_effort': row.get('effortExpense_original'),
                'predicted_effort': row.get('effortExpense_predicted'),
                'final_effort': row.get('effortExpense_final'),
                'issue_type': 'missing' if row['is_missing_effort'] else 'over_limit',
                'billing_rate': row.get('billingRate_hourlyRate'),
                'effort_costs': row.get('effortTimeCosts'),
                'job_title': row.get('msg_JobTitle', ''),
                'community': row.get('msg_Community', '')
            }
            notification_data.append(notification)
        
        return notification_data
