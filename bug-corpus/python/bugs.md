# Python Bug Corpus

## Bug 01 — Security: Unsafe eval usage

### Buggy Code
```python
def calculate(expression: str) -> float:
    return eval(expression)
```

### Issue
`eval()` executes arbitrary code — critical security vulnerability.

### Fixed Code
```python
import ast
import operator

def calculate(expression: str) -> float:
    allowed = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
    }
    tree = ast.parse(expression, mode="eval")
    return _eval_node(tree.body, allowed)
```

---

## Bug 02 — Missing Error Handling

### Buggy Code
```python
def read_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)
```

### Issue
No handling for missing file or invalid JSON.

### Fixed Code
```python
def read_config(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {path}: {e}")
```

---

## Bug 03 — High Complexity

### Buggy Code
```python
def process(value):
    if value > 100:
        if value > 500:
            if value > 1000:
                return "huge"
            return "large"
        return "medium"
    return "small"
```

### Issue
Deep nesting, magic numbers.

### Fixed Code
```python
THRESHOLDS = [(1000, "huge"), (500, "large"), (100, "medium")]

def process(value: int) -> str:
    for threshold, label in THRESHOLDS:
        if value > threshold:
            return label
    return "small"
```

---

## Bug 04 — Poor Naming

### Buggy Code
```python
def f(x, y):
    z = x * y
    return z + 24
```

### Issue
Unclear names, magic number.

### Fixed Code
```python
TAX_RATE = 24

def calculate_total(price: float, quantity: float) -> float:
    subtotal = price * quantity
    return subtotal + TAX_RATE
```

---

## Bug 05 — Code Duplication

### Buggy Code
```python
def process_order(order):
    if order.total > 100 and order.status == "active":
        discount = order.total * 0.1
    # ... 50 lines ...
    if order.total > 100 and order.status == "active":
        discount = order.total * 0.1
```

### Issue
Same condition repeated multiple times.

### Fixed Code
```python
def calculate_discount(order: Order) -> float:
    if order.total > 100 and order.status == "active":
        return order.total * 0.1
    return 0
```

---

## Bug 06 — No Type Hints

### Buggy Code
```python
def merge(a, b):
    return {**a, **b}
```

### Issue
No type information, unclear what types are expected.

### Fixed Code
```python
def merge(dict_a: dict, dict_b: dict) -> dict:
    return {**dict_a, **dict_b}
```

---

## Bug 07 — Bare Except

### Buggy Code
```python
def fetch_data(url):
    try:
        return requests.get(url)
    except:
        return None
```

### Issue
Bare except catches everything including KeyboardInterrupt.

### Fixed Code
```python
def fetch_data(url: str) -> dict | None:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error("Request failed: %s", e)
        return None
```

---

## Bug 08 — Mutable Default Argument

### Buggy Code
```python
def add_item(item, items=[]):
    items.append(item)
    return items
```

### Issue
Mutable default is shared across calls.

### Fixed Code
```python
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

---

## Bug 09 — Resource Leak

### Buggy Code
```python
def read_lines(path):
    f = open(path)
    lines = f.readlines()
    return lines
```

### Issue
File handle never closed.

### Fixed Code
```python
def read_lines(path: str) -> list[str]:
    with open(path) as f:
        return f.readlines()
```

---

## Bug 10 — SQL Injection

### Buggy Code
```python
def get_user(username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return db.execute(query)
```

### Issue
String formatting in SQL enables injection.

### Fixed Code
```python
def get_user(username: str) -> dict | None:
    query = "SELECT * FROM users WHERE name = %s"
    return db.execute(query, (username,))
```
