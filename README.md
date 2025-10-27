# AI-Powered Data Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![CatBoost](https://img.shields.io/badge/CatBoost-ML-green.svg)](https://catboost.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent data processing platform that uses machine learning to predict effort expenses, identify data quality issues, and automate notifications through Microsoft 365 and n8n workflows.

## 🚀 Quick Start

### ⚡ One-Click Launch (Recommended)

The easiest way to get started is using our automated launcher scripts:

**For Windows Users:**
```cmd
launch.bat
```

**For Linux/Mac Users:**
```bash
chmod +x launch.sh
./launch.sh
```

The launcher will automatically:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Configure environment
- ✅ Launch the application

📖 For detailed instructions, see [LAUNCH_GUIDE.md](LAUNCH_GUIDE.md)

---

### 🛠️ Manual Setup

If you prefer to set up manually:

**Prerequisites:**
- **Python 3.8+** (recommended: Python 3.9 or 3.10)
- **Git** for cloning the repository
- **Microsoft 365 Account** (optional, for notifications)

**1. Clone the Repository**

```bash
# Clone the repository
git clone https://github.com/ikiru1372k2/tech_interupt_final_project.git

# Navigate to the project directory
cd tech_interupt_final_project
```

**2. Create Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

**3. Install Dependencies**

```bash
# Install required packages
pip install -r requirements.txt
```

**4. Configure Environment (Optional)**

```bash
# Copy environment template
copy env_example.txt .env
# Linux/Mac:
cp env_example.txt .env
```

Edit the `.env` file with your configuration (optional):

```env
# Microsoft 365 Graph API Configuration (Optional - for notifications)
TENANT_ID=your_tenant_id_here
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here

# Optional: Override default values
EFFORT_EXPENSE_LIMIT=30
MISSING_VALUE_THRESHOLD=0.1
```

**Note**: You can run the application without configuring Microsoft 365. The ML prediction and data analysis features will work without any external integrations.

**5. Run the Application**

```bash
# Start the application
streamlit run streamlit_app.py
```

The application will be available at: **http://localhost:8501**

---

## 📋 Features

### 🤖 Machine Learning
- **CatBoost Regression** for effort expense prediction
- **Automatic missing value handling**
- **Categorical feature support** (no encoding required)
- **Prediction constraints** (never exceeds 30 hours)
- **Model persistence** and versioning

### 📊 Data Analysis
- **Interactive visualizations** with Plotly
- **Missing data analysis**
- **Over-limit detection**
- **Time series analysis**
- **Feature importance ranking**

### 🔔 Notifications
- **Microsoft 365 Email** integration
- **Microsoft Teams** notifications
- **n8n workflow** automation
- **Customizable templates**

### 📈 Reporting
- **Excel/CSV export**
- **JSON data export**
- **Summary reports**
- **Detailed analytics**

---

## 🛠️ Installation Guide

### Step 1: System Requirements

**Minimum Requirements:**
- **OS**: Windows 10+, macOS 10.14+, or Linux
- **RAM**: 4GB (8GB recommended)
- **Storage**: 1GB free space
- **Python**: 3.8 or higher

**Check Python Version:**
```bash
python --version
# Should show Python 3.8 or higher
```

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/ikiru1372k2/tech_interupt_final_project.git

# Navigate to project directory
cd tech_interupt_final_project

# Verify files are present
ls
# Should show: main.py, streamlit_app.py, requirements.txt, etc.
```

### Step 3: Virtual Environment Setup

**Why use virtual environment?**
- Isolates project dependencies
- Prevents conflicts with other Python projects
- Ensures reproducible builds

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows Command Prompt:
venv\Scripts\activate.bat
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Verify activation (should show venv path)
where python
# Windows: C:\path\to\project\venv\Scripts\python.exe
# Linux/Mac: /path/to/project/venv/bin/python
```

### Step 4: Install Dependencies

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

**Key Dependencies:**
- `streamlit` - Web application framework
- `catboost` - Machine learning model
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `plotly` - Interactive visualizations
- `scikit-learn` - ML utilities
- `openpyxl` - Excel file support

### Step 5: Configuration Setup

```bash
# Copy environment template
copy env_example.txt .env
# Linux/Mac:
cp env_example.txt .env

# Edit configuration file
notepad .env
# Linux/Mac:
nano .env
```

**Optional Configuration:**
```env
# Microsoft 365 (optional - for notifications)
TENANT_ID=your_tenant_id_here
CLIENT_ID=your_client_id_here
CLIENT_SECRET=your_client_secret_here

# Override default values
EFFORT_EXPENSE_LIMIT=30
MISSING_VALUE_THRESHOLD=0.1
```

**Note**: The application works without any configuration. Microsoft 365 integration is optional and only needed for sending notifications.

### Step 6: Run Application

```bash
# Start the application
streamlit run .\streamlit_app.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.100:8501
```

---

## 📊 Data Format

### Required Columns

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `effortExpense` | Numeric | Effort expense in hours (target) | 25.5 |
| `effortDate` | Date | Date of effort entry | 2025-01-15 |
| `effortTimeCosts` | Numeric | Time-related costs | 127.63 |
| `billingRate_hourlyRate` | Numeric | Hourly billing rate | 136.55 |

### Optional Columns (for better predictions)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `msg_JobTitle` | Text | Job title | "Senior Consultant" |
| `msg_Community` | Text | Team/community | "Data Analytics" |
| `taskType` | Text | Task type | "Development" |
| `Email` | Text | User email | "user@company.com" |
| `name_P` | Text | Project name | "Project Alpha" |

### Sample Data

```csv
effortDate,effortExpense,effortTimeCosts,billingRate_hourlyRate,msg_JobTitle,Email
2025-01-15,25.5,127.63,136.55,Senior Consultant,user@company.com
2025-01-16,,210.36,225.10,Principal Consultant,manager@company.com
2025-01-17,35.0,150.00,200.00,Consultant,senior@company.com
```

---

## 🔧 Configuration

### Microsoft 365 Setup

1. **Register Application in Azure AD**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to "Azure Active Directory" > "App registrations"
   - Click "New registration"
   - Fill in application details

2. **Configure API Permissions**
   - Go to "API permissions" in your app registration
   - Add Microsoft Graph permissions:
     - `Mail.Send` (Application)
     - `ChannelMessage.Send` (Application)
     - `User.Read` (Application)

3. **Create Client Secret**
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Copy the secret value

4. **Get IDs**
   - Copy "Application (client) ID"
   - Copy "Directory (tenant) ID"

### n8n Setup (Optional - Future Feature)

n8n integration is planned for future releases. Currently, the application focuses on:
- Machine learning predictions
- Data analysis and visualization
- Microsoft 365 notifications (optional)

---

## 📖 Usage Guide

### 1. Upload & Train

1. **Upload Data**
   - Go to "Upload & Train" tab
   - Upload Excel/CSV file
   - Configure effort limit (default: 30 hours)
   - Set missing value threshold (default: 10%)

2. **Train Model**
   - Click "Train New Model"
   - Wait for training to complete (10-30 seconds)
   - View model training results

3. **Load Existing Model**
   - Check "Load Existing Model"
   - Click "Load Existing Model"
   - Use previously trained model

### 2. Analysis

1. **Select Analysis Type**
   - Effort Distribution
   - Missing Data Analysis
   - Over-Limit Analysis
   - Time Series Analysis

2. **View Visualizations**
   - Interactive charts
   - Statistical summaries
   - Trend analysis

### 3. Notifications (Optional)

1. **Configure Notifications**
   - Enable/disable email notifications
   - Enable/disable Teams notifications
   - Requires Microsoft 365 configuration

2. **Send Notifications**
   - Review notification preview
   - Click "Send Notifications"
   - Monitor delivery status

**Note**: Notifications require Microsoft 365 setup. The ML prediction and analysis features work without notifications.

### 4. Reports

1. **Generate Reports**
   - Summary Report
   - Detailed Analysis
   - Raw Data Export

2. **Export Data**
   - Excel format (.xlsx)
   - CSV format (.csv)
   - JSON format (.json)

---

## 🐛 Troubleshooting

### Common Issues

**1. "No module named 'streamlit'"**
```bash
# Solution: Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

**2. "Port 8501 already in use"**
```bash
# Solution: Kill existing process
# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID_NUMBER> /F
# Linux/Mac:
lsof -ti:8501 | xargs kill -9
```

**3. "Microsoft 365 authentication fails"**
- Check tenant ID, client ID, and client secret
- Ensure application has required permissions
- Verify application is registered in Azure AD
- **Note**: This is optional - you can use the app without Microsoft 365

**4. "File upload errors"**
- Ensure file is Excel (.xlsx, .xls) or CSV format
- Check file contains required columns
- Verify file is not corrupted

**5. "Model training fails"**
- Ensure sufficient data (minimum 10 rows)
- Check data quality (missing values < 50%)
- Verify all required columns are present

**6. "Port 8501 already in use"**
- Kill existing Streamlit process
- Use different port: `streamlit run .\streamlit_app.py --server.port 8502`

### Logs

Check application logs for detailed error messages:
```bash
# View logs
tail -f effort_expense_system.log
```

---

## 📁 Project Structure

```
tech_interupt_final_project/
├── main.py                          # Main application entry point
├── streamlit_app.py                 # Streamlit web application
├── data_processor.py                # Data processing and ML logic
├── catboost_model.py                # CatBoost ML model implementation
├── model_storage.py                 # Model persistence and storage
├── microsoft_integration.py         # Microsoft 365 integration
├── n8n_integration.py              # n8n webhook integration
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── env_example.txt                 # Environment variables template
├── run.bat                         # Windows startup script
├── run.sh                          # Linux/Mac startup script
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose configuration
├── assests/                        # Static assets
│   └── image.png                   # Logo image
├── templates/                      # Notification templates
│   ├── email_template.html         # Email template
│   └── teams_template.json         # Teams template
├── catboost_info/                  # CatBoost model files
├── ML_MODEL_SELECTION_DOCUMENTATION.md  # ML model documentation
├── ML_PREDICTION_DOCUMENTATION.md       # Prediction documentation
└── README.md                       # This file
```

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push to branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open Pull Request**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- **Documentation**: Check this README and code comments
- **Issues**: Create an issue in the repository
- **Logs**: Check `effort_expense_system.log` for errors
- **Contact**: Reach out to the development team

---

## 🚀 Deployment

### Docker Deployment

```bash
# Build Docker image
docker build -t ai-data-platform .

# Run container
docker run -p 8501:8501 ai-data-platform
```

### Production Deployment

1. **Set up production environment**
2. **Configure environment variables**
3. **Set up reverse proxy (nginx)**
4. **Configure SSL certificates**
5. **Set up monitoring and logging**

---

## 📈 Roadmap

- [ ] **Database Integration** - PostgreSQL/MongoDB support
- [ ] **Real-time Processing** - Live data updates
- [ ] **Advanced ML Models** - Ensemble methods
- [ ] **API Endpoints** - REST API for external integration
- [ ] **Multi-language Support** - Internationalization
- [ ] **Advanced Analytics** - Statistical analysis tools
- [ ] **Cloud Deployment** - AWS/Azure/GCP support
- [ ] **Mobile App** - React Native mobile application

---

**Made with ❤️ for intelligent data processing**

---

## 🔗 Links

- **Repository**: https://github.com/ikiru1372k2/tech_interupt_final_project.git
- **Documentation**: [ML Model Selection](ML_MODEL_SELECTION_DOCUMENTATION.md)
- **Issues**: [Report Bug](https://github.com/ikiru1372k2/tech_interupt_final_project/issues)
- **Discussions**: [Community](https://github.com/ikiru1372k2/tech_interupt_final_project/discussions)

---

**⭐ Star this repository if you find it helpful!**