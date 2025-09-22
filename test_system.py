#!/usr/bin/env python3
"""
Test script for Effort Expense Management
This script tests the core functionality without requiring a full setup
"""

import pandas as pd
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from data_processor import DataProcessor

def test_data_processing():
    """Test the ML data processing functionality."""
    print("🧪 Testing ML Data Processing...")
    
    try:
        # Initialize processor with LightGBM
        processor = DataProcessor(effort_limit=30, missing_threshold=0.1, model_type='lightgbm')
        
        # Test with sample data
        print("   📁 Loading sample data...")
        df = processor.load_data('sample_data.csv')
        print(f"   ✅ Loaded {len(df)} rows successfully")
        
        # Test preprocessing
        print("   🔄 Preprocessing data...")
        df_processed = processor.preprocess_data(df)
        print(f"   ✅ Preprocessed {len(df_processed)} rows")
        
        # Test model training
        print("   🚀 Training ML model...")
        metrics = processor.train_model(df_processed, hyperparameter_tuning=False)
        print(f"   ✅ Model trained successfully")
        print(f"   - Test RMSE: {metrics['test_rmse']:.4f}")
        print(f"   - Test R²: {metrics['test_r2']:.4f}")
        
        # Test prediction
        print("   🔮 Making predictions...")
        df_predicted = processor.predict_effort_expenses(df_processed)
        print(f"   ✅ Predictions completed")
        
        # Test issue identification
        print("   🔍 Identifying issues...")
        issues = processor.identify_issues(df_predicted)
        print(f"   ✅ Found {len(issues['needs_notification'])} issues")
        
        # Test summary generation
        print("   📊 Generating summary...")
        summary = processor.generate_summary_report(df_predicted, issues)
        print(f"   ✅ Summary generated")
        
        # Test notification data preparation
        print("   📧 Preparing notification data...")
        notification_data = processor.prepare_notification_data(df_predicted, issues)
        print(f"   ✅ Prepared {len(notification_data)} notifications")
        
        # Test model saving
        print("   💾 Testing model save/load...")
        processor.save_model('test_model.pkl')
        processor2 = DataProcessor(model_type='lightgbm')
        processor2.load_model('test_model.pkl')
        print(f"   ✅ Model save/load successful")
        
        # Display results
        print("\n📈 Test Results:")
        print(f"   - Total rows: {summary['total_rows']}")
        print(f"   - Missing effort: {summary['missing_effort_count']}")
        print(f"   - Over limit: {summary['over_limit_count']}")
        print(f"   - Notifications: {summary['notification_count']}")
        print(f"   - Missing percentage: {summary['missing_percentage']:.1f}%")
        print(f"   - Over limit percentage: {summary['over_limit_percentage']:.1f}%")
        print(f"   - Model accuracy (R²): {metrics['test_r2']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n🔧 Testing Configuration...")
    
    try:
        from config import Config
        
        print(f"   - Effort limit: {Config.EFFORT_EXPENSE_LIMIT}")
        print(f"   - Missing threshold: {Config.MISSING_VALUE_THRESHOLD}")
        print(f"   - n8n webhook: {'✅ Configured' if Config.N8N_WEBHOOK_URL else '❌ Not configured'}")
        print(f"   - Microsoft 365: {'✅ Configured' if Config.TENANT_ID else '❌ Not configured'}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_imports():
    """Test that all required modules can be imported."""
    print("\n📦 Testing Imports...")
    
    modules = [
        'streamlit',
        'pandas',
        'numpy',
        'openpyxl',
        'requests',
        'msal',
        'plotly',
        'lightgbm',
        'xgboost',
        'sklearn',
        'joblib'
    ]
    
    failed_imports = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️  Missing modules: {', '.join(failed_imports)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Effort Expense Management - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Data Processing Test", test_data_processing)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\n🚀 To start the application, run:")
        print("   python main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Common solutions:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Check your .env file configuration")
        print("   - Ensure sample_data.csv exists in the project directory")

if __name__ == "__main__":
    main()
