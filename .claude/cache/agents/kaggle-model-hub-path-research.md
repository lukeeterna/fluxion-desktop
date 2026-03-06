# Kaggle Model Hub — Path di Montaggio FLUX.1-schnell
> Research CoVe 2026 — 2026-03-05

## TL;DR — Risposte Dirette

### 1. Qual e' il path ESATTO a runtime?

**Path confermato da esempi reali (dev):**
```
/kaggle/input/flux/pytorch/flux.1-dev/1/flux1-dev.safetensors
```

**Path atteso per schnell (stesso pattern):**
```
/kaggle/input/flux/pytorch/flux.1-schnell/1/flux1-schnell.safetensors
```

**OPPURE (variante alternativa, da verificare):**
```
/kaggle/input/flux/pytorch/flux1-schnell/1/flux1-schnell.safetensors
```

### 2. Il path e' case-sensitive? pyTorch o pytorch?

**Il path usa `pytorch` (lowercase) — NON `pyTorch`.**

Il metadata `kernel-metadata.json` usa `pyTorch` con la P maiuscola:
```json
"model_sources": ["black-forest-labs/flux/pyTorch/flux1-schnell/1"]
```

Ma il **mount path a runtime usa lowercase `pytorch`**, confermato dalla path reale:
```
/kaggle/input/flux/pytorch/flux.1-dev/1/...
```

**Spiegazione tecnica:** Il Kaggle backend (`AttachDatasourceUsingJwt` API) genera il `mountSlug`
indipendentemente dalla stringa nel metadata. Il mountSlug e' costruito server-side e usa lowercase
per il framework. Il kagglehub client poi costruisce il path come:
```python
cached_path = f"{base_mount_path}/{result['mountSlug']}"
# = "/kaggle/input/" + "flux/pytorch/flux.1-dev/1"
```

### 3. Variation slug nel path: `flux1-schnell` o `flux.1-schnell`?

**INCERTEZZA:** Non e' stato trovato un esempio live confermato per schnell.

**Per dev** il variation slug nel path e' `flux.1-dev` (CON il punto):
```
/kaggle/input/flux/pytorch/flux.1-dev/1/
                              ^^^^^^^^
                              variazione slug con PUNTO
```

**Per schnell**, basandosi sul pattern identico, dovrebbe essere `flux.1-schnell`:
```
/kaggle/input/flux/pytorch/flux.1-schnell/1/
```

**MA** — il metadata del kernel usa `flux1-schnell` (SENZA punto):
```json
"model_sources": ["black-forest-labs/flux/pyTorch/flux1-schnell/1"]
```

Questa discrepanza (senza punto nel metadata, con punto nel path) e' coerente con come Kaggle
normalizza i nomi dei modelli: la variation slug nel path riflette il nome originale del modello
registrato su Kaggle, non necessariamente la stringa nel metadata.

**Conclusione:** Usare la strategia glob/find per trovare il path corretto (vedi sotto).

---

## Architettura del Path Kaggle — Come Funziona

### Formato ufficiale (da Kaggle models_metadata.md)
```
/kaggle/input/<model_slug>/<framework>/<variation_slug>/<version>/
/kaggle/input/<model_slug>/<framework>/<variation_slug>/<version>/<filename>
```

### Fonti autorevoli
1. **Kaggle API docs** (`models_metadata.md`): conferma il formato con template variables `${PATH}` e `${FILEPATH}`
2. **kohya-ss/sd-scripts issue #1571**: mostra path reale `/kaggle/input/flux/pytorch/flux.1-dev/1/flux1-dev.safetensors`
3. **kagglehub source code** (`kaggle_cache_resolver.py`): conferma che il mountSlug e' generato dal backend Kaggle
4. **Kaggle notebook pubblici**: crischir/testing-flux1-flux-1-dev, crischir/testing-flux1-model-schnel

### Framework normalization (case)
| Nel metadata (kernel-metadata.json) | Nel path a runtime (/kaggle/input) |
|--------------------------------------|-------------------------------------|
| `pyTorch` | `pytorch` |
| `tensorFlow2` | `tensorflow2` (presumibile) |
| `jax` | `jax` |

Il backend Kaggle lowercase-ifica il framework nel mountSlug.

### Struttura file FLUX.1 su Kaggle (formato diffusers/HuggingFace)
```
/kaggle/input/flux/pytorch/flux.1-dev/1/
├── flux1-dev.safetensors           # modello principale (singolo file)
```

Per schnell (stesso pattern atteso):
```
/kaggle/input/flux/pytorch/flux.1-schnell/1/
├── flux1-schnell.safetensors       # modello principale
```

**ATTENZIONE:** Kaggle monta i modelli in formato "singolo file safetensors", NON in formato
directory diffusers completa (transformer/, vae/, text_encoder/, etc.). Per usare con diffusers
occorre usare `from_single_file()`.

---

## Problema nel Kernel Corrente

Il tuo `kernel-metadata.json` usa:
```json
"model_sources": ["black-forest-labs/flux/pyTorch/flux1-schnell/1"]
```

Possibili cause del path non trovato:
1. **Il variation slug nel path e' `flux.1-schnell` (con punto), non `flux1-schnell`** — discrepanza tra metadata string e runtime path
2. **L'accesso al modello e' soggetto ad accettazione T&C** — se non hai accettato i termini di utilizzo di FLUX.1-schnell su Kaggle, il modello non viene montato
3. **Il modello richiede autenticazione** — FLUX.1-dev richiede sign-in e accettazione licenza

---

## Codice Python Robusto per Trovare il Path

```python
import os
import glob

def find_flux_schnell_path() -> str | None:
    """
    Trova il path di FLUX.1-schnell montato da Kaggle in modo robusto.
    Gestisce varianti del variation slug (con/senza punto, case).
    """
    base = "/kaggle/input"

    # Strategia 1: path esatto atteso (basato sul pattern flux.1-dev)
    candidates = [
        f"{base}/flux/pytorch/flux.1-schnell/1",
        f"{base}/flux/pytorch/flux1-schnell/1",
        f"{base}/flux/pyTorch/flux.1-schnell/1",
        f"{base}/flux/pyTorch/flux1-schnell/1",
    ]

    for path in candidates:
        if os.path.isdir(path):
            print(f"[INFO] Trovato path FLUX.1-schnell: {path}")
            return path

    # Strategia 2: glob wildcard su varianti del variation slug
    patterns = [
        f"{base}/flux/*/flux*schnell/*",
        f"{base}/flux/*/flux.1-schnell/*",
    ]

    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            # Prendi la versione piu' alta (massimo numerico)
            path = sorted(matches, key=lambda p: int(p.split('/')[-1]) if p.split('/')[-1].isdigit() else 0)[-1]
            print(f"[INFO] Trovato via glob: {path}")
            return path

    # Strategia 3: cerca qualsiasi directory contenente flux1-schnell.safetensors
    for root, dirs, files in os.walk("/kaggle/input/flux"):
        for f in files:
            if "schnell" in f.lower() and f.endswith(".safetensors"):
                path = root
                print(f"[INFO] Trovato safetensors: {os.path.join(root, f)}")
                return path

    # Strategia 4: debug — lista tutto quello che e' montato
    print("[DEBUG] Contenuto /kaggle/input:")
    try:
        for item in os.listdir("/kaggle/input"):
            item_path = os.path.join("/kaggle/input", item)
            if os.path.isdir(item_path):
                print(f"  DIR: {item_path}")
                try:
                    for sub in os.listdir(item_path):
                        print(f"    {sub}")
                except:
                    pass
    except Exception as e:
        print(f"[ERROR] {e}")

    return None


def find_flux_model_file(base_path: str) -> str | None:
    """Trova il file .safetensors dentro il path montato."""
    if not base_path:
        return None

    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.endswith(".safetensors") and "schnell" in f.lower():
                return os.path.join(root, f)
        # Anche file con solo "flux" nel nome
        for f in files:
            if f.endswith(".safetensors"):
                return os.path.join(root, f)

    return None


# Utilizzo:
MODEL_PATH = find_flux_schnell_path()
MODEL_FILE = find_flux_model_file(MODEL_PATH)

if MODEL_FILE:
    print(f"[OK] Modello trovato: {MODEL_FILE}")
    # Carica con diffusers (single file)
    from diffusers import FluxPipeline
    pipe = FluxPipeline.from_single_file(MODEL_FILE, torch_dtype=torch.bfloat16)
else:
    print("[ERRORE] Modello FLUX.1-schnell non trovato in /kaggle/input")
    # Fallback: download da HuggingFace
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-schnell",
        torch_dtype=torch.bfloat16
    )
```

---

## Debug Immediato — Aggiungi questo all'inizio del kernel

```python
import os
import subprocess

# Lista tutto cio' che e' montato
result = subprocess.run(['find', '/kaggle/input', '-maxdepth', '5', '-type', 'd'],
                       capture_output=True, text=True)
print(result.stdout)

# Controlla se il modello e' visibile
result2 = subprocess.run(['find', '/kaggle/input', '-name', '*.safetensors'],
                        capture_output=True, text=True)
print(result2.stdout)
```

Questo output rivelera' il path esatto come montato da Kaggle.

---

## Alternative se il Path Continua a Non Funzionare

### Opzione A: Usa kagglehub (piu' affidabile)
```python
import kagglehub
path = kagglehub.model_download("black-forest-labs/flux/pyTorch/flux1-schnell/1")
print(f"Path: {path}")  # Mostra il path reale
```

### Opzione B: Usa dataset invece di model_sources
Invece di `model_sources`, aggiungi il modello come `dataset_sources` tramite:
1. Kaggle UI: "Add Data" -> cerca "flux schnell"
2. oppure aggiungi il dataset `hanqiangfei/flux1-schnell.safetensors`
   - Path risultante: `/kaggle/input/flux1-schnell-safetensors/...`

### Opzione C: Download HuggingFace (richiede internet abilitato)
```python
from diffusers import FluxPipeline
pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-schnell",
    token=os.environ.get("HF_TOKEN"),  # Non necessario per schnell (Apache 2.0)
    torch_dtype=torch.bfloat16
)
```

---

## Checklist Debug Kaggle Model Sources

1. **Hai accettato i termini di utilizzo?**
   - Vai su https://www.kaggle.com/models/black-forest-labs/flux/pyTorch/flux1-schnell
   - Clicca "I Understand and Accept" se richiesto

2. **Verifica kernel-metadata.json**
   - Formato corretto: `"black-forest-labs/flux/pyTorch/flux1-schnell/1"`
   - NON usare `"black-forest-labs/FLUX.1-schnell"` (formato HuggingFace, non Kaggle)

3. **Esegui debug find all'inizio del notebook**

4. **Controlla se la versione e' giusta** — la versione `1` potrebbe non esistere,
   prova con versione `2` o `3` se disponibili

5. **Prova kagglehub.model_download()** — gestisce automaticamente varianti di path

---

## Fonti Chiave

- [Kaggle models_metadata.md](https://github.com/Kaggle/kaggle-api/blob/main/docs/models_metadata.md) — formato ufficiale
- [kagglehub kaggle_cache_resolver.py](https://github.com/Kaggle/kagglehub/blob/main/src/kagglehub/kaggle_cache_resolver.py) — mountSlug logic
- [kohya-ss/sd-scripts issue #1571](https://github.com/kohya-ss/sd-scripts/issues/1571) — path reale `/kaggle/input/flux/pytorch/flux.1-dev/1/flux1-dev.safetensors`
- [Kaggle model FLUX.1](https://www.kaggle.com/models/black-forest-labs/flux) — pagina ufficiale
- [hanqiangfei/flux1-schnell.safetensors](https://www.kaggle.com/models/hanqiangfei/flux1-schnell.safetensors) — modello alternativo
