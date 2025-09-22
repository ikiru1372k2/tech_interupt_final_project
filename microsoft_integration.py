import msal
import requests
import json
import logging
from typing import Dict, List, Optional
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MicrosoftGraphAPI:
    """Handles Microsoft 365 Graph API integration for sending emails and Teams notifications."""
    
    def __init__(self):
        self.tenant_id = Config.TENANT_ID
        self.client_id = Config.CLIENT_ID
        self.client_secret = Config.CLIENT_SECRET
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.access_token = None
        
    def get_access_token(self) -> Optional[str]:
        """Get access token for Microsoft Graph API."""
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            
            result = app.acquire_token_silent(self.scope, account=None)
            if not result:
                result = app.acquire_token_for_client(scopes=self.scope)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                logger.info("Successfully obtained access token")
                return self.access_token
            else:
                logger.error(f"Failed to obtain access token: {result.get('error_description', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error obtaining access token: {str(e)}")
            return None
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = True) -> bool:
        """Send email via Microsoft Graph API."""
        if not self.access_token:
            if not self.get_access_token():
                return False
        
        try:
            url = "https://graph.microsoft.com/v1.0/me/sendMail"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            email_data = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "HTML" if is_html else "Text",
                        "content": body
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": to_email
                            }
                        }
                    ]
                }
            }
            
            response = requests.post(url, headers=headers, json=email_data)
            
            if response.status_code == 202:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def send_teams_message(self, channel_id: str, message: str) -> bool:
        """Send message to Teams channel via Microsoft Graph API."""
        if not self.access_token:
            if not self.get_access_token():
                return False
        
        try:
            url = f"https://graph.microsoft.com/v1.0/teams/{channel_id}/channels/{channel_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            message_data = {
                "body": {
                    "contentType": "text",
                    "content": message
                }
            }
            
            response = requests.post(url, headers=headers, json=message_data)
            
            if response.status_code == 201:
                logger.info(f"Teams message sent successfully to channel {channel_id}")
                return True
            else:
                logger.error(f"Failed to send Teams message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Teams message: {str(e)}")
            return False
    
    def send_teams_webhook(self, webhook_url: str, message: Dict) -> bool:
        """Send message to Teams via webhook (alternative method)."""
        try:
            response = requests.post(webhook_url, json=message)
            
            if response.status_code == 200:
                logger.info("Teams webhook message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Teams webhook: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Teams webhook: {str(e)}")
            return False

class NotificationService:
    """Service for sending notifications about effort expense issues."""
    
    def __init__(self):
        self.graph_api = MicrosoftGraphAPI()
    
    def send_effort_expense_notifications(self, notification_data: List[Dict], 
                                        teams_webhook_url: Optional[str] = None,
                                        teams_channel_id: Optional[str] = None) -> Dict[str, int]:
        """Send notifications for effort expense issues."""
        results = {
            'emails_sent': 0,
            'emails_failed': 0,
            'teams_sent': 0,
            'teams_failed': 0
        }
        
        # Group notifications by issue type
        missing_effort = [n for n in notification_data if n['issue_type'] == 'missing']
        over_limit = [n for n in notification_data if n['issue_type'] == 'over_limit']
        
        # Send individual email notifications
        for notification in notification_data:
            if notification['user_email'] and notification['user_email'] != 'NaN':
                email_sent = self._send_individual_email(notification)
                if email_sent:
                    results['emails_sent'] += 1
                else:
                    results['emails_failed'] += 1
        
        # Send Teams summary notifications
        if teams_webhook_url or teams_channel_id:
            teams_sent = self._send_teams_summary(notification_data, teams_webhook_url, teams_channel_id)
            if teams_sent:
                results['teams_sent'] += 1
            else:
                results['teams_failed'] += 1
        
        return results
    
    def _send_individual_email(self, notification: Dict) -> bool:
        """Send individual email notification."""
        subject = f"Effort Expense Alert - {notification['issue_type'].title()}"
        
        body = self._generate_email_body(notification)
        
        return self.graph_api.send_email(
            to_email=notification['user_email'],
            subject=subject,
            body=body,
            is_html=True
        )
    
    def _send_teams_summary(self, notification_data: List[Dict], 
                           webhook_url: Optional[str] = None,
                           channel_id: Optional[str] = None) -> bool:
        """Send Teams summary notification."""
        message = self._generate_teams_message(notification_data)
        
        if webhook_url:
            return self.graph_api.send_teams_webhook(webhook_url, message)
        elif channel_id:
            return self.graph_api.send_teams_message(channel_id, message['text'])
        else:
            return False
    
    def _generate_email_body(self, notification: Dict) -> str:
        """Generate HTML email body."""
        issue_type = notification['issue_type']
        project_name = notification['project_name']
        task_name = notification['task_name']
        effort_date = notification['effort_date']
        original_effort = notification['original_effort']
        predicted_effort = notification['predicted_effort']
        final_effort = notification['final_effort']
        
        if issue_type == 'missing':
            title = "Missing Effort Expense Data"
            description = f"Your effort expense data is missing for the following entry:"
        else:
            title = "Over-Limit Effort Expense Alert"
            description = f"Your effort expense exceeds the limit ({Config.EFFORT_EXPENSE_LIMIT} hours) for the following entry:"
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; }}
                .content {{ margin: 20px 0; }}
                .details {{ background-color: #f9f9f9; padding: 15px; border-left: 4px solid #0078d4; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                .highlight {{ color: #d13438; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>{title}</h2>
            </div>
            
            <div class="content">
                <p>{description}</p>
                
                <div class="details">
                    <h3>Project Details:</h3>
                    <ul>
                        <li><strong>Project:</strong> {project_name}</li>
                        <li><strong>Task:</strong> {task_name}</li>
                        <li><strong>Date:</strong> {effort_date}</li>
                        <li><strong>Job Title:</strong> {notification.get('job_title', 'N/A')}</li>
                        <li><strong>Community:</strong> {notification.get('community', 'N/A')}</li>
                    </ul>
                    
                    <h3>Effort Expense Information:</h3>
                    <ul>
                        <li><strong>Original Value:</strong> <span class="highlight">{original_effort if original_effort is not None else 'Missing'}</span></li>
                        <li><strong>Predicted Value:</strong> {predicted_effort:.2f} hours</li>
                        <li><strong>Final Value:</strong> <span class="highlight">{final_effort:.2f} hours</span></li>
                    </ul>
                </div>
                
                <p><strong>Action Required:</strong> Please review and update your effort expense data if necessary.</p>
            </div>
            
            <div class="footer">
                <p>This is an automated notification from the Effort Expense Management System.</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _generate_teams_message(self, notification_data: List[Dict]) -> Dict:
        """Generate Teams message card."""
        missing_count = len([n for n in notification_data if n['issue_type'] == 'missing'])
        over_limit_count = len([n for n in notification_data if n['issue_type'] == 'over_limit'])
        
        message = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "0078D4",
            "summary": "Effort Expense Alert Summary",
            "sections": [{
                "activityTitle": "Effort Expense Management Alert",
                "activitySubtitle": f"Found {len(notification_data)} issues requiring attention",
                "facts": [
                    {"name": "Missing Effort Data", "value": str(missing_count)},
                    {"name": "Over-Limit Effort Data", "value": str(over_limit_count)},
                    {"name": "Total Issues", "value": str(len(notification_data))}
                ],
                "markdown": True
            }]
        }
        
        # Add individual issue details
        if notification_data:
            issue_details = "\n\n**Issues Details:**\n"
            for i, notification in enumerate(notification_data[:10], 1):  # Limit to first 10
                issue_type = notification['issue_type'].title()
                project = notification['project_name']
                user = notification['user_name']
                effort = notification['final_effort']
                issue_details += f"{i}. **{issue_type}** - {project} ({user}): {effort:.2f}h\n"
            
            if len(notification_data) > 10:
                issue_details += f"\n... and {len(notification_data) - 10} more issues"
            
            message["sections"][0]["text"] = issue_details
        
        return message
