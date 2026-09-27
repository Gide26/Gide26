# 11 · Setup: Python & API Keys

> **Time:** 30 minutes
> **You'll need:** a computer, internet, and about $1 of credit
> **You'll learn:** install Python packages, create an API key safely, set a spending cap

Up to now you've used AI through a website. Now you'll use it **from code** — which means you can build things the chat window can't do.

---

## Why bother with the API?

| Chat interface | API |
|---|---|
| You type, it replies | Your code calls it inside a program |
| One conversation at a time | Process hundreds of inputs automatically |
| Manual, every time | Runs while you sleep |
| Can't touch your files or systems | Can read your data, write output, trigger actions |

**The API is the difference between using AI and building with AI.**

You also pay only for what you use — typically fractions of a cent per call. Working through all of Part 3 costs **well under a dollar** if you follow the cheap-model advice in Module 12.

---

## Step 1: Check Python

Open a terminal (Terminal on Mac/Linux, PowerShell or Command Prompt on Windows).

```bash
python3 --version
```

You want **3.9 or newer**. If you get an error or a version starting with 2:

- **Mac:** `brew install python3`, or download from python.org
- **Windows:** download from [python.org](https://www.python.org/downloads/) — **tick "Add Python to PATH"** during install
- **Linux:** `sudo apt install python3 python3-pip`

---

## Step 2: Create a project folder

```bash
mkdir ai-course
cd ai-course
```

### Create a virtual environment

A virtual environment keeps this project's packages separate from everything else on your computer. Do it once per project — it prevents a whole category of confusing breakage.

```bash
# Create it
python3 -m venv .venv

# Activate it — Mac/Linux
source .venv/bin/activate

# Activate it — Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Activate it — Windows (Command Prompt)
.venv\Scripts\activate.bat
```

You'll know it worked because your prompt shows `(.venv)`.

> **You must re-activate this every time you open a new terminal.** If things suddenly can't find packages, check for `(.venv)` first.

---

## Step 3: Install the SDK

This course uses **Anthropic's Claude API** for the main examples.

```bash
pip install anthropic
```

Also install this — you'll want it from Module 12 onward:

```bash
pip install python-dotenv
```

Verify:

```bash
python3 -c "import anthropic; print(anthropic.__version__)"
```

If that prints a version number, you're set.

---

## Step 4: Get an API key

1. Go to [platform.claude.com](https://platform.claude.com/) and create an account
2. Add a payment method and **buy a small amount of credit — $5 is plenty**
3. Go to **API keys** and create a new key
4. **Copy it immediately.** It looks like `sk-ant-...` and you won't see it again.

> ### 🔴 Treat this key like a password
>
> Anyone with your key can spend your money. Never:
>
> - ❌ Paste it into your code
> - ❌ Commit it to Git
> - ❌ Share it in a screenshot
> - ❌ Put it in a public repo, a Discord message, or a pastebin
>
> If it leaks, **delete it in the dashboard immediately** and create a new one. Revoking takes seconds.

---

## Step 5: 🔴 Set a spending limit (do this now)

**Before your first API call, cap your spending.** This is the step people skip and regret.

In your account dashboard, find **billing / limits** and set:

- A **monthly spend limit** — start with **$5**
- Enable **usage notifications** if offered

Now the worst case for any bug in this course is $5, not $500.

---

## Step 6: Store the key safely

We'll keep the key in a `.env` file that **never gets committed to Git.**

### Create `.env`

In your project folder, create a file called `.env` containing exactly one line:

```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Create `.gitignore`

Critical step. Create a file called `.gitignore`:

```
.env
.venv/
__pycache__/
*.pyc
```

This tells Git to ignore your key. **Check this is in place before you ever commit anything.**

### Make sure it's ignored

```bash
git init
git add .
git status
```

**`.env` must not appear in the list.** If it does, stop — remove it with `git rm --cached .env` and check your `.gitignore` before going further.

---

## Step 7: Test the connection

Create a file called `test_setup.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env and puts values into environment variables

key = os.getenv("ANTHROPIC_API_KEY")

if not key:
    print("❌ No key found. Check your .env file.")
elif key.startswith("sk-ant-"):
    print("✅ Key loaded successfully.")
    print(f"   Key starts with: {key[:12]}...")
else:
    print("⚠️  Key found but doesn't look right. It should start with 'sk-ant-'")
```

Run it:

```bash
python3 test_setup.py
```

You should see `✅ Key loaded successfully.`

**If it fails:**

| Symptom | Fix |
|---|---|
| `No key found` | `.env` is in the wrong folder — it must be next to your script. Or check for extra spaces around the `=`. |
| `No module named dotenv` | Virtual environment isn't activated, or run `pip install python-dotenv` |
| Key doesn't start with `sk-ant-` | You copied something else — recreate the key |

---

## A quick terminal orientation

If the terminal is new to you, these five commands cover 95% of what you need:

```bash
pwd              # where am I? (print working directory)
ls               # what's in this folder?
cd foldername    # go into a folder
cd ..            # go back up one level
python3 file.py  # run a Python file
```

Plus two that save time:

```bash
# Up arrow — previous command
# Tab       — autocomplete file and folder names
```

---

## Project layout

Your folder should now look like:

```
ai-course/
├── .venv/              # virtual environment (ignored by git)
├── .env                # your API key (ignored by git)
├── .gitignore          # tells git what to ignore
└── test_setup.py       # connection test
```

Clean and safe.

---

## ✏️ Exercise 11.1 — Get set up (20 min)

Work through all seven steps. Don't move on until:

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] `anthropic` and `python-dotenv` installed
- [ ] API key created and saved in `.env`
- [ ] **Spending cap set** (non-negotiable)
- [ ] `.gitignore` includes `.env`
- [ ] `git status` does **not** show `.env`
- [ ] `test_setup.py` prints the success message

---

## ✏️ Exercise 11.2 — Read your own setup (5 min)

Ask your AI assistant:

```
I'm a beginner setting up Python for API work. Here's my
project structure:

[Paste the output of `ls -a`]

1. Is anything here a security risk?
2. Is anything missing that I'll regret later?
3. Explain what each file does in one line.
```

Good practice for using AI to check your work — and it catches real mistakes.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `pip: command not found` | Use `python3 -m pip install anthropic` |
| `Permission denied` | Don't use `sudo` with pip. Use a virtual environment. |
| SSL / certificate errors | `pip install --upgrade certifi` |
| Very slow install | Normal on first install. Wait it out. |
| `ModuleNotFoundError` | Virtual environment not activated — look for `(.venv)` in your prompt |

---

## Key takeaways

- ✅ The API lets you **build with** AI instead of just using it
- ✅ **Virtual environments** isolate packages — activate with `source .venv/bin/activate`
- ✅ Your API key is a **password** — `.env` + `.gitignore`, always
- ✅ **Set a spending cap before your first call**
- ✅ `load_dotenv()` reads `.env` into environment variables

---

**Next: [12 · Your First API Call](./12-first-api-call.md)**
