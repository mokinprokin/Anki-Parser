# ⚡ Anki Clipboard Agent (`anki_parser`)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Managed by uv](https://img.shields.io/badge/managed%20by-uv-261230?style=flat-square&logo=astral&logoColor=white)](https://astral.sh/uv)
[![Anki](https://img.shields.io/badge/AnkiConnect-Integrated-007acc?style=flat-square)](https://apps.ankiweb.net/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)

An autonomous, ultra-fast background clipboard daemon that instantly parses LLM-generated vocabulary cards and pushes them directly into your local **[Anki](https://apps.ankiweb.net/)** decks via [AnkiConnect](https://git.sr.ht/~foosoft/anki-connect).

**Zero UI. Zero Manual File Imports. Zero Context-Switching.** Just hit `Ctrl+C` on your AI output, and your flashcards are in Anki.

---

## 🚀 Instant Run (Zero Installation, No `git clone`)

You **do not need to clone this repository**, create virtual environments, or run `pip install`. 

Thanks to **[`uv`](https://docs.astral.sh/uv/)**, you can run the agent straight from GitHub in a single command:

```powershell
uvx --from git+https://github.com/mokinprokin/Anki-Parser.git anki_parser
```

🔄 How the Workflow Looks
```markdown
[ AI Output (ChatGPT / Claude / LM Studio) ]
                  │
                  ▼ (User hits Ctrl + C)
       [ OS System Clipboard ]
                  │
                  ▼ (Detected)
    [ anki_parser Daemon (Background) ]
                  │
         ┌────────┴────────┐
         ▼                 ▼
[ In-Memory Cache ]   [ AnkiConnect API ]
(Skip Duplicates)      (Push to Target Deck)
                  │
                  ▼
 [ Windows 11 Native Toast Notification 🔔 ]
```

1.  You ask an AI to generate vocabulary using our strict delimiter format.
2.  You select the output and press Ctrl + C.
3.  The background daemon scans the clipboard, filters out non-card text in
    microseconds, checks for duplicates, and creates notes in Anki.
4.  A native Windows toast notification with sound confirms:
    "Saved: 3 | Duplicates skipped: 1".
5.  The clipboard is automatically cleared.



## 🧠 LLM System Prompt Protocol

Give this prompt to ChatGPT, Claude, LM Studio, or local models:

### Formatting Protocol for Automated Anki Parsing
Whenever you generate vocabulary cards, format them STRICTLY using these delimiters:
```markdown
===DECK: [Deck Name if specified, e.g. English]===
===FRONT===
[Definition, fill-in-the-blank examples, or collocations without the target word]
===BACK===
[Target word/phrase accompanied by phonetic transcription or translation]
===END===
```
📖 Full System Prompt: You can find the complete, battle-tested agent prompt with
multi-scenario rules (single words, phrases, synonym clusters) and few-shot
examples in [`instruction.md`](instruction.md).


🛠️ Features

  - ⚡ Zero-Clone Execution: Run anywhere with uvx --from git+....
  - 🛡️ Built-in Deduplication Cache: On startup, the agent warms up an in-memory
    cache of all existing card backings across all decks. It will never create
    duplicate cards.
  - 🧹 Clean Text Pipeline: Strips Angular attributes, CSS bloat, and raw HTML
    tags before storage.
  - 🔔 Native Windows Toasts & Audio: Uses win11toast via WinRT with fallback
    sound cues and custom icons.
  - 🗂️ Dynamic Deck Routing: Automatically targets decks specified in ===DECK:
    ...=== (falls back to .env default).
  - 🔕 Silent Background Mode: Can be registered to run invisibly on Windows boot
    via pythonw.exe and startup scripts.

📋 Prerequisites

1.  Anki Desktop: Must be running on your machine.
2.  AnkiConnect Plugin:
      - Open Anki \rightarrow Tools \rightarrow Add-ons \rightarrow Get
        Add-ons...
      - Enter code: 2055492159
      - Restart Anki (runs on http://127.0.0.1:8765).
3.  uv: The fast Python package manager.

⚙️ Local Development (Optional)

If you prefer to clone and customize the code locally:

# 1. Clone repository
git clone https://github.com/mokinprokin/AnkiParser.git
cd AnkiParser

# 2. Sync dependencies
uv sync

# 3. Run agent locally
uv run anki_parser

Environment Configuration (.env)

You can override defaults by placing a .env file in the root directory:
```
ANKI_CONNECT_URL=http://127.0.0.1:8765
DEFAULT_DECK=English
REQUEST_TIMEOUT=5
```
🪟 Windows Silent Autostart Setup

To make the agent start automatically on Windows boot without opening a terminal
window:

1.  Run the installer:
    uv run anki_parser_install
2.  This creates a silent VBS launcher inside %APPDATA%\Microsoft\Windows\Start
    Menu\Programs\Startup pointing to your virtual environment's pythonw.exe.

📄 License

Distributed under the MIT License.
