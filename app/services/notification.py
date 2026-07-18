import smtplib
from email.mime.text import MIMEText
from fastapi import BackgroundTasks, WebSocket
from typing import Dict, List
from app.core.config import settings

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

manager = ConnectionManager()

async def send_internal_websocket_msg(user_id: str, message: dict):
    await manager.send_personal_message(message, user_id)

def send_critical_email_sync(to_email: str, subject: str, body: str):
    if not settings.SMTP_USER or not settings.SMTP_SERVER:
        print("[Notification System] SMTP configurations are not fully set.")
        return
    msg = MIMEText(body, 'html', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = settings.SMTP_USER
    msg['To'] = to_email
    try:
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, [to_email], msg.as_string())
    except Exception as e:
        print(f"[Notification Center Error] Email failed to send: {str(e)}")

async def dispatch_risk_notification(user_id: str, user_email: str, task_id: str, risk_summary: str, bg_tasks: BackgroundTasks):
    # WS notification
    ws_payload = {"type": "CRITICAL_RISK", "task_id": task_id, "content": f"检测到紧急红标漏洞: {risk_summary}"}
    await send_internal_websocket_msg(user_id, ws_payload)
    
    # SMTP email notification
    email_subject = f"【律盾安全警告】任务 {task_id} 触发高危合规红线提示"
    email_body = f"<h3>安全审计警报</h3>您上传的合同存在重大合规漏洞：<br/><b>{risk_summary}</b><br/>请登录系统查看多智能体决策链路留痕树。"
    bg_tasks.add_task(send_critical_email_sync, user_email, email_subject, email_body)
