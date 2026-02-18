#!/bin/zsh
export PATH="/usr/local/bin:$HOME/.cargo/bin:$HOME/.nvm/versions/node/v20.18.2/bin:$PATH"
cd "/Volumes/MacSSD - Dati/fluxion"
echo "🚀 Avvio Fluxion..."
npm run tauri dev
