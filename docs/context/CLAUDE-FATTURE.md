# 🧾 FLUXION Fatturazione - XML FatturaPA

> Fatturazione elettronica italiana conforme SDI.

---

## Regime Fiscale

| Codice | Descrizione | Applicazione |
|--------|-------------|--------------|
| **RF01** | Ordinario | IVA normale |
| **RF19** | Forfettario | NO IVA + dicitura |

### Dati Emittente (da .env)

```
AZIENDA_NOME=Automation Business
AZIENDA_PARTITA_IVA=02159940762
AZIENDA_CODICE_FISCALE=DSTMGN81S12L738L
REGIME_FISCALE=RF19
```

---

## Validatori

### Codice Fiscale

```typescript
export function validaCodiceFiscale(cf: string): boolean {
    if (!cf || cf.length !== 16) return false;
    const pattern = /^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$/i;
    if (!pattern.test(cf)) return false;
    // Algoritmo carattere controllo...
    return true;
}
```

### Partita IVA

```typescript
export function validaPartitaIva(piva: string): boolean {
    if (!piva || piva.length !== 11) return false;
    if (!/^\d{11}$/.test(piva)) return false;
    // Algoritmo Luhn modificato...
    return true;
}
```

---

## Naming File XML

```
IT{PIVA}_{PROGRESSIVO}.xml

Esempio: IT02159940762_00001.xml
```

---

## Dicitura Regime Forfettario

```
Operazione effettuata ai sensi dell'articolo 1, commi da 54 a 89, 
della Legge n. 190/2014 - Regime forfettario.
Operazione senza applicazione dell'IVA.
```

---

*Ultimo aggiornamento: 2025-12-28*
