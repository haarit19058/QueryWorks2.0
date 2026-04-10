Yeah — your current function is using **wrong field names** (like `"problem"`), while your dataset actually uses `"description"` and others.

Let’s fix it properly based on your schema.

---

## ✅ Correct Column Mapping

From your dataset:

| Your Code         | Actual Column   |
| ----------------- | --------------- |
| `problem` ❌       | `description` ✅ |
| `title` ✅         | `title`         |
| `time_limit` ✅    | `time_limit`    |
| `memory_limit` ✅  | `memory_limit`  |
| `input_format` ✅  | `input_format`  |
| `output_format` ✅ | `output_format` |
| `examples` ✅      | `examples`      |

---

## 🔧 Fixed & Clean Version

Here’s the corrected function:

````python
def build_prompt(example):
    prompt = f"""You are an expert competitive programmer.

Solve the problem below.

Rules:
- Use <think>...</think> for reasoning
- Then output ONLY final code
- Must read stdin / write stdout

Title: {example.get("title", "")}
Contest: {example.get("contest_name", "")}
Time limit: {example.get("time_limit", "")} sec
Memory: {example.get("memory_limit", "")} MB

Problem:
{example.get("description", "")}

Input:
{example.get("input_format", "")}

Output:
{example.get("output_format", "")}

Examples:
{format_examples(example.get("examples", []))}

Notes:
{example.get("note", "")}

Final format:
<think>...</think>
```cpp
// code
````

"""
return {"prompt": prompt}

````

---

## 🧠 Improvements I Added (Important)

- ✅ Fixed `problem → description`
- ✅ Added `contest_name` (useful context for model)
- ✅ Added `note` (CF problems often hide constraints there)
- ✅ Kept `.get()` safe defaults
- ✅ Clean formatting for LLM parsing

---

## ⚠️ Optional (but HIGHLY recommended)

If you're training or prompting a model like DeepSeek / Code LLM:

### 1. Remove `<think>` (for inference)
Many models:
- either ignore it
- or leak reasoning into output

Better alternative:

```text
Think step by step, but do not include reasoning in output.
````

---

### 2. Stronger Output Constraint

Replace:

```
- Then output ONLY final code
```

with:

````
- Output ONLY C++ code inside ```cpp```
- No explanations, no comments outside code
````

---

### 3. Example Formatter (if broken)

Make sure `format_examples` is structured like:

```python
def format_examples(examples):
    out = ""
    for ex in examples:
        inp = ex.get("input", "").strip()
        outp = ex.get("output", "").strip()
        out += f"Input:\n{inp}\nOutput:\n{outp}\n\n"
    return out
```

---

## 🚀 Final Thought

Your dataset already contains a `"prompt"` column — so check:

* If it's already well-structured → reuse it
* Otherwise → your custom prompt (above) is **better for reasoning models**

---

If you want next step, I can help you:

* optimize prompt for **multi-GPU inference**
* or convert this into **chat format (messages column)** for better performance with modern LLMs
