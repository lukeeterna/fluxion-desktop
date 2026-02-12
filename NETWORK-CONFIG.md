# Fluxion Network Configuration

## IP Statici (da configurare su router)

| Dispositivo | IP | MAC Address | Note |
|-------------|----|-------------|------|
| iMac (Voice Agent) | 192.168.1.7 | - | Server Voice Agent |
| MacBook (Dev) | 192.168.1.8 | - | Sviluppo |

## Porte

| Servizio | Porta | Protocollo | Note |
|----------|-------|------------|------|
| Voice Agent HTTP | 3002 | TCP | API REST |
| Tauri Bridge | 3001 | TCP | HTTP Bridge |

## Test Cross-Machine

```bash
# Da MacBook, test connessione a iMac
curl http://192.168.1.7:3002/health

# Test completo
python3 voice-agent/scripts/test_cross_machine.py
```

## CoVe Verification Checklist

- [ ] IP statico configurato su router
- [ ] Test cross-machine eseguito con successo
- [ ] Voice Agent ascolta su 0.0.0.0 (tutte le interfacce)
- [ ] Firewall permette traffico porta 3002
