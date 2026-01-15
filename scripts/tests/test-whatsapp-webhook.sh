#!/bin/bash
# FLUXION WhatsApp Webhook Integration Test

echo "Testing WhatsApp Webhook Integration..."

# n8n webhook URL (adjust if different)
WEBHOOK_URL="http://localhost:5678/webhook/whatsapp"

# Test payload
PAYLOAD=$(cat <<'EOF'
{
  "messages": [
    {
      "from": "393459876543",
      "type": "text",
      "id": "wamid.test_123",
      "timestamp": "1705342200",
      "text": {
        "body": "Ciao, quanto costa un tagliando?"
      }
    }
  ],
  "contacts": [
    {
      "profile": {
        "name": "Mario Rossi"
      },
      "wa_id": "393459876543"
    }
  ]
}
EOF
)

echo ""
echo "Sending test WhatsApp message..."
echo "Payload:"
echo "$PAYLOAD" | python3 -m json.tool 2>/dev/null || echo "$PAYLOAD"

echo ""
echo "Posting to webhook..."
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s

echo ""
echo "Test complete. Check n8n workflow for processing."
