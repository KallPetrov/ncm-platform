import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications via email and webhooks"""
    
    def __init__(self):
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'localhost')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.smtp_use_tls = getattr(settings, 'SMTP_USE_TLS', True)
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@ncm-platform.local')
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send an email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add plain text version
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML version if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return {
                'success': True,
                'channel': 'email',
                'recipient': to_email,
                'error_message': None
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                'success': False,
                'channel': 'email',
                'recipient': to_email,
                'error_message': str(e)
            }
    
    def send_webhook(
        self,
        webhook_url: str,
        payload: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Send a webhook notification"""
        try:
            default_headers = {
                'Content-Type': 'application/json',
                'User-Agent': f'{settings.APP_NAME}/{settings.APP_VERSION}'
            }
            
            if headers:
                default_headers.update(headers)
            
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    webhook_url,
                    json=payload,
                    headers=default_headers
                )
                response.raise_for_status()
            
            logger.info(f"Webhook sent successfully to {webhook_url}")
            return {
                'success': True,
                'channel': 'webhook',
                'url': webhook_url,
                'status_code': response.status_code,
                'error_message': None
            }
            
        except Exception as e:
            logger.error(f"Failed to send webhook to {webhook_url}: {str(e)}")
            return {
                'success': False,
                'channel': 'webhook',
                'url': webhook_url,
                'status_code': None,
                'error_message': str(e)
            }
    
    def send_backup_notification(
        self,
        device_name: str,
        device_id: int,
        backup_status: str,
        error_message: Optional[str] = None,
        recipients: List[str] = None,
        webhooks: List[str] = None
    ) -> Dict[str, Any]:
        """Send backup completion notification"""
        subject = f"Backup {'Success' if backup_status == 'success' else 'Failed'} - {device_name}"
        
        body = f"""
Device: {device_name} (ID: {device_id})
Backup Status: {backup_status}
Timestamp: {datetime.now().isoformat()}
"""
        
        if error_message:
            body += f"Error: {error_message}\n"
        
        html_body = f"""
<html>
<body>
    <h2>Backup {'Success' if backup_status == 'success' else 'Failed'}</h2>
    <p><strong>Device:</strong> {device_name} (ID: {device_id})</p>
    <p><strong>Status:</strong> {backup_status}</p>
    <p><strong>Timestamp:</strong> {datetime.now().isoformat()}</p>
    {f'<p><strong>Error:</strong> {error_message}</p>' if error_message else ''}
</body>
</html>
"""
        
        results = []
        
        # Send email notifications
        if recipients:
            for recipient in recipients:
                result = self.send_email(recipient, subject, body, html_body)
                results.append(result)
        
        # Send webhook notifications
        if webhooks:
            payload = {
                'event_type': 'backup_completed',
                'device_name': device_name,
                'device_id': device_id,
                'status': backup_status,
                'timestamp': datetime.now().isoformat(),
                'error_message': error_message
            }
            for webhook_url in webhooks:
                result = self.send_webhook(webhook_url, payload)
                results.append(result)
        
        return {
            'total_notifications': len(results),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }
    
    def send_change_detection_notification(
        self,
        device_name: str,
        device_id: int,
        old_version: int,
        new_version: int,
        change_summary: str,
        recipients: List[str] = None,
        webhooks: List[str] = None
    ) -> Dict[str, Any]:
        """Send configuration change detection notification"""
        subject = f"Configuration Change Detected - {device_name}"
        
        body = f"""
Device: {device_name} (ID: {device_id})
Change detected between version {old_version} and {new_version}
Summary: {change_summary}
Timestamp: {datetime.now().isoformat()}
"""
        
        html_body = f"""
<html>
<body>
    <h2>Configuration Change Detected</h2>
    <p><strong>Device:</strong> {device_name} (ID: {device_id})</p>
    <p><strong>Version Change:</strong> {old_version} → {new_version}</p>
    <p><strong>Summary:</strong> {change_summary}</p>
    <p><strong>Timestamp:</strong> {datetime.now().isoformat()}</p>
</body>
</html>
"""
        
        results = []
        
        # Send email notifications
        if recipients:
            for recipient in recipients:
                result = self.send_email(recipient, subject, body, html_body)
                results.append(result)
        
        # Send webhook notifications
        if webhooks:
            payload = {
                'event_type': 'configuration_changed',
                'device_name': device_name,
                'device_id': device_id,
                'old_version': old_version,
                'new_version': new_version,
                'change_summary': change_summary,
                'timestamp': datetime.now().isoformat()
            }
            for webhook_url in webhooks:
                result = self.send_webhook(webhook_url, payload)
                results.append(result)
        
        return {
            'total_notifications': len(results),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }
    
    def send_device_offline_notification(
        self,
        device_name: str,
        device_id: int,
        last_seen: Optional[str] = None,
        recipients: List[str] = None,
        webhooks: List[str] = None
    ) -> Dict[str, Any]:
        """Send device offline notification"""
        subject = f"Device Offline - {device_name}"
        
        body = f"""
Device: {device_name} (ID: {device_id})
Status: Offline
Last Seen: {last_seen or 'Unknown'}
Timestamp: {datetime.now().isoformat()}
"""
        
        html_body = f"""
<html>
<body>
    <h2>Device Offline Alert</h2>
    <p><strong>Device:</strong> {device_name} (ID: {device_id})</p>
    <p><strong>Status:</strong> Offline</p>
    <p><strong>Last Seen:</strong> {last_seen or 'Unknown'}</p>
    <p><strong>Timestamp:</strong> {datetime.now().isoformat()}</p>
</body>
</html>
"""
        
        results = []
        
        # Send email notifications
        if recipients:
            for recipient in recipients:
                result = self.send_email(recipient, subject, body, html_body)
                results.append(result)
        
        # Send webhook notifications
        if webhooks:
            payload = {
                'event_type': 'device_offline',
                'device_name': device_name,
                'device_id': device_id,
                'last_seen': last_seen,
                'timestamp': datetime.now().isoformat()
            }
            for webhook_url in webhooks:
                result = self.send_webhook(webhook_url, payload)
                results.append(result)
        
        return {
            'total_notifications': len(results),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }
