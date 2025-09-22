#!/usr/bin/env python3
"""
Diagnostic script to analyze ML prediction issues
Run this to understand why predictions might be crossing 30 hours
"""

import pandas as pd
import numpy as np
import os
from data_processor import DataProcessor

def analyze_training_data(file_path):
    """Analyze the training data for potential issues."""
    print("🔍 ANALYZING TRAINING DATA")
    print("=" * 50)
    
    try:
        # Load data
        df = pd.read_csv(file_path)
        print(f"✅ Data loaded successfully: {len(df)} rows")
        
        # Analyze effort expense column
        effort_col = 'effortExpense'
        if effort_col not in df.columns:
            print(f"❌ Column '{effort_col}' not found!")
            print(f"Available columns: {list(df.columns)}")
            return
        
        effort_data = df[effort_col].dropna()
        print(f"\n📊 EFFORT EXPENSE ANALYSIS")
        print(f"Total rows: {len(df)}")
        print(f"Rows with effort data: {len(effort_data)}")
        print(f"Missing values: {df[effort_col].isna().sum()}")
        
        if len(effort_data) > 0:
            print(f"\nEffort Expense Statistics:")
            print(f"  Mean: {effort_data.mean():.2f} hours")
            print(f"  Median: {effort_data.median():.2f} hours")
            print(f"  Std: {effort_data.std():.2f} hours")
            print(f"  Min: {effort_data.min():.2f} hours")
            print(f"  Max: {effort_data.max():.2f} hours")
            
            # Check for extreme values
            print(f"\n🚨 EXTREME VALUES CHECK:")
            print(f"  Values > 30 hours: {len(effort_data[effort_data > 30])}")
            print(f"  Values > 40 hours: {len(effort_data[effort_data > 40])}")
            print(f"  Values > 50 hours: {len(effort_data[effort_data > 50])}")
            
            if len(effort_data[effort_data > 50]) > 0:
                print(f"\n⚠️  WARNING: Found {len(effort_data[effort_data > 50])} extreme values (>50 hours)")
                print("   These might be teaching the model wrong patterns!")
                extreme_values = effort_data[effort_data > 50]
                print(f"   Extreme values: {extreme_values.tolist()}")
            
            # Check data distribution
            print(f"\n📈 DISTRIBUTION ANALYSIS:")
            ranges = [
                (0, 10, "0-10 hours"),
                (10, 20, "10-20 hours"),
                (20, 30, "20-30 hours"),
                (30, 40, "30-40 hours"),
                (40, 50, "40-50 hours"),
                (50, float('inf'), "50+ hours")
            ]
            
            for min_val, max_val, label in ranges:
                count = len(effort_data[(effort_data >= min_val) & (effort_data < max_val)])
                percentage = (count / len(effort_data)) * 100
                print(f"  {label}: {count} rows ({percentage:.1f}%)")
        
        # Check other important columns
        print(f"\n🔍 OTHER COLUMNS CHECK:")
        important_cols = ['effortTimeCosts', 'billingRate_hourlyRate', 'msg_JobTitle', 'taskType']
        for col in important_cols:
            if col in df.columns:
                missing = df[col].isna().sum()
                print(f"  {col}: {missing} missing values")
            else:
                print(f"  {col}: ❌ Column not found")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        return None

def test_model_training(df):
    """Test model training and analyze results."""
    print(f"\n🤖 TESTING MODEL TRAINING")
    print("=" * 50)
    
    try:
        # Initialize processor
        processor = DataProcessor(model_type='lightgbm')
        
        # Preprocess data
        df_processed = processor.preprocess_data(df)
        print(f"✅ Data preprocessed: {len(df_processed)} rows")
        
        # Check training data
        training_data = df_processed.dropna(subset=['effortExpense'])
        print(f"Training data available: {len(training_data)} rows")
        
        if len(training_data) < 10:
            print("❌ ERROR: Not enough training data!")
            print("   Need at least 10 rows with effort expense values")
            return None
        
        # Train model
        print("🚀 Training model...")
        metrics = processor.train_model(df_processed, hyperparameter_tuning=False)
        
        print(f"\n📈 MODEL PERFORMANCE:")
        print(f"  Train R²: {metrics['train_r2']:.4f}")
        print(f"  Test R²: {metrics['test_r2']:.4f}")
        print(f"  Train RMSE: {metrics['train_rmse']:.2f}")
        print(f"  Test RMSE: {metrics['test_rmse']:.2f}")
        
        # Check for overfitting
        r2_diff = metrics['train_r2'] - metrics['test_r2']
        if r2_diff > 0.1:
            print(f"\n⚠️  WARNING: Model may be overfitting!")
            print(f"   Train R² ({metrics['train_r2']:.4f}) >> Test R² ({metrics['test_r2']:.4f})")
            print(f"   Difference: {r2_diff:.4f}")
        
        # Feature importance
        if 'feature_importance' in metrics:
            print(f"\n🔍 TOP 10 FEATURE IMPORTANCE:")
            importance = metrics['feature_importance']
            sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            for i, (feature, imp) in enumerate(sorted_features[:10]):
                print(f"  {i+1:2d}. {feature}: {imp:.4f}")
        
        return processor, metrics
        
    except Exception as e:
        print(f"❌ Error training model: {str(e)}")
        return None, None

def test_predictions(processor, df):
    """Test predictions and analyze results."""
    print(f"\n🔮 TESTING PREDICTIONS")
    print("=" * 50)
    
    try:
        # Preprocess data
        df_processed = processor.preprocess_data(df)
        
        # Make predictions
        df_predicted = processor.predict_effort_expenses(df_processed)
        
        # Analyze predictions
        predicted_rows = df_predicted[df_predicted['needs_prediction']]
        print(f"✅ Predictions made: {len(predicted_rows)} rows")
        
        if len(predicted_rows) > 0:
            predictions = predicted_rows['effortExpense_predicted']
            
            print(f"\n📊 PREDICTION STATISTICS:")
            print(f"  Min prediction: {predictions.min():.2f} hours")
            print(f"  Max prediction: {predictions.max():.2f} hours")
            print(f"  Mean prediction: {predictions.mean():.2f} hours")
            print(f"  Median prediction: {predictions.median():.2f} hours")
            print(f"  Std prediction: {predictions.std():.2f} hours")
            
            # Check problematic predictions
            print(f"\n🚨 PROBLEMATIC PREDICTIONS:")
            high_predictions = predicted_rows[predicted_rows['effortExpense_predicted'] > 35]
            print(f"  Predictions > 35 hours: {len(high_predictions)}")
            
            if len(high_predictions) > 0:
                print(f"\n⚠️  WARNING: Found {len(high_predictions)} high predictions!")
                print("   These predictions exceed reasonable limits:")
                for idx, row in high_predictions.iterrows():
                    original = row['effortExpense']
                    predicted = row['effortExpense_predicted']
                    issue_type = "missing" if row['is_missing_effort'] else "over_limit"
                    print(f"     Row {idx}: {issue_type} - Original: {original}, Predicted: {predicted:.2f}")
            
            # Check prediction distribution
            print(f"\n📈 PREDICTION DISTRIBUTION:")
            ranges = [
                (0, 10, "0-10 hours"),
                (10, 20, "10-20 hours"),
                (20, 30, "20-30 hours"),
                (30, 40, "30-40 hours"),
                (40, float('inf'), "40+ hours")
            ]
            
            for min_val, max_val, label in ranges:
                count = len(predictions[(predictions >= min_val) & (predictions < max_val)])
                percentage = (count / len(predictions)) * 100
                print(f"  {label}: {count} predictions ({percentage:.1f}%)")
        
        return df_predicted
        
    except Exception as e:
        print(f"❌ Error making predictions: {str(e)}")
        return None

def main():
    """Main diagnostic function."""
    print("🔬 ML PREDICTION DIAGNOSTIC TOOL")
    print("=" * 60)
    print("This tool will help you understand why predictions might be crossing 30 hours")
    print()
    
    # Check for sample data
    sample_file = "sample_data.csv"
    if os.path.exists(sample_file):
        print(f"📁 Found sample data: {sample_file}")
        df = analyze_training_data(sample_file)
        
        if df is not None:
            processor, metrics = test_model_training(df)
            
            if processor is not None:
                df_predicted = test_predictions(processor, df)
                
                print(f"\n🎯 SUMMARY & RECOMMENDATIONS")
                print("=" * 50)
                
                if metrics:
                    if metrics['test_r2'] < 0.3:
                        print("❌ Model performance is poor (R² < 0.3)")
                        print("   → Collect more training data")
                        print("   → Improve feature engineering")
                        print("   → Check data quality")
                    
                    if metrics['train_r2'] - metrics['test_r2'] > 0.1:
                        print("❌ Model is overfitting")
                        print("   → Increase regularization")
                        print("   → Reduce model complexity")
                        print("   → Use more conservative parameters")
                
                if df_predicted is not None:
                    high_preds = len(df_predicted[df_predicted['effortExpense_predicted'] > 35])
                    if high_preds > 0:
                        print("❌ Predictions exceed 35 hours")
                        print("   → Check training data for extreme values")
                        print("   → Increase regularization parameters")
                        print("   → Add prediction constraints")
                        print("   → Consider removing outliers from training")
                    else:
                        print("✅ Predictions are within reasonable limits")
                
                print(f"\n📚 Next steps:")
                print("   1. Review the detailed analysis above")
                print("   2. Check ML_PREDICTION_DOCUMENTATION.md for technical details")
                print("   3. Use PREDICTION_ISSUES_RESEARCH_GUIDE.md for specific research")
                print("   4. Consider the recommendations based on your results")
    else:
        print(f"❌ Sample data file not found: {sample_file}")
        print("   Please ensure you have data to analyze")
        print("   You can use your own CSV file by modifying the script")

if __name__ == "__main__":
    main()
