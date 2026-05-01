/// <reference types="vite/client" />

// S184 α.1.2 — Sentry release tag (defined in vite.config.ts)
declare const __APP_VERSION__: string;

interface ImportMetaEnv {
  readonly VITE_SENTRY_DSN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
