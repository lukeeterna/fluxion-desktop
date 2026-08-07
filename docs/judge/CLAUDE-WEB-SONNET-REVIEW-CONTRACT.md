# Contratto review — Claude Web Sonnet

Ogni review usa una nuova sessione browser stateless con modello Sonnet. Il reviewer riceve soltanto il dossier sigillato e l'attestazione del nodo Claude Code Web.

Output JSON obbligatorio, senza testo esterno:

- `schema_version: 1`
- `reviewer: "CLAUDE_WEB_SONNET"`
- `model: "Sonnet"`
- `repository`
- `pr_number`
- `base_sha`
- `head_sha`
- `dossier_sha256`
- `ccweb_attestation_sha256`
- `verdict: GREEN|RED|BLOCKED`
- `safe_to_merge: yes|no`
- `summary`
- `findings[]`
- `required_changes[]`
- `next_action`

`safe_to_merge=yes` è consentito soltanto con `verdict=GREEN`. Il reviewer non modifica GitHub, file, runtime o task e non usa il ragionamento dell'autore/esecutore come prova.
