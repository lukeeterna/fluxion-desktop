# n8n Workflows - FLUXION Additional Automations

Ready-to-import JSON workflows for FLUXION automation system.

---

## 1. Booking Reminder Workflow

**File: `n8n-workflows/auto/booking-reminder.json`**

Use case: Send SMS/WhatsApp reminder 24h before appointment

```json
{
  "name": "AUTO - Booking Reminder (24h before)",
  "description": "Sends appointment reminder to client 24 hours before scheduled time",
  "nodes": [
    {
      "parameters": {
        "interval": [
          "hours"
        ],
        "triggerAtHour": 9,
        "triggerAtMinute": 0
      },
      "id": "trigger_scheduler",
      "name": "Trigger - Every Day at 9:00 AM",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [
        250,
        300
      ]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT a.id, a.data, a.ora_inizio, c.telefono, c.nome, s.nome as servizio_nome FROM appuntamenti a JOIN clienti c ON a.cliente_id = c.id JOIN servizi s ON a.servizio_id = s.id WHERE a.data = DATE('now', '+1 day') AND a.stato = 'confermato' AND c.telefono IS NOT NULL"
      },
      "id": "query_appointments",
      "name": "Query - Get Tomorrow's Appointments",
      "type": "n8n-nodes-base.sqlite",
      "typeVersion": 1,
      "position": [
        450,
        300
      ],
      "credentials": {
        "sqlite": "fluxion_db"
      }
    },
    {
      "parameters": {
        "resource": "text",
        "textInput": "Ciao {{$node.query_appointments.json.body[0].nome}},\n\nTi ricordo che domani {{$node.query_appointments.json.body[0].data}} alle {{$node.query_appointments.json.body[0].ora_inizio}} hai un appuntamento per:\n\n{{$node.query_appointments.json.body[0].servizio_nome}}\n\nConferma o cancella qui: https://fluxion.local/appuntamenti/{{$node.query_appointments.json.body[0].id}}\n\nGrazie!"
      },
      "id": "format_message",
      "name": "Format - Message Template",
      "type": "n8n-nodes-base.set",
      "typeVersion": 1,
      "position": [
        650,
        300
      ]
    },
    {
      "parameters": {
        "resource": "message",
        "phoneNumber": "={{$node.query_appointments.json.body[0].telefono}}",
        "message": "={{$node.format_message.json.textInput}}",
        "waitForReply": false
      },
      "id": "send_whatsapp",
      "name": "Send - WhatsApp Message",
      "type": "n8n-nodes-base.whatsapp",
      "typeVersion": 1,
      "position": [
        850,
        300
      ],
      "credentials": {
        "whatsappApi": "whatsapp_business"
      }
    },
    {
      "parameters": {
        "operation": "insert",
        "table": "chat_history",
        "columns": "id,cliente_id,user_query,response,channel,timestamp",
        "columnsUi": {
          "columnValues": [
            {
              "column": "id",
              "value": "={{Date.now()}}_reminder"
            },
            {
              "column": "cliente_id",
              "value": "={{$node.query_appointments.json.body[0].cliente_id}}"
            },
            {
              "column": "user_query",
              "value": "REMINDER"
            },
            {
              "column": "response",
              "value": "={{$node.format_message.json.textInput}}"
            },
            {
              "column": "channel",
              "value": "whatsapp"
            },
            {
              "column": "timestamp",
              "value": "=CURRENT_TIMESTAMP"
            }
          ]
        }
      },
      "id": "log_reminder",
      "name": "SQLite - Log Reminder Sent",
      "type": "n8n-nodes-base.sqlite",
      "typeVersion": 1,
      "position": [
        1050,
        300
      ],
      "credentials": {
        "sqlite": "fluxion_db"
      }
    }
  ],
  "connections": {
    "trigger_scheduler": {
      "main": [
        [
          {
            "node": "query_appointments",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "query_appointments": {
      "main": [
        [
          {
            "node": "format_message",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "format_message": {
      "main": [
        [
          {
            "node": "send_whatsapp",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "send_whatsapp": {
      "main": [
        [
          {
            "node": "log_reminder",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## 2. Invoice Generator Workflow

**File: `n8n-workflows/auto/invoice-generator.json`**

Use case: Generate and send invoice after appointment completion

```json
{
  "name": "AUTO - Invoice Generator (Post-Appointment)",
  "description": "Generates PDF invoice and sends to client after appointment completion",
  "nodes": [
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT a.id, a.data, a.ora_inizio, a.ora_fine, c.id as cliente_id, c.nome, c.cognome, c.email, s.nome as servizio_nome, s.prezzo FROM appuntamenti a JOIN clienti c ON a.cliente_id = c.id JOIN servizi s ON a.servizio_id = s.id WHERE a.stato = 'completato' AND a.updated_at > DATE('now', '-1 day')"
      },
      "id": "query_completed",
      "name": "Query - Get Completed Appointments",
      "type": "n8n-nodes-base.sqlite",
      "typeVersion": 1,
      "position": [
        250,
        300
      ],
      "credentials": {
        "sqlite": "fluxion_db"
      }
    },
    {
      "parameters": {
        "resource": "text",
        "textInput": "FATTURA\n\nData: {{$node.query_completed.json.body[0].data}}\nOra: {{$node.query_completed.json.body[0].ora_inizio}}\n\nCliente: {{$node.query_completed.json.body[0].nome}} {{$node.query_completed.json.body[0].cognome}}\n\nServizio: {{$node.query_completed.json.body[0].servizio_nome}}\nPrezzo: €{{$node.query_completed.json.body[0].prezzo}}\n\nDurata: {{$node.query_completed.json.body[0].ora_inizio}} - {{$node.query_completed.json.body[0].ora_fine}}\n\nGrazie per aver scelto i nostri servizi!"
      },
      "id": "format_invoice",
      "name": "Format - Invoice Template",
      "type": "n8n-nodes-base.set",
      "typeVersion": 1,
      "position": [
        450,
        300
      ]
    },
    {
      "parameters": {
        "url": "http://127.0.0.1:3001/api/pdf/generate",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": "json",
        "sendBody": true,
        "bodyParametersJson": {
          "content": "={{$node.format_invoice.json.textInput}}",
          "filename": "invoice_{{$node.query_completed.json.body[0].cliente_id}}_{{$node.query_completed.json.body[0].data}}.pdf"
        }
      },
      "id": "generate_pdf",
      "name": "HTTP - Generate PDF",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [
        650,
        300
      ]
    },
    {
      "parameters": {
        "fromEmail": "fatture@fluxion.local",
        "toEmail": "={{$node.query_completed.json.body[0].email}}",
        "subject": "Fattura - {{$node.query_completed.json.body[0].servizio_nome}}",
        "text": "Fattura allegata per il tuo appuntamento del {{$node.query_completed.json.body[0].data}}\n\nServizio: {{$node.query_completed.json.body[0].servizio_nome}}\nImporto: €{{$node.query_completed.json.body[0].prezzo}}",
        "attachments": [
          {
            "url": "={{$node.generate_pdf.json.pdf_url}}"
          }
        ]
      },
      "id": "send_email",
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "position": [
        850,
        300
      ]
    },
    {
      "parameters": {
        "operation": "update",
        "table": "appuntamenti",
        "condition": "id = ?",
        "conditionValue": "={{$node.query_completed.json.body[0].id}}",
        "columns": "fattura_inviata,updated_at",
        "updateValues": "1,CURRENT_TIMESTAMP"
      },
      "id": "mark_invoiced",
      "name": "SQLite - Mark Invoiced",
      "type": "n8n-nodes-base.sqlite",
      "typeVersion": 1,
      "position": [
        1050,
        300
      ],
      "credentials": {
        "sqlite": "fluxion_db"
      }
    }
  ],
  "connections": {
    "query_completed": {
      "main": [
        [
          {
            "node": "format_invoice",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "format_invoice": {
      "main": [
        [
          {
            "node": "generate_pdf",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "generate_pdf": {
      "main": [
        [
          {
            "node": "send_email",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "send_email": {
      "main": [
        [
          {
            "node": "mark_invoiced",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## 3. Loyalty Points Update Workflow

**File: `n8n-workflows/bellezza/loyalty-update.json`**

Use case: Update client loyalty points after appointment

```json
{
  "name": "BELLEZZA - Loyalty Points Update",
  "description": "Increments loyalty points for client after appointment completion",
  "nodes": [
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT a.id, c.id as cliente_id, c.punti_fedelta, s.prezzo FROM appuntamenti a JOIN clienti c ON a.cliente_id = c.id JOIN servizi s ON a.servizio_id = s.id WHERE a.stato = 'completato' AND a.category = 'bellezza' AND a.punti_added IS NULL AND a.updated_at > DATE('now', '-1 day')"
      },
      "id": "query_loyalty",
      "name": "Query - Get Appointments for Loyalty",
      "type": "n8n-nodes-base.sqlite",
      "typeVersion": 1,
      "position": [
        250,
        300
      ],
      "credentials": {
        "sqlite": "fluxion_db"
      }
    },
    {
      "parameters": {
        "jsCode": "const prezzo = $input.first().json.body[0].prezzo;\nconst punti = Math.floor(prezzo / 10);\nreturn { punti: punti };",
        "resource": "jsonata"
      },
      "id": "calculate_points",
      "name": "Calculate Points (1 per €10)",
      "type": "n8n-nodes-base.code",
      "typeVersion": 1,
      "position": [
        450,
        300
      ]
    },
    {
      "parameters": {
        "operation": "update",
        "table": "clienti",
        "condition": "id = ?",
        "conditionValue": "={{$node.query_loyalty.json.body[0].cliente_id}}",
        "columns": "punti_fedelta,updated_at",
        "updateValues": "punti_fedelta + {{$node.calculate_points.json.punti}},CURRENT_TIMESTAMP"
      },
      "id": "update_points",
      "name": "SQLite - Update Loyalty Points",
      "type": "n8n-nodes-base.sqlite",
      "typeVersion": 1,
      "position": [
        650,
        300
      ],
      "credentials": {
        "sqlite": "fluxion_db"
      }
    },
    {
      "parameters": {
        "resource": "message",
        "phoneNumber": "={{$node.query_loyalty.json.body[0].telefono}}",
        "message": "Grazie! Hai accumulato {{$node.calculate_points.json.punti}} punti fedeltà. Totale: {{$node.query_loyalty.json.body[0].punti_fedelta + $node.calculate_points.json.punti}} punti"
      },
      "id": "notify_whatsapp",
      "name": "Notify - WhatsApp Points Update",
      "type": "n8n-nodes-base.whatsapp",
      "typeVersion": 1,
      "position": [
        850,
        300
      ],
      "credentials": {
        "whatsappApi": "whatsapp_business"
      }
    }
  ],
  "connections": {
    "query_loyalty": {
      "main": [
        [
          {
            "node": "calculate_points",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "calculate_points": {
      "main": [
        [
          {
            "node": "update_points",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "update_points": {
      "main": [
        [
          {
            "node": "notify_whatsapp",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## 4. Review Request Workflow

**File: `n8n-workflows/bellezza/review-request.json`**

Use case: Request review 3 days after appointment

```json
{
  "name": "BELLEZZA - Review Request (3 days post-appointment)",
  "description": "Sends review request link 3 days after appointment completion",
  "nodes": [
    {
      "parameters": {
        "interval": [
          "days"
        ]
      },
      "id": "trigger_daily",
      "name": "Trigger - Every Day",
      "type": "n8n-nodes-base.cron",
      "typeVersion": 1,
      "position": [
        250,
        300
      ]
    },
    {
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT a.id, c.id as cliente_id, c.nome, c.email, s.nome as servizio FROM appuntamenti a JOIN clienti c ON a.cliente_id = c.id JOIN servizi s ON a.servizio_id = s.id WHERE a.stato = 'completato' AND a.review_requested IS NULL AND DATE(a.updated_at) = DATE('now', '-3 days')"
      },
      "id": "query_reviews",
      "name": "Query - Get 3-day Post Appointments",
      "type": "n8n-nodes-base.sqlite",
      "typeVersion": 1,
      "position": [
        450,
        300
      ],
      "credentials": {
        "sqlite": "fluxion_db"
      }
    },
    {
      "parameters": {
        "resource": "message",
        "phoneNumber": "={{$node.query_reviews.json.body[0].telefono}}",
        "message": "Ciao {{$node.query_reviews.json.body[0].nome}}, come è andata la tua esperienza con il nostro servizio {{$node.query_reviews.json.body[0].servizio}}? Lascia una recensione: https://fluxion.local/reviews/{{$node.query_reviews.json.body[0].cliente_id}}"
      },
      "id": "send_review_request",
      "name": "Send - Review Request WhatsApp",
      "type": "n8n-nodes-base.whatsapp",
      "typeVersion": 1,
      "position": [
        650,
        300
      ],
      "credentials": {
        "whatsappApi": "whatsapp_business"
      }
    },
    {
      "parameters": {
        "operation": "update",
        "table": "appuntamenti",
        "condition": "id = ?",
        "conditionValue": "={{$node.query_reviews.json.body[0].id}}",
        "columns": "review_requested,updated_at",
        "updateValues": "1,CURRENT_TIMESTAMP"
      },
      "id": "mark_review_sent",
      "name": "SQLite - Mark Review Requested",
      "type": "n8n-nodes-base.sqlite",
      "typeVersion": 1,
      "position": [
        850,
        300
      ],
      "credentials": {
        "sqlite": "fluxion_db"
      }
    }
  ],
  "connections": {
    "trigger_daily": {
      "main": [
        [
          {
            "node": "query_reviews",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "query_reviews": {
      "main": [
        [
          {
            "node": "send_review_request",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "send_review_request": {
      "main": [
        [
          {
            "node": "mark_review_sent",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## Import Instructions

1. In n8n UI, go to **Workflows → Import**
2. Paste each JSON above
3. Configure credentials:
   - `sqlite`: Point to FLUXION SQLite DB
   - `whatsappApi`: WhatsApp Business credentials
   - Email: SMTP settings

4. Test each workflow:
   - Booking Reminder: Runs at 9 AM daily
   - Invoice Generator: Triggers on appointment completion
   - Loyalty Update: Auto-runs after appointment
   - Review Request: Runs 3 days post-appointment

---

## Workflow Status

| Workflow | Trigger | Action | Status |
|----------|---------|--------|--------|
| WhatsApp Chatbot | Message received | Voice pipeline | ✅ ACTIVE |
| Booking Reminder | Daily 9 AM | SMS/WhatsApp | ⏳ IMPORT |
| Invoice Generator | Appointment completed | Email PDF | ⏳ IMPORT |
| Loyalty Update | Appointment completed | Points + SMS | ⏳ IMPORT |
| Review Request | 3 days post-appt | WhatsApp link | ⏳ IMPORT |

---

**Last Updated**: 15 Gennaio 2026  
**Status**: Ready for Import  
**Next**: Test in staging environment
