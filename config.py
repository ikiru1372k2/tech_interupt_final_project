import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Microsoft 365 Graph API Configuration
    TENANT_ID = os.getenv('TENANT_ID')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    
    # n8n Configuration
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')
    
    # Business Rules Configuration
    EFFORT_EXPENSE_LIMIT = 30
    MISSING_VALUE_THRESHOLD = 0.1  # 10% threshold for missing values
    
    # File Upload Configuration
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = ['.xlsx', '.xls', '.csv']
    
    # Notification Configuration
    EMAIL_TEMPLATE = "effort_expense_notification.html"
    TEAMS_TEMPLATE = "effort_expense_teams.json"
