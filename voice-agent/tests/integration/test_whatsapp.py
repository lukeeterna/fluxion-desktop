"""
Integration Tests - WhatsApp API
CoVe 2026 - Voice Agent Enterprise
"""

import pytest
from unittest.mock import Mock, AsyncMock

class TestWhatsAppIntegration:
    """Test integrazione WhatsApp"""
    
    @pytest.mark.asyncio
    async def test_send_booking_confirmation(self):
        """Test invio conferma prenotazione"""
        mock_whatsapp = AsyncMock()
        mock_whatsapp.send_template_message.return_value = {
            "status": "sent",
            "message_id": "wamid.123",
            "recipient": "+39123456789"
        }
        
        template_data = {
            "template_name": "booking_confirmation",
            "language": "it",
            "parameters": {
                "service": "taglio",
                "date": "14/02/2026",
                "time": "15:00"
            }
        }
        
        result = await mock_whatsapp.send_template_message(
            to="+39123456789",
            template=template_data
        )
        
        assert result["status"] == "sent"
        assert result["message_id"].startswith("wamid")
    
    @pytest.mark.asyncio
    async def test_send_reminder(self):
        """Test invio reminder"""
        mock_whatsapp = AsyncMock()
        mock_whatsapp.send_message.return_value = {
            "status": "sent",
            "message_id": "wamid.456"
        }
        
        reminder_text = "Promemoria: hai un appuntamento domani alle 15:00"
        result = await mock_whatsapp.send_message(
            to="+39123456789",
            body=reminder_text
        )
        
        assert result["status"] == "sent"
    
    @pytest.mark.asyncio
    async def test_receive_message_webhook(self):
        """Test ricezione messaggio via webhook"""
        mock_whatsapp = Mock()
        mock_whatsapp.parse_webhook.return_value = {
            "type": "text",
            "from": "+39123456789",
            "body": "Confermo l'appuntamento",
            "timestamp": "1707830400"
        }
        
        webhook_data = {"entry": [{"changes": [{"value": {"messages": [{"from": "+39123456789"}]}}]}]}
        result = mock_whatsapp.parse_webhook(webhook_data)
        
        assert result["type"] == "text"
        assert result["from"] == "+39123456789"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
