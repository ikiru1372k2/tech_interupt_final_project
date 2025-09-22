# 🚀 Complete Setup Guide

This guide will walk you through setting up the Effort Expense Management System from scratch.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] Microsoft 365 account with admin access
- [ ] n8n instance (optional but recommended)
- [ ] Basic understanding of Excel/CSV data formats

## 🔧 Step-by-Step Setup

### Step 1: Download and Extract

1. Download the project files to your local machine
2. Extract to a folder (e.g., `C:\effort-expense-system\`)
3. Open a terminal/command prompt in the project folder

### Step 2: Python Environment Setup

**Windows:**
```cmd
# Check Python version
python --version

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip
```

**Linux/Mac:**
```bash
# Check Python version
python3 --version

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Microsoft 365 Configuration

#### 4.1 Register Application in Azure AD

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Fill in the details:
   - **Name**: Effort Expense Management System
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: Leave blank for now
5. Click **Register**

#### 4.2 Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Choose **Application permissions**
5. Add the following permissions:
   - `Mail.Send`
   - `ChannelMessage.Send`
   - `Chat.ReadWrite`
   - `User.Read`
6. Click **Add permissions**
7. Click **Grant admin consent** (requires admin privileges)

#### 4.3 Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Add description: "Effort Expense System Secret"
4. Choose expiration (recommend 24 months)
5. Click **Add**
6. **IMPORTANT**: Copy the secret value immediately (you won't see it again)

#### 4.4 Get Application Details

1. Go to **Overview** in your app registration
2. Copy the following values:
   - **Application (client) ID**
   - **Directory (tenant) ID**

### Step 5: n8n Setup (Optional but Recommended)

#### 5.1 Install n8n

**Using npm:**
```bash
npm install -g n8n
```

**Using Docker:**
```bash
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

#### 5.2 Start n8n

```bash
n8n start
```

#### 5.3 Create Webhook Workflow

1. Open n8n in your browser (usually `http://localhost:5678`)
2. Click **New workflow**
3. Add a **Webhook** node:
   - **HTTP Method**: POST
   - **Path**: `effort-expense`
   - **Response Mode**: Respond to Webhook
4. Add a **Microsoft Outlook** node:
   - **Operation**: Send Email
   - Configure with your Microsoft 365 credentials
5. Connect the nodes
6. Save the workflow
7. Copy the webhook URL

### Step 6: Environment Configuration

1. Copy the environment template:
   ```bash
   # Windows
   copy env_example.txt .env
   
   # Linux/Mac
   cp env_example.txt .env
   ```

2. Edit the `.env` file with your values:
   ```env
   # Microsoft 365 Graph API Configuration
   TENANT_ID=your_tenant_id_from_azure
   CLIENT_ID=your_client_id_from_azure
   CLIENT_SECRET=your_client_secret_from_azure
   
   # n8n Configuration
   N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/effort-expense
   
   # Optional: Override default values
   EFFORT_EXPENSE_LIMIT=30
   MISSING_VALUE_THRESHOLD=0.1
   ```

### Step 7: Test the Installation

1. **Run the application:**
   ```bash
   python main.py
   ```

2. **Open your browser** and go to `http://localhost:8501`

3. **Test with sample data:**
   - Use the provided `sample_data.csv` file
   - Upload it in the "Upload Data" tab
   - Check if data processing works correctly

### Step 8: Verify Notifications (Optional)

1. **Test email notifications:**
   - Process some data with missing/over-limit values
   - Go to the "Notifications" tab
   - Click "Test Notifications"
   - Check if emails are sent successfully

2. **Test n8n integration:**
   - Ensure n8n is running
   - Send a test notification
   - Check n8n logs for incoming webhook data

## 🔍 Troubleshooting Common Issues

### Issue 1: Python Not Found
**Error:** `'python' is not recognized as an internal or external command`

**Solution:**
- Install Python from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal/command prompt

### Issue 2: Permission Denied (Linux/Mac)
**Error:** `Permission denied` when running scripts

**Solution:**
```bash
chmod +x run.sh
./run.sh
```

### Issue 3: Microsoft 365 Authentication Failed
**Error:** `Failed to obtain access token`

**Solutions:**
- Verify your tenant ID, client ID, and client secret
- Check if the application has the required permissions
- Ensure admin consent has been granted
- Verify the application is registered in the correct Azure AD tenant

### Issue 4: n8n Webhook Not Working
**Error:** `Failed to send data to n8n webhook`

**Solutions:**
- Ensure n8n is running and accessible
- Check the webhook URL in your `.env` file
- Verify the webhook is properly configured in n8n
- Check n8n logs for errors

### Issue 5: File Upload Errors
**Error:** `Unsupported file format` or processing errors

**Solutions:**
- Ensure the file is in Excel (.xlsx, .xls) or CSV format
- Check that the file contains the required columns
- Verify the file is not corrupted
- Try with the provided `sample_data.csv` first

### Issue 6: Port Already in Use
**Error:** `Port 8501 is already in use`

**Solutions:**
- Kill the existing process using the port
- Use a different port by setting `STREAMLIT_SERVER_PORT` environment variable
- Restart your computer if needed

## 📊 Testing Your Setup

### Test 1: Basic Functionality
1. Upload `sample_data.csv`
2. Verify data is processed correctly
3. Check that missing values are identified
4. Verify over-limit values are flagged

### Test 2: Notifications
1. Process data with issues
2. Go to Notifications tab
3. Click "Test Notifications"
4. Verify notifications are generated

### Test 3: Reports
1. Go to Reports tab
2. Generate a summary report
3. Download the report
4. Verify the report contains expected data

## 🎯 Next Steps

Once your setup is complete:

1. **Customize the system** for your specific needs
2. **Train your team** on using the system
3. **Set up regular data processing** workflows
4. **Monitor the logs** for any issues
5. **Scale up** as needed

## 📞 Getting Help

If you encounter issues not covered in this guide:

1. Check the main `README.md` file
2. Review the application logs in `effort_expense_system.log`
3. Search for similar issues online
4. Contact your system administrator
5. Create an issue in the project repository

## 🔄 Updates and Maintenance

### Regular Maintenance
- Update dependencies monthly: `pip install -r requirements.txt --upgrade`
- Check Microsoft 365 app registration for expired secrets
- Monitor n8n workflows for errors
- Review and clean up log files

### Security Considerations
- Rotate Microsoft 365 client secrets regularly
- Use environment variables for sensitive data
- Keep the system updated with latest security patches
- Monitor access logs for suspicious activity

---

**🎉 Congratulations! Your Effort Expense Management System is now ready to use!**
