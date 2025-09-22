# 📊 Effort Expense Management

A comprehensive system for predicting effort expenses and automating notifications using business rules instead of ML models. This system processes Excel/CSV files, identifies missing or over-limit effort expenses, and sends automated notifications via Microsoft 365 and n8n.

## 🌟 Features

- **📁 File Upload Support**: Upload Excel (.xlsx, .xls) or CSV files
- **🔍 Data Analysis**: Comprehensive analysis of effort expense data
- **📊 Business Rules Prediction**: Predict missing effort expenses using business logic
- **🔔 Automated Notifications**: Send emails and Teams notifications
- **🔗 n8n Integration**: Seamless integration with n8n workflows
- **📈 Interactive Dashboard**: Beautiful Streamlit-based web interface
- **📋 Reporting**: Generate detailed reports and exports

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Microsoft 365 account (for notifications)
- n8n instance (optional, for advanced automation)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd validation_n8n
   ```

2. **Run the setup script**
   
   **Windows:**
   ```cmd
   run.bat
   ```
   
   **Linux/Mac:**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

3. **Manual setup (if needed)**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the application
   python main.py
   ```

### Configuration

1. **Copy environment template**
   ```bash
   copy env_example.txt .env
   ```

2. **Configure your settings in `.env`**
   ```env
   # Microsoft 365 Graph API Configuration
   TENANT_ID=your_tenant_id_here
   CLIENT_ID=your_client_id_here
   CLIENT_SECRET=your_client_secret_here
   
   # n8n Configuration
   N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/effort-expense
   
   # Optional: Override default values
   EFFORT_EXPENSE_LIMIT=30
   MISSING_VALUE_THRESHOLD=0.1
   ```

## 📖 Usage

### 1. Upload Data

1. Open the web application (usually at `http://localhost:8501`)
2. Go to the **"Upload Data"** tab
3. Upload your Excel or CSV file containing effort expense data
4. Configure the effort limit and missing value threshold in the sidebar
5. Click **"Process Data"** to analyze your data

### 2. View Analysis

1. Go to the **"Analysis"** tab
2. Select different analysis types:
   - **Effort Distribution**: View distribution of effort expenses
   - **Missing Data Analysis**: Analyze missing data patterns
   - **Over-Limit Analysis**: Identify over-limit entries
   - **Time Series Analysis**: View trends over time

### 3. Send Notifications

1. Go to the **"Notifications"** tab
2. Review the notification preview
3. Configure notification settings:
   - Enable/disable email notifications
   - Enable/disable Teams notifications
   - Set n8n webhook URL
4. Click **"Send All Notifications"** to send alerts

### 4. Generate Reports

1. Go to the **"Reports"** tab
2. Select report type:
   - **Summary Report**: High-level overview
   - **Detailed Analysis**: Comprehensive data analysis
   - **Notification Report**: Notification details
   - **Raw Data Export**: Export processed data
3. Choose export format (Excel, CSV, JSON)
4. Click **"Generate Report"** to download

## 🔧 Configuration

### Microsoft 365 Setup

1. **Register an application in Azure AD**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to "Azure Active Directory" > "App registrations"
   - Click "New registration"
   - Fill in the application details

2. **Configure API permissions**
   - Go to "API permissions" in your app registration
   - Add the following Microsoft Graph permissions:
     - `Mail.Send` (Application)
     - `ChannelMessage.Send` (Application)
     - `Chat.ReadWrite` (Application)
     - `User.Read` (Application)

3. **Create client secret**
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Copy the secret value

4. **Get tenant and client IDs**
   - Copy the "Application (client) ID" and "Directory (tenant) ID"

### n8n Setup

1. **Install n8n** (if not already installed)
   ```bash
   npm install -g n8n
   n8n start
   ```

2. **Create webhook workflow**
   - Open n8n interface (usually at `http://localhost:5678`)
   - Create a new workflow
   - Add a "Webhook" node
   - Configure the webhook URL
   - Add Microsoft 365 nodes for email/Teams integration

3. **Configure webhook URL**
   - Copy the webhook URL from n8n
   - Add it to your `.env` file

## 📊 Data Format

The system expects Excel or CSV files with the following columns:

### Required Columns
- `effortExpense`: The effort expense value (target column)
- `effortDate`: Date of the effort entry
- `effortTimeCosts`: Time-related costs
- `billingRate_hourlyRate`: Hourly billing rate

### Optional Columns (for better predictions)
- `msg_JobTitle`: Job title of the user
- `msg_Community`: Community/team information
- `taskType`: Type of task
- `CountryManagerForProject`: Project manager
- `Email`: User email for notifications
- `name_P`: Project name
- `Task Name`: Task name

### Sample Data Structure
```csv
effortDate,effortExpense,effortTimeCosts,billingRate_hourlyRate,msg_JobTitle,Email
2025-01-15,25.5,127.63,136.55,Consultant,user@company.com
2025-01-16,,210.36,225.10,Principal Consultant,manager@company.com
2025-01-17,35.0,150.00,200.00,Senior Consultant,senior@company.com
```

## 🔍 Business Rules

The system uses the following business rules for prediction:

1. **Similar Job Titles**: Use average effort from similar job titles
2. **Billing Rate Relationship**: Estimate based on cost efficiency ratio
3. **Historical Averages**: Use monthly/quarterly averages
4. **Dataset Averages**: Fallback to overall dataset average
5. **Over-Limit Capping**: Cap predictions at the configured limit

## 📁 Project Structure

```
validation_n8n/
├── main.py                 # Main application entry point
├── streamlit_app.py        # Streamlit web application
├── data_processor.py       # Data processing and prediction logic
├── microsoft_integration.py # Microsoft 365 Graph API integration
├── n8n_integration.py      # n8n webhook integration
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment variables template
├── run.bat               # Windows startup script
├── run.sh                # Linux/Mac startup script
├── templates/            # Notification templates
│   ├── email_template.html
│   └── teams_template.json
└── README.md             # This file
```

## 🛠️ Development

### Adding New Prediction Rules

1. Edit `data_processor.py`
2. Modify the `_calculate_effort_prediction` method
3. Add your custom business logic

### Customizing Notifications

1. Edit templates in the `templates/` directory
2. Modify the notification generation methods in `microsoft_integration.py`

### Adding New Analysis Types

1. Edit `streamlit_app.py`
2. Add new analysis functions
3. Update the analysis tab interface

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'streamlit'"**
   - Make sure you've activated the virtual environment
   - Run `pip install -r requirements.txt`

2. **Microsoft 365 authentication fails**
   - Check your tenant ID, client ID, and client secret
   - Ensure the application has the required permissions
   - Verify the application is registered in Azure AD

3. **n8n webhook not working**
   - Check the webhook URL in your `.env` file
   - Ensure n8n is running and accessible
   - Verify the webhook is properly configured in n8n

4. **File upload errors**
   - Ensure the file is in Excel (.xlsx, .xls) or CSV format
   - Check that the file contains the required columns
   - Verify the file is not corrupted

### Logs

Check the `effort_expense_system.log` file for detailed error messages and debugging information.

## 📞 Support

For support and questions:

1. Check the troubleshooting section above
2. Review the logs in `effort_expense_system.log`
3. Create an issue in the project repository
4. Contact your system administrator

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📈 Roadmap

- [ ] Machine learning model integration (optional)
- [ ] Database integration for data persistence
- [ ] Advanced reporting features
- [ ] Multi-language support
- [ ] API endpoints for external integration
- [ ] Real-time data processing
- [ ] Advanced notification scheduling

---

**Made with ❤️ for efficient effort expense management**
