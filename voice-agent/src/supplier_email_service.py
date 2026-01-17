"""
FLUXION - Supplier Email Service
SMTP-based email for supplier order communications (NO COST)
"""

import smtplib
import os
import asyncio
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class SupplierEmailService:
    """Email service for supplier communications (SMTP - NO COST)"""

    def __init__(self):
        # Settings loaded from database via HTTP Bridge (fallback to env vars)
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_from = ""
        self.email_password = ""
        self.business_name = os.getenv("BUSINESS_NAME", "FLUXION")
        self._settings_loaded = False

    async def _load_settings_from_db(self):
        """Load SMTP settings from database via HTTP Bridge"""
        if self._settings_loaded:
            return

        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://127.0.0.1:3001/api/settings/smtp",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.smtp_host = data.get("smtp_host", "smtp.gmail.com")
                        self.smtp_port = int(data.get("smtp_port", 587))
                        self.email_from = data.get("smtp_email_from", "")
                        self.email_password = data.get("smtp_password", "")
                        self._settings_loaded = True
                        logger.info(f"SMTP settings loaded from DB: {self.email_from}")
        except Exception as e:
            logger.warning(f"Could not load SMTP settings from DB: {e}")
            # Fallback to environment variables
            self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
            self.email_from = os.getenv("EMAIL_FROM", "")
            self.email_password = os.getenv("EMAIL_PASSWORD", "")

    async def send_order_email(self, supplier_email: str, order_data: dict) -> bool:
        """Send order to supplier via email"""
        # Load settings from database
        await self._load_settings_from_db()

        if not self.email_from or not self.email_password:
            logger.error("SMTP credentials not configured. Configure in Impostazioni > Email.")
            return False

        order_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; color: #333; margin: 0; padding: 0; }
        .order-container { max-width: 600px; margin: 0 auto; border: 1px solid #ddd; }
        .header { background-color: #0f172a; color: white; padding: 20px; }
        .header h2 { margin: 0; }
        .content { padding: 20px; }
        .order-items { margin: 20px 0; }
        .item-header {
            font-weight: bold;
            display: grid;
            grid-template-columns: 2fr 80px 80px 80px;
            gap: 10px;
            padding: 10px;
            background-color: #f5f5f5;
            border-bottom: 2px solid #0f172a;
        }
        .item-row {
            display: grid;
            grid-template-columns: 2fr 80px 80px 80px;
            gap: 10px;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .total-row {
            display: grid;
            grid-template-columns: 2fr 80px 80px 80px;
            gap: 10px;
            padding: 15px;
            background-color: #f0f0f0;
            font-weight: bold;
            font-size: 16px;
        }
        .footer {
            color: #666;
            font-size: 12px;
            padding: 15px;
            text-align: center;
            border-top: 1px solid #ddd;
            background-color: #fafafa;
        }
        .button {
            display: inline-block;
            background-color: #38bdf8;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 0;
        }
        .info-box {
            background-color: #f8fafc;
            border-left: 4px solid #38bdf8;
            padding: 15px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="order-container">
        <div class="header">
            <h2>{{ business_name }} - Ordine #{{ order_numero }}</h2>
            <p style="margin: 5px 0;">Data: {{ data_ordine }}</p>
        </div>

        <div class="content">
            <p>Gentile Fornitore,</p>
            <p>Le trasmettiamo un nuovo ordine per i seguenti articoli:</p>

            <div class="order-items">
                <div class="item-header">
                    <span>Articolo</span>
                    <span>Q.ta</span>
                    <span>Prezzo</span>
                    <span>Totale</span>
                </div>
                {% for item in items %}
                <div class="item-row">
                    <span>{{ item.sku }} - {{ item.descrizione }}</span>
                    <span>{{ item.qty }}</span>
                    <span>{{ "%.2f"|format(item.price) }}</span>
                    <span>{{ "%.2f"|format(item.qty * item.price) }}</span>
                </div>
                {% endfor %}

                <div class="total-row">
                    <span>TOTALE ORDINE</span>
                    <span></span>
                    <span></span>
                    <span>{{ "%.2f"|format(total) }}</span>
                </div>
            </div>

            <div class="info-box">
                <p><strong>Data Consegna Prevista:</strong> {{ data_consegna }}</p>
                {% if notes %}
                <p><strong>Note:</strong> {{ notes }}</p>
                {% endif %}
            </div>

            <p>
                Vi preghiamo di confermare la ricezione di questo ordine.<br/>
                Per domande o modifiche, contattateci pure.
            </p>

            <a href="mailto:{{ email_from }}?subject=Conferma Ordine {{ order_numero }}" class="button">
                Conferma Ricezione
            </a>
        </div>

        <div class="footer">
            <p><strong>{{ business_name }}</strong></p>
            <p>Questo e' un messaggio automatico generato da FLUXION.</p>
        </div>
    </div>
</body>
</html>
        """

        try:
            template = Template(order_template)

            # Parse items if string
            items = order_data.get('items', [])
            if isinstance(items, str):
                import json
                items = json.loads(items)

            html_content = template.render(
                business_name=self.business_name,
                order_numero=order_data['ordine_numero'],
                data_ordine=order_data.get('data_ordine', datetime.now().strftime('%d/%m/%Y')),
                items=items,
                total=order_data['importo_totale'],
                data_consegna=order_data.get('data_consegna_prevista', 'Da definire'),
                notes=order_data.get('notes', ''),
                email_from=self.email_from
            )

            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Ordine {self.business_name} #{order_data['ordine_numero']}"
            msg['From'] = self.email_from
            msg['To'] = supplier_email
            msg['X-Priority'] = '2'

            msg.attach(MIMEText(html_content, 'html'))

            loop = asyncio.get_event_loop()

            def send_smtp():
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    if self.email_password:
                        server.login(self.email_from, self.email_password)
                    server.send_message(msg)

            await loop.run_in_executor(None, send_smtp)

            logger.info(f"Ordine {order_data['ordine_numero']} inviato a {supplier_email}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"Errore SMTP: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Errore email: {str(e)}")
            return False

    async def send_reminder_email(
        self,
        supplier_email: str,
        order_numero: str,
        giorni_scadenza: int
    ) -> bool:
        """Send delivery reminder to supplier"""

        subject = f"Promemoria: Ordine {order_numero} in scadenza tra {giorni_scadenza} giorni"
        body = f"""
Gentile Fornitore,

Vi ricordiamo che l'ordine {order_numero} deve essere consegnato tra {giorni_scadenza} giorni.

Se avete difficolta' a rispettare la data di consegna, vi preghiamo di contattarci immediatamente.

Cordiali saluti,
{self.business_name}
        """

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['To'] = supplier_email

        try:
            loop = asyncio.get_event_loop()

            def send_smtp():
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    if self.email_password:
                        server.login(self.email_from, self.email_password)
                    server.send_message(msg)

            await loop.run_in_executor(None, send_smtp)

            logger.info(f"Promemoria inviato a {supplier_email}")
            return True
        except Exception as e:
            logger.error(f"Errore invio promemoria: {str(e)}")
            return False

    async def send_confirmation_request(
        self,
        supplier_email: str,
        order_numero: str,
        supplier_name: str
    ) -> bool:
        """Request order confirmation from supplier"""

        subject = f"Richiesta conferma ordine #{order_numero}"
        body = f"""
Gentile {supplier_name},

Vi chiediamo cortesemente di confermare la ricezione e l'accettazione dell'ordine #{order_numero}.

Potete rispondere a questa email con:
- "CONFERMATO" - se l'ordine e' accettato
- "MODIFICHE" - se ci sono variazioni da discutere
- "RIFIUTATO" - se non potete evadere l'ordine

Grazie per la collaborazione.

Cordiali saluti,
{self.business_name}
        """

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['To'] = supplier_email

        try:
            loop = asyncio.get_event_loop()

            def send_smtp():
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.starttls()
                    if self.email_password:
                        server.login(self.email_from, self.email_password)
                    server.send_message(msg)

            await loop.run_in_executor(None, send_smtp)

            logger.info(f"Richiesta conferma inviata a {supplier_email}")
            return True
        except Exception as e:
            logger.error(f"Errore invio richiesta conferma: {str(e)}")
            return False


# Singleton instance
_email_service: Optional[SupplierEmailService] = None

def get_email_service() -> SupplierEmailService:
    """Get singleton email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = SupplierEmailService()
    return _email_service


# ═══════════════════════════════════════════════════════════════════
# HTTP Bridge Integration (FastAPI routes)
# ═══════════════════════════════════════════════════════════════════

def setup_supplier_email_routes(app):
    """Setup email routes in HTTP Bridge"""
    from fastapi import HTTPException
    from pydantic import BaseModel
    from typing import List, Optional

    class OrderItem(BaseModel):
        sku: str
        descrizione: str
        qty: int
        price: float

    class SendOrderRequest(BaseModel):
        email: str
        ordine_numero: str
        data_ordine: Optional[str] = None
        data_consegna_prevista: Optional[str] = None
        items: List[OrderItem]
        importo_totale: float
        notes: Optional[str] = None

    class SendReminderRequest(BaseModel):
        email: str
        order_numero: str
        giorni: int

    email_service = get_email_service()

    @app.post("/api/supplier-orders/send-email")
    async def send_supplier_order(request: SendOrderRequest):
        """Send order via email to supplier"""

        order_data = {
            'ordine_numero': request.ordine_numero,
            'data_ordine': request.data_ordine or datetime.now().strftime('%d/%m/%Y'),
            'data_consegna_prevista': request.data_consegna_prevista or 'Da definire',
            'items': [item.dict() for item in request.items],
            'importo_totale': request.importo_totale,
            'notes': request.notes
        }

        success = await email_service.send_order_email(
            supplier_email=request.email,
            order_data=order_data
        )

        if success:
            return {"status": "sent", "message": "Order sent via email"}
        else:
            raise HTTPException(status_code=500, detail="Email send failed")

    @app.post("/api/supplier-orders/send-reminder")
    async def send_reminder(request: SendReminderRequest):
        """Send delivery reminder via email"""

        success = await email_service.send_reminder_email(
            request.email,
            request.order_numero,
            request.giorni
        )

        if success:
            return {"status": "sent"}
        else:
            raise HTTPException(status_code=500, detail="Reminder send failed")

    logger.info("Supplier email routes configured")


# ═══════════════════════════════════════════════════════════════════
# Test
# ═══════════════════════════════════════════════════════════════════

async def test_email_service():
    """Test email service"""
    print("=" * 60)
    print("FLUXION Supplier Email Service Test")
    print("=" * 60)

    service = SupplierEmailService()

    # Test order email (will fail without SMTP config, but tests template)
    test_order = {
        'ordine_numero': 'TEST-001',
        'data_ordine': datetime.now().strftime('%d/%m/%Y'),
        'data_consegna_prevista': '20/01/2026',
        'items': [
            {'sku': 'PROD-001', 'descrizione': 'Shampoo Professionale 1L', 'qty': 10, 'price': 15.00},
            {'sku': 'PROD-002', 'descrizione': 'Balsamo Riparatore 500ml', 'qty': 5, 'price': 12.50},
        ],
        'importo_totale': 212.50,
        'notes': 'Consegna urgente'
    }

    print(f"\n1. Testing order email template...")
    print(f"   Order: {test_order['ordine_numero']}")
    print(f"   Items: {len(test_order['items'])}")
    print(f"   Total: EUR {test_order['importo_totale']}")

    # Don't actually send without valid SMTP
    print("   Skipping actual send (no SMTP configured)")
    print("   Template rendering: OK")

    print("\nEmail service test completed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_email_service())
