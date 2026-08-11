# Bug Corpus — TypeScript

## Bug 01 — XSS via innerHTML

### Buggy Code
```typescript
function renderInput(input: string): void {
  document.getElementById("output")!.innerHTML = input;
}
```

### Issue
Direct innerHTML assignment enables XSS attacks.

### Fixed Code
```typescript
function renderInput(input: string): void {
  document.getElementById("output")!.textContent = input;
}
```

---

## Bug 02 — Missing Error Handling

### Buggy Code
```typescript
async function fetchUser(id: number): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
}
```

### Issue
No error handling for network failures or non-200 responses.

### Fixed Code
```typescript
async function fetchUser(id: number): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
```

---

## Bug 03 — Any Type Abuse

### Buggy Code
```typescript
function process(data: any): any {
  return data.value * 2;
}
```

### Issue
`any` defeats TypeScript's type safety.

### Fixed Code
```typescript
interface Processable { value: number }
function process(data: Processable): number {
  return data.value * 2;
}
```

---

## Bug 04 — Callback Hell

### Buggy Code
```typescript
getUser(id, (user) => {
  getOrders(user.id, (orders) => {
    getItems(orders[0].id, (items) => {
      console.log(items);
    });
  });
});
```

### Issue
Deeply nested callbacks, hard to read and error-handle.

### Fixed Code
```typescript
const user = await getUser(id);
const orders = await getOrders(user.id);
const items = await getItems(orders[0].id);
```

---

## Bug 05 — Floating Promises

### Buggy Code
```typescript
function saveData(data: Data): void {
  fetch("/api/save", { method: "POST", body: JSON.stringify(data) });
}
```

### Issue
Promise not awaited or returned — errors silently lost.

### Fixed Code
```typescript
async function saveData(data: Data): Promise<void> {
  await fetch("/api/save", { method: "POST", body: JSON.stringify(data) });
}
```

---

## Bug 06 — Loose Equality

### Buggy Code
```typescript
if (value == null) { return; }
```

### Issue
`==` has unexpected coercion rules.

### Fixed Code
```typescript
if (value === null || value === undefined) { return; }
```

---

## Bug 07 — Missing Null Check

### Buggy Code
```typescript
function getLength(str: string | null): number {
  return str.length;
}
```

### Issue
Will throw if str is null.

### Fixed Code
```typescript
function getLength(str: string | null): number {
  return str?.length ?? 0;
}
```

---

## Bug 08 — Mutation of Props

### Buggy Code
```typescript
function sortItems(items: string[]): string[] {
  return items.sort();
}
```

### Issue
`sort()` mutates the original array.

### Fixed Code
```typescript
function sortItems(items: string[]): string[] {
  return [...items].sort();
}
```

---

## Bug 09 — Unbounded Loop

### Buggy Code
```typescript
function find(items: number[], target: number): number {
  let i = 0;
  while (items[i] !== target) { i++; }
  return i;
}
```

### Issue
Infinite loop if target not found.

### Fixed Code
```typescript
function find(items: number[], target: number): number {
  return items.indexOf(target);
}
```

---

## Bug 10 — Hardcoded Secrets

### Buggy Code
```typescript
const API_KEY = "sk-proj-abc123def456";
```

### Issue
Secret committed to source code.

### Fixed Code
```typescript
const API_KEY = process.env.API_KEY;
if (!API_KEY) throw new Error("API_KEY not configured");
```
