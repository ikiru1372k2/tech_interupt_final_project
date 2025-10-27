# 🚀 Quick Launch Guide

This guide will help you quickly set up and run the AI-Powered Effort Expense Management System.

## 📋 Prerequisites

Before running the launcher, make sure you have:
- **Python 3.8 or higher** installed
- **Git** (optional, for cloning the repository)
- **Windows/Linux/Mac** operating system

---

## 🖥️ For Windows Users

### Option 1: Use the Launcher (Recommended)

Simply double-click the `launch.bat` file, or run it from the command prompt:

```cmd
launch.bat
```

### Option 2: Manual Setup

If you prefer to set up manually:

```cmd
REM Create virtual environment
python -m venv venv

REM Activate virtual environment
venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Run the application
streamlit run streamlit_app.py
```

---

## 🐧 For Linux/Mac Users

### Option 1: Use the Launcher (Recommended)

Make the script executable and run it:

```bash
chmod +x launch.sh
./launch.sh
```

### Option 2: Manual Setup

If you prefer to set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

---

## 🎯 What the Launcher Does

The launcher script automatically:

1. ✅ **Checks Python Installation** - Verifies Python 3.8+ is installed
2. ✅ **Creates Virtual Environment** - Sets up an isolated Python environment
3. ✅ **Installs Dependencies** - Downloads and installs all required packages
4. ✅ **Configures Environment** - Sets up .env file from template
5. ✅ **Validates Application Files** - Ensures all required files are present
6. ✅ **Launches Application** - Starts the Streamlit web application

---

## 🌐 Accessing the Application

Once the launcher finishes, the application will be available at:

**URL:** http://localhost:8501

The application should automatically open in your default web browser.

---

## ⚙️ Configuration (Optional)

The application works without any configuration! However, if you want to use notifications:

1. Edit the `.env` file in the project directory
2. Add your Microsoft 365 credentials (optional):
   ```env
   TENANT_ID=your_tenant_id_here
   CLIENT_ID=your_client_id_here
   CLIENT_SECRET=your_client_secret_here
   ```

See the [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed Microsoft 365 setup instructions.

---

## 📊 First Steps After Launching

1. **Upload Data** - Go to the "Upload & Train" tab
2. **Train Model** - Upload your Excel/CSV file and train the model
3. **View Analysis** - Check the "Analysis" tab for insights
4. **Configure Notifications** - Set up notifications (optional)
5. **Download Reports** - Export your data and reports

---

## 🛠️ Troubleshooting

### Problem: "Python is not installed"

**Solution:**
- Download Python from https://python.org
- During installation, check "Add Python to PATH"
- Restart your terminal/command prompt

### Problem: "Port 8501 is already in use"

**Solution:**
```bash
# Find and kill the process using port 8501
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID_NUMBER> /F

# Linux/Mac:
lsof -ti:8501 | xargs kill -9
```

### Problem: "ModuleNotFoundError"

**Solution:**
- Make sure the virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Problem: Launcher fails to create virtual environment

**Solution:**
- Check if you have write permissions in the directory
- Try running as administrator (Windows) or with sudo (Linux/Mac)

---

## 🎯 Features Overview

### 🤖 Machine Learning
- **CatBoost Regression** for effort expense prediction
- Automatic missing value handling
- Categorical feature support
- Model persistence and versioning

### 📊 Data Analysis
- Interactive visualizations with Plotly
- Missing data analysis
- Over-limit detection
- Time series analysis
- Feature importance ranking

### 🔔 Notifications
- Microsoft 365 Email integration
- Microsoft Teams notifications
- n8n workflow automation
- Customizable templates

### 📈 Reporting
- Excel/CSV export
- JSON data export
- Summary reports
- Detailed analytics

---

## 🔄 Updating the Application

To update the application with the latest changes:

### Windows:
```cmd
launch.bat
```
(The launcher will detect existing installation and update dependencies)

### Linux/Mac:
```bash
./launch.sh
```

---

## 📞 Getting Help

If you encounter issues:

1. Check the [README.md](README.md) for general information
2. Review the [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
3. Check application logs in `effort_expense_system.log`
4. Create an issue in the repository

---

## 🎉 You're All Set!

The application is now ready to use. Enjoy analyzing your effort expense data with AI-powered predictions!

**Made with ❤️ for intelligent data processing**

