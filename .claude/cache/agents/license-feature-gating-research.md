# License Feature Gating — Research & Gap Analysis
> Research file for Voice Agent + Scheda Dynamic license feature gating implementation
> **Status**: ✅ Complete analysis
> **Date**: 2026-03-04

---

## EXECUTIVE SUMMARY

**3 Critical Issues Found:**
1. **Pricing mismatch**: Codified €199/€399/€799 vs actual €297/€497/€897
2. **VoiceAgent.tsx**: Missing license gate entirely — renders for all tiers
3. **Sidebar.tsx**: Voice Agent menu always visible — should be Pro+ only

**Pattern exists**: SchedaClienteDynamic (schede-cliente) has complete feature gating implementation to copy.

---

## 1. PRICING DISCREPANCIES (€€€)

### Current Codified Pricing (WRONG ❌)
- **Base**: €199 (should be €297)
- **Pro**: €399 (should be €497)
- **Enterprise**: €799 (should be €897)

### Files with outdated pricing

**File 1: `/Volumes/MontereyT7/FLUXION/src/types/license-ed25519.ts`**
- **Lines 120, 133, 147**: `LICENSE_TIERS_ED25519` constant array
  - Line 120: `price: 199,` (Base)
  - Line 133: `price: 399,` (Pro)
  - Line 147: `price: 799,` (Enterprise)
- Export function: `getTierPrice()` at line 166-169 (reads from array)

**File 2: `/Volumes/MontereyT7/FLUXION/src-tauri/src/commands/license_ed25519.rs`**
- **Lines 734-745**: Base tier TierInfo (line 738 `price: 199`)
- **Lines 747-760**: Pro tier TierInfo (line 751 `price: 399`)
- **Lines 761-772**: Enterprise tier TierInfo (line 765 `price: 799`)
- Function: `get_tier_info_ed25519()` at line 719 (hardcoded TierInfo vecs)

### Update Plan
```
TypeScript:  199 → 297  |  399 → 497  |  799 → 897
Rust:        199 → 297  |  399 → 497  |  799 → 897
```

---

## 2. PATTERN: SchedaClienteDynamic Feature Gating (REFERENCE IMPLEMENTATION)

### Reference File
**Path**: `/Volumes/MontereyT7/FLUXION/src/components/schede-cliente/SchedaClienteDynamic.tsx`

### How It Works (lines 141-170)

**Step 1: Import hook (line 8)**
```typescript
import { useLicenseStatusEd25519 } from '../../hooks/use-license-ed25519';
```

**Step 2: Use hook (lines 142-143)**
```typescript
const { data: licenseStatus, isLoading: isLoadingLicense } = useLicenseStatusEd25519();
```

**Step 3: Handle loading state (lines 145-153)**
```typescript
if (isLoadingConfig || isLoadingLicense) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-8 text-center text-slate-400">
        Caricamento configurazione...
      </CardContent>
    </Card>
  );
}
```

**Step 4: Build access logic (lines 164-166)**
```typescript
// Enterprise OR in enabled_verticals OR trial = HAS ACCESS
const hasAccess = licenseStatus?.tier === 'enterprise' || 
                  licenseStatus?.enabled_verticals?.includes(verticale) ||
                  licenseStatus?.tier === 'trial';
```

**Step 5: Gate with SchedaBloccata (lines 168-170)**
```typescript
if (!hasAccess && licenseStatus?.tier !== 'trial') {
  return <SchedaBloccata vertical={verticale} tier={licenseStatus?.tier_display || 'Base'} />;
}
```

**Step 6: Render correct component (lines 173-223)**
```typescript
// Only reaches here if hasAccess === true
switch (microCategoria) {
  case 'odontoiatra':
    return <SchedaOdontoiatrica clienteId={clienteId} />;
  // ... other cases
}
```

### The Lock Component: `SchedaBloccata` (lines 61-97)

**Appearance:**
- Lock icon in amber badge (lines 71-72)
- Title: "Scheda Non Disponibile"
- Subtitle: "Aggiorna la tua licenza per sbloccare"
- Message: `La scheda <strong>{vertical}</strong> non è inclusa nel tuo piano attuale`
- Current tier display: `Piano attuale: <span className="text-cyan-400">{tier}</span>`
- Button: "Aggiorna Licenza" with gradient (cyan → teal)

**Code pattern (lines 68-96):**
```typescript
function SchedaBloccata({ 
  vertical, 
  tier 
}: { 
  vertical: string; 
  tier: string;
}) {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader className="flex flex-row items-center gap-3">
        <div className="p-2 bg-amber-500/20 rounded-lg">
          <Lock className="w-6 h-6 text-amber-500" />
        </div>
        <div>
          <CardTitle className="text-white">Scheda Non Disponibile</CardTitle>
          <p className="text-sm text-slate-400">Aggiorna la tua licenza per sbloccare</p>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="bg-slate-900 p-4 rounded-lg text-center">
          <p className="text-slate-300 mb-2">
            La scheda <span className="text-amber-400 font-medium">{vertical}</span> non è inclusa nel tuo piano attuale.
          </p>
          <p className="text-slate-500 text-sm">
            Piano attuale: <span className="text-cyan-400">{tier}</span>
          </p>
        </div>
        <div className="flex justify-center">
          <Button className="bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-700 hover:to-teal-700">
            <Sparkles className="w-4 h-4 mr-2" />
            Aggiorna Licenza
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

---

## 3. GAP ANALYSIS: Voice Agent Feature Gating

### ISSUE 1: VoiceAgent.tsx Missing Gate

**File**: `/Volumes/MontereyT7/FLUXION/src/pages/VoiceAgent.tsx`

**Current state:**
- Line 6: Imports 17 hooks from `use-voice-pipeline`
- **Line 8 onwards**: NO import of `useLicenseStatusEd25519`
- **Line 59-800**: `export function VoiceAgent()` renders UI unconditionally
- **Feature**: `voice_agent: boolean` is in `LicenseFeatures`
- **Tier availability**: Trial ✅ | Base ❌ | Pro ✅ | Enterprise ✅

**Where gate should be:**
1. **Line 40 (imports section)**: Add
   ```typescript
   import { useLicenseStatusEd25519 } from '@/hooks/use-license-ed25519';
   ```

2. **Line 59-78 (component start, after existing hooks)**: Add
   ```typescript
   const { data: licenseStatus, isLoading: isLoadingLicense } = useLicenseStatusEd25519();
   ```

3. **Line 329 (before JSX return statement)**: Add access check
   ```typescript
   const canAccessVoiceAgent = licenseStatus?.features.voice_agent === true;
   
   if (!isLoadingLicense && !canAccessVoiceAgent) {
     return <VoiceAgentBloccato tier={licenseStatus?.tier_display || 'Base'} />;
   }
   ```

**New component needed**: `VoiceAgentBloccato` (similar to SchedaBloccata)
- Title: "Voice Agent Non Disponibile"
- Message: "Il Voice Agent è disponibile solo nei piani Pro ed Enterprise"
- Show current tier
- Upgrade button

### ISSUE 2: Sidebar.tsx Always Shows Voice Agent

**File**: `/Volumes/MontereyT7/FLUXION/src/components/layout/Sidebar.tsx`

**Current state:**
- **Lines 38-49**: Static `NAV_ITEMS` array with hardcoded menu items
- **Line 47**: `{ icon: Mic, label: 'Voice Agent', path: '/voice', testId: 'sidebar-voice' },`
- **Lines 55-125**: Navigation rendering loop (no license check)
- **Issue**: Voice Agent menu item always visible for all tiers

**Where gate should be:**

**Option A: Hide Voice Agent for Base (cleaner UX)**
- Add hook at component start (after line 56):
  ```typescript
  const { data: licenseStatus } = useLicenseStatusEd25519();
  ```
- Filter `NAV_ITEMS` before rendering (around line 100):
  ```typescript
  const visibleItems = NAV_ITEMS.filter(item => {
    if (item.path === '/voice') {
      return licenseStatus?.features.voice_agent === true;
    }
    return true;
  });
  ```
- Map `visibleItems` instead of `NAV_ITEMS` in line 100 loop

**Option B: Gray out Voice Agent for Base (show but disabled)**
- Add hook + build access check
- Add conditional className to link (line 109):
  ```typescript
  className={cn(
    'flex items-center gap-3 px-3 py-2.5 rounded-md transition-all',
    'hover:bg-slate-800/50',
    item.path === '/voice' && !licenseStatus?.features.voice_agent
      ? 'opacity-40 pointer-events-none cursor-not-allowed'
      : isActive
      ? 'bg-teal-500/20 text-teal-400'
      : 'text-slate-300 hover:text-white'
  )}
  ```

**Recommendation**: Use **Option A (hide)** for cleaner UX. Base tier users won't see irrelevant menu items.

---

## 4. AVAILABLE LICENSE HOOKS

**File**: `/Volumes/MontereyT7/FLUXION/src/hooks/use-license-ed25519.ts`

### Query Hooks (read-only)

| Hook | Return Type | Params | Use Case | Cache |
|------|-------------|--------|----------|-------|
| `useLicenseStatusEd25519()` | `Query<LicenseStatusEd25519>` | none | Full license status object | 5 min |
| `useTierInfoEd25519()` | `Query<TierInfo[]>` | none | All available tier info | 1 hour |
| `useFeatureAccessEd25519(feature)` | `Query<boolean>` | `feature: string` | Check single feature (e.g., "voice_agent") | 5 min |
| `useVerticalAccessEd25519(vertical)` | `Query<boolean>` | `vertical: string` | Check vertical access | 5 min |
| `useMachineFingerprint()` | `Query<string>` | none | Hardware fingerprint | Never stale |

### Mutation Hooks (state-changing)

| Hook | Return Type | Input | Effect |
|------|-------------|-------|--------|
| `useActivateLicenseEd25519()` | `Mutation<ActivationResultEd25519>` | `licenseData: string` | Activate license, invalidate all queries |
| `useDeactivateLicenseEd25519()` | `Mutation<void>` | none | Downgrade to trial, invalidate all queries |

### Convenience Hooks

| Hook | Return Type | Logic |
|------|-------------|-------|
| `useLicenseInfo()` | Combined object | status + tierInfo + fingerprint in one call |
| `useHasValidLicense()` | `boolean` | Returns `status?.is_valid ?? false` |
| `useIsTrial()` | `boolean` | Returns `status?.tier === 'trial'` |
| `useIsTrialExpiring()` | `boolean` | Trial AND days_remaining ≤ 7 |
| `useCurrentTier()` | `string` | Returns tier name or 'none' |

### Feature Object Structure

From `LicenseStatusEd25519.features`:
```typescript
{
  voice_agent: boolean,           // Pro+ feature
  whatsapp_ai: boolean,           // Pro+ feature
  rag_chat: boolean,              // Pro+ feature
  fatturazione_pa: boolean,       // All tiers
  loyalty_advanced: boolean,      // Pro+ feature
  api_access: boolean,            // Enterprise only
  max_verticals: number           // 1=Base, 3=Pro, 99=Trial, 0=Enterprise
}
```

---

## 5. TIER FEATURE MATRIX (Backend Definition)

**Source**: `src-tauri/src/commands/license_ed25519.rs` lines 174-215 (`LicenseFeatures::for_tier()`)

### Feature Availability by Tier

| Feature | Trial | Base | Pro | Enterprise | Gate Type |
|---------|-------|------|-----|------------|-----------|
| voice_agent | ✅ true | ❌ false | ✅ true | ✅ true | Feature flag |
| whatsapp_ai | ✅ true | ❌ false | ✅ true | ✅ true | Feature flag |
| rag_chat | ✅ true | ❌ false | ✅ true | ✅ true | Feature flag |
| fatturazione_pa | ✅ true | ✅ true | ✅ true | ✅ true | Feature flag |
| loyalty_advanced | ✅ true | ❌ false | ✅ true | ✅ true | Feature flag |
| api_access | ✅ true | ❌ false | ❌ false | ✅ true | Feature flag |
| max_verticals | 99 | 1 | 3 | 0 (unlimited) | Numeric |

### Verification Functions (lines 673-715)

**`check_feature_access_ed25519(feature: String) -> bool`** (line 675)
- Params: feature name ("voice_agent", "whatsapp_ai", etc.)
- Returns: feature enabled for current tier
- Used by: Frontend to determine UI visibility

**`check_vertical_access_ed25519(vertical: String) -> bool`** (line 698)
- Params: vertical name
- Logic:
  - If invalid license: false
  - If Enterprise: true (all verticals)
  - Else: check if in `enabled_verticals` list
- Used by: SchedaClienteDynamic to gate schede

---

## 6. ACCEPTANCE CRITERIA & IMPLEMENTATION PLAN

### AC1: VoiceAgent.tsx shows locked state for Base tier

**Acceptance**: User with Base tier sees lock screen instead of Voice Agent UI

**Implementation Steps**:

1. Import hook:
   ```typescript
   import { useLicenseStatusEd25519 } from '@/hooks/use-license-ed25519';
   ```

2. Get license status in component:
   ```typescript
   const { data: licenseStatus, isLoading: isLoadingLicense } = useLicenseStatusEd25519();
   ```

3. Create `VoiceAgentBloccato` component (new file or inline):
   - Lock icon + amber badge
   - Title: "Voice Agent Non Disponibile"
   - Message: "Il Voice Agent è disponibile nei piani Pro ed Enterprise"
   - Show tier: `licenseStatus?.tier_display`
   - Button: "Aggiorna Licenza"

4. Add gate before render (before line 329):
   ```typescript
   if (!isLoadingLicense && !licenseStatus?.features.voice_agent) {
     return <VoiceAgentBloccato tier={licenseStatus?.tier_display || 'Base'} />;
   }
   ```

5. Test: Base user sees lock, Pro/Enterprise/Trial users see full UI

### AC2: Sidebar hides Voice Agent for Base tier

**Acceptance**: Base tier users don't see "Voice Agent" menu item

**Implementation Steps**:

1. Import hook:
   ```typescript
   import { useLicenseStatusEd25519 } from '@/hooks/use-license-ed25519';
   ```

2. Get license status (after line 56):
   ```typescript
   const { data: licenseStatus } = useLicenseStatusEd25519();
   ```

3. Filter nav items (before line 100):
   ```typescript
   const visibleItems = NAV_ITEMS.filter(item => {
     if (item.path === '/voice') {
       return licenseStatus?.features.voice_agent === true;
     }
     return true;
   });
   ```

4. Update render loop (line 100):
   ```typescript
   {visibleItems.map((item) => {
     // ... rest of mapping code
   })}
   ```

5. Test: Base tier sees 8 items (no Voice), Pro+ sees 9 items (with Voice)

### AC3: Pricing constants corrected everywhere

**Acceptance**: All pricing in UI and backend matches €297/€497/€897

**Implementation Steps**:

1. **File**: `src/types/license-ed25519.ts`
   - Line 120: `price: 199,` → `price: 297,`
   - Line 133: `price: 399,` → `price: 497,`
   - Line 147: `price: 799,` → `price: 897,`

2. **File**: `src-tauri/src/commands/license_ed25519.rs`
   - Line 738: `price: 199,` → `price: 297,`
   - Line 751: `price: 399,` → `price: 497,`
   - Line 765: `price: 799,` → `price: 897,`

3. Test: Verify `getTierPrice()` returns correct prices

---

## 7. FILES TO MODIFY (SUMMARY)

| # | File | Lines | Type | Change | Effort |
|---|------|-------|------|--------|--------|
| 1 | `src/types/license-ed25519.ts` | 120, 133, 147 | Price update | 199→297, 399→497, 799→897 | 5 min |
| 2 | `src-tauri/src/commands/license_ed25519.rs` | 738, 751, 765 | Price update | 199→297, 399→497, 799→897 | 5 min |
| 3 | `src/pages/VoiceAgent.tsx` | 6-80, 329+ | Feature gate | Add hook + gate + locked component | 30 min |
| 4 | `src/components/layout/Sidebar.tsx` | 56-125 | Feature gate | Add hook + filter nav | 20 min |
| NEW | `src/components/layout/VoiceAgentBloccato.tsx` | — | New component | Lock screen for Base | 15 min |

**Total Implementation Effort**: ~1.25 hours

---

## 8. EDGE CASES & NOTES

### Loading States
- Both `VoiceAgent.tsx` and `Sidebar.tsx` will have 5-min cache on license status
- Use `isLoading` flags to prevent flickering
- Default to "show" while loading (optimistic)

### Trial Behavior
- Trial tier has `voice_agent: true` (full feature)
- Should NOT see lock screen
- Pattern in SchedaClienteDynamic: `|| licenseStatus?.tier === 'trial'` to allow trial access

### Enterprise Fallback
- Enterprise has all features enabled
- Check `tier === 'enterprise'` OR feature flag

### Sidebar Menu Flexibility
- Only Voice Agent needs gating (other features not tier-locked yet)
- Future: Cassa, Fornitori may also need gating
- Current filter is minimal (only /voice path)

### TypeScript Strictness
- No `any` types
- No `@ts-ignore`
- Proper null checks on `licenseStatus?.features.voice_agent`

---

## 9. REFERENCE: Hook Query Keys

For debugging / cache invalidation:

```typescript
licenseEd25519Keys = {
  all: ['license-ed25519'],
  status: () => ['license-ed25519', 'status'],
  tierInfo: () => ['license-ed25519', 'tier-info'],
  feature: (feature) => ['license-ed25519', 'feature', feature],
  vertical: (vertical) => ['license-ed25519', 'vertical', vertical],
}
```

Both mutations invalidate `licenseEd25519Keys.all` on success → all queries refetch.

---

## VERIFICATION CHECKLIST

Before marking AC complete:

- [ ] `npm run type-check` → 0 errors
- [ ] VoiceAgent.tsx: Base tier shows lock, Pro+ shows UI
- [ ] Sidebar: Base tier missing Voice Agent item, Pro+ has it
- [ ] Pricing updated: €297/€497/€897 in both TS and Rust
- [ ] No `any` types, no `@ts-ignore`
- [ ] Existing tests still pass
- [ ] Test with trial user (should see full VoiceAgent UI)

---

**Status**: ✅ Ready for implementation phase (FASE 3)
