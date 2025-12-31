# 🎯 PROMPT 2 - E2E Test Customization for FLUXION

**Purpose**: This prompt helps Claude Code customize the E2E tests with real FLUXION app selectors and data-testid attributes.

---

## 📋 Before You Start

The E2E test **foundation is ready**:
- ✅ WebdriverIO configured (`wdio.conf.ts`)
- ✅ Page Objects created (BasePage, DashboardPage, ClientiPage, ServiziPage, CalendarioPage)
- ✅ Test suite base (smoke, navigation, CRUD, validation, conflict detection)
- ✅ Fixtures and test helpers
- ✅ npm scripts ready

**What's missing**: Real `data-testid` selectors from your actual UI components.

---

## 🔍 Information Needed from You

Please answer these questions to help me customize the tests:

### 1. **data-testid Attributes**

Do you have `data-testid` attributes in your UI components?

- [ ] Yes, already implemented
- [ ] No, need to add them
- [ ] Some components have them

If **Yes**, please provide examples from key pages:

**Dashboard:**
```tsx
// Example selectors you currently have
<div data-testid="dashboard-header">...</div>
<nav data-testid="sidebar">...</nav>
<a data-testid="sidebar-clienti">...</a>
```

**Clienti Page:**
```tsx
// What are the actual data-testid values?
<button data-testid="new-cliente-button">...</button>
<table data-testid="clienti-table">...</table>
```

**Servizi/Calendario similar info...**

### 2. **Page Structure**

**Question**: How are your main pages structured?

For **each page** (Dashboard, Clienti, Servizi, Operatori, Calendario):
- What is the page header selector? (h1, h2, or data-testid?)
- What are the main action buttons? (Nuovo Cliente, Nuovo Servizio, etc.)
- What are the table/grid selectors?
- What are the dialog/modal selectors?

### 3. **Form Fields**

**Question**: What are the `name` attributes for form fields?

**Clienti Form:**
- Name field: `name="___"`?
- Email field: `name="___"`?
- Phone field: `name="___"`?

**Servizi Form:**
- Nome: `name="___"`?
- Prezzo: `name="___"`?
- Durata: `name="___"`?

**Appuntamenti Form:**
- Cliente select: `name="___"`?
- Servizio select: `name="___"`?
- Data/ora: `name="___"`?

### 4. **Entities and IDs**

**Question**: How do you get entity IDs after creation?

- Does `createCliente` return the created cliente with `id`?
- Does `createServizio` return the servizio `id`?
- How can tests know the ID of created entities to use in other operations?

### 5. **Database Cleanup**

**Question**: Is there a way to clean test data?

- [ ] I have a Tauri command for cleanup (e.g., `reset_database`)
- [ ] I can delete all data with specific prefix (e.g., test@)
- [ ] Manual cleanup (SQL queries)
- [ ] No cleanup method yet

If you have a cleanup method, please describe it.

### 6. **Authentication/Login**

**Question**: Does FLUXION require authentication?

- [ ] No authentication - app opens directly to Dashboard
- [ ] Yes, there's a login page
- [ ] Planned for future

If **Yes**:
- What are the login form fields?
- What credentials should tests use?

### 7. **Error Messages**

**Question**: How are validation errors displayed?

- In form fields as `<FormMessage>` components?
- In a toast notification?
- In a banner at top of dialog?

What are the selectors for error messages?

### 8. **Calendar Specifics**

**Question**: How is the calendar grid structured?

- Are days clickable with `data-date="YYYY-MM-DD"` attributes?
- How are appointments rendered in day cells?
- What are the selectors for month navigation (prev/next/today buttons)?

### 9. **Loading States**

**Question**: What indicates the app is loading?

- Spinner selector: `[data-testid="___"]`?
- Loading skeleton: `[data-testid="___"]`?
- Disabled buttons while loading?

### 10. **Edge Cases You Want Tested**

**Question**: Any specific scenarios you want automated?

Examples:
- Bulk operations (create 100 clienti)
- Concurrent users
- Offline mode
- Specific business logic edge cases

---

## 🚀 What I'll Do Next

Based on your answers, I will:

1. **Add `data-testid` attributes** to your UI components (if needed)
2. **Update Page Objects** with real selectors
3. **Fix test specs** to use actual form field names
4. **Implement database cleanup** utility
5. **Add missing test scenarios** you requested
6. **Create helper functions** for common workflows (e.g., `createTestCliente()`)
7. **Add data seeding** for consistent test environments
8. **Optimize tests** for speed and reliability
9. **Add coverage reporting** to track tested features

---

## 📝 Optional: Even Without Answers

If you don't answer these questions, I can still:

- Generate **generic placeholder tests** that will need manual adjustment
- Add **TODO comments** where selectors need updating
- Create **utility scripts** to help you find selectors (`npm run e2e:find-selectors`)

---

## ✅ How to Use This Prompt

1. **Copy this entire section below** and send it to Claude Code:

```
I'm ready to customize FLUXION E2E tests. Here's the info:

1. data-testid attributes:
   [Your answer]

2. Page structure:
   [Your answer]

3. Form fields:
   [Your answer]

4. Entity IDs:
   [Your answer]

5. Database cleanup:
   [Your answer]

6. Authentication:
   [Your answer]

7. Error messages:
   [Your answer]

8. Calendar specifics:
   [Your answer]

9. Loading states:
   [Your answer]

10. Edge cases:
    [Your answer]
```

2. **Or just say**: "Proceed with placeholder tests, I'll update selectors manually later"

---

## 🎯 Expected Outcome

After customization, you'll have:

- ✅ **Production-ready E2E tests** that actually work with your UI
- ✅ **Regression test suite** for the 3 bugs we fixed
- ✅ **Automated validation** for all CRUD operations
- ✅ **CI/CD ready** tests for GitHub Actions
- ✅ **Documentation** on how to maintain and extend tests

---

**Ready? Send me the info above, or tell me to proceed with placeholders!** 🚀
