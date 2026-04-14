---
name: S154 Audit — Recurring anti-patterns to avoid
description: Patterns found in S154 audit that should not be repeated in new code
type: feedback
---

Never catch mutateAsync errors silently (console.error only). Always add toast.error() in every catch block that handles a user-triggered mutation.

**Why:** S154 audit found 13 catch blocks in Clienti, Cassa, Fatture, Fornitori that swallow errors without any user feedback. PMI users have no way to know the operation failed.

**How to apply:** Every async handler that calls mutateAsync() MUST have `toast.error('...', { description: String(error) })` in the catch block. No exceptions.

---

Always destructure `error` from useQuery alongside `isLoading` and `data`. Never render a page that can silently go blank on query failure.

**Why:** Cassa.tsx destructures `isLoading` but not `error` — if the query fails, the loading spinner disappears and a blank section renders with no message.

**How to apply:** Pattern: `const { data, isLoading, error } = useQuery(...)`. Always add `if (error)` render path.

---

Icon-only interactive elements must have aria-label.

**Why:** Calendar navigation buttons, search clear button found without aria-label in S154. Keyboard/screen reader users cannot identify them.

**How to apply:** Any `<Button>` or `<button>` that contains only an icon (no visible text) must have `aria-label="..."` in Italian.
