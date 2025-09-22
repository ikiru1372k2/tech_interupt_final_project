import requests
import json
import logging
from typing import Dict, List, Optional
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class N8NWebhookClient:
    """Client for sending data to n8n webhooks."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or Config.N8N_WEBHOOK_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'EffortExpenseSystem/1.0'
        })
    
    def send_effort_expense_data(self, data: Dict) -> bool:
        """Send effort expense data to n8n webhook."""
        if not self.webhook_url:
            logger.warning("No n8n webhook URL configured")
            return False
        
        try:
            response = self.session.post(
                self.webhook_url,
                json=data,
                timeout=30
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Successfully sent data to n8n webhook: {response.status_code}")
                return True
            else:
                logger.error(f"Failed to send data to n8n webhook: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending data to n8n webhook: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending data to n8n webhook: {str(e)}")
            return False
    
    def send_notification_request(self, notification_data: List[Dict], 
                                summary: Dict, 
                                notification_type: str = "effort_expense_alert") -> bool:
        """Send notification request to n8n for processing."""
        
        payload = {
            "event_type": notification_type,
            "timestamp": self._get_current_timestamp(),
            "summary": summary,
            "notifications": notification_data,
            "metadata": {
                "system": "effort_expense_management",
                "version": "1.0",
                "processing_required": True
            }
        }
        
        return self.send_effort_expense_data(payload)
    
    def send_processing_complete(self, processing_id: str, 
                               results: Dict, 
                               success: bool = True) -> bool:
        """Send processing completion status to n8n."""
        
        payload = {
            "event_type": "processing_complete",
            "processing_id": processing_id,
            "timestamp": self._get_current_timestamp(),
            "success": success,
            "results": results,
            "metadata": {
                "system": "effort_expense_management",
                "version": "1.0"
            }
        }
        
        return self.send_effort_expense_data(payload)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

class N8NWorkflowManager:
    """Manages n8n workflow interactions."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_client = N8NWebhookClient(webhook_url)
    
    def trigger_effort_expense_workflow(self, 
                                      processed_data: Dict,
                                      issues: Dict,
                                      notification_data: List[Dict]) -> bool:
        """Trigger the complete effort expense workflow in n8n."""
        
        workflow_data = {
            "workflow_type": "effort_expense_processing",
            "data": {
                "processed_data": processed_data,
                "issues": issues,
                "notifications": notification_data
            },
            "actions": {
                "send_emails": True,
                "send_teams_notifications": True,
                "generate_reports": True,
                "update_database": False  # Set to True if you have database integration
            },
            "settings": {
                "effort_limit": Config.EFFORT_EXPENSE_LIMIT,
                "missing_threshold": Config.MISSING_VALUE_THRESHOLD,
                "notification_priority": "high"
            }
        }
        
        return self.webhook_client.send_effort_expense_data(workflow_data)
    
    def send_batch_notifications(self, 
                               batch_data: List[Dict],
                               batch_id: str) -> bool:
        """Send batch of notifications to n8n for processing."""
        
        payload = {
            "event_type": "batch_notification",
            "batch_id": batch_id,
            "timestamp": self._get_current_timestamp(),
            "batch_size": len(batch_data),
            "notifications": batch_data,
            "metadata": {
                "system": "effort_expense_management",
                "batch_processing": True
            }
        }
        
        return self.webhook_client.send_effort_expense_data(payload)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

# Example n8n workflow configuration
N8N_WORKFLOW_EXAMPLE = {
    "name": "Effort Expense Notification Workflow",
    "nodes": [
        {
            "name": "Webhook Trigger",
            "type": "n8n-nodes-base.webhook",
            "parameters": {
                "path": "effort-expense",
                "httpMethod": "POST"
            }
        },
        {
            "name": "Process Data",
            "type": "n8n-nodes-base.function",
            "parameters": {
                "functionCode": """
                // Process incoming effort expense data
                const data = $input.all()[0].json;
                
                // Filter notifications that need to be sent
                const notifications = data.notifications || [];
                const emailNotifications = notifications.filter(n => n.user_email && n.user_email !== 'NaN');
                const teamsNotifications = notifications.filter(n => n.issue_type);
                
                return {
                    emailNotifications,
                    teamsNotifications,
                    summary: data.summary
                };
                """
            }
        },
        {
            "name": "Send Emails",
            "type": "n8n-nodes-base.microsoftOutlook",
            "parameters": {
                "operation": "send",
                "toEmail": "={{ $json.emailNotifications[0].user_email }}",
                "subject": "Effort Expense Alert",
                "message": "={{ $json.emailNotifications[0].message }}"
            }
        },
        {
            "name": "Send Teams Message",
            "type": "n8n-nodes-base.microsoftTeams",
            "parameters": {
                "operation": "postMessage",
                "channelId": "your-teams-channel-id",
                "message": "={{ $json.teamsNotifications[0].message }}"
            }
        }
    ],
    "connections": {
        "Webhook Trigger": ["Process Data"],
        "Process Data": ["Send Emails", "Send Teams Message"]
    }
}

def create_n8n_workflow_config() -> Dict:
    """Create n8n workflow configuration for effort expense processing."""
    return N8N_WORKFLOW_EXAMPLE
