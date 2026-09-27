# Resources

Official documentation, tools worth knowing, and where to go next.

> **Check dates.** AI documentation changes fast. If a link is dead, search for the page title — it almost certainly moved rather than disappeared.

---

## Official documentation

The only sources you should trust for model names, prices, and API shapes.

| Provider | Docs |
|---|---|
| **Anthropic (Claude)** | [platform.claude.com/docs](https://platform.claude.com/docs/en/get-started) |
| └ Model list & pricing | [Models overview](https://platform.claude.com/docs/en/models/overview) |
| └ Prompting best practices | [Prompting guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) |
| └ Structured outputs | [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) |
| **OpenAI** | [developers.openai.com](https://developers.openai.com/api/docs/models) |
| └ Text generation | [Text guide](https://developers.openai.com/api/docs/guides/text) |
| └ Prompting | [Prompting guide](https://developers.openai.com/api/docs/guides/prompting) |
| **Google (Gemini)** | [ai.google.dev](https://ai.google.dev/gemini-api/docs/models) |

**Why official docs matter:** most AI comparison sites are SEO content farms with outdated or invented model names. While researching this course I found multiple sites confidently listing models that don't exist. **Go to the source.**

---

## Chat assistants

| Tool | Link | Best for |
|---|---|---|
| ChatGPT | [chatgpt.com](https://chatgpt.com/) | All-round, largest ecosystem |
| Claude | [claude.ai](https://claude.ai/) | Writing, long documents, coding |
| Gemini | [gemini.google.com](https://gemini.google.com/) | Google Workspace, large context |
| Perplexity | [perplexity.ai](https://www.perplexity.ai/) | Research with citations |
| Grok | [x.ai](https://x.ai/) | Real-time X context |
| Copilot | [copilot.microsoft.com](https://copilot.microsoft.com/) | Microsoft 365 |

---

## Developer tools

### SDKs
- [Anthropic Python SDK](https://platform.claude.com/docs/en/cli-sdks-libraries/overview)
- [OpenAI Python SDK](https://developers.openai.com/api/docs/libraries)

### Building UIs
- [Streamlit](https://streamlit.io/) — the fastest way to put a Python script on the web
- [Gradio](https://www.gradio.app/) — simple ML/AI interfaces, great for demos

### Embeddings and vector search
- [Gemini Embedding](https://ai.google.dev/gemini-api/docs/models) — includes a multimodal embedding model
- [OpenAI Embeddings](https://developers.openai.com/api/docs/guides/embeddings)
- [Chroma](https://www.trychroma.com/) — easiest vector database to start with
- [Qdrant](https://qdrant.tech/) — solid production option
- [pgvector](https://github.com/pgvector/pgvector) — if you already use Postgres

### Running models locally
- [Ollama](https://ollama.com/) — simplest local setup
- [LM Studio](https://lmstudio.ai/) — friendly GUI
- [Hugging Face](https://huggingface.co/) — the open-model ecosystem

### Terminal output
- [Rich](https://github.com/Textualize/rich) — markdown, tables, and syntax highlighting in the terminal

---

## Python packages used in this course

```bash
pip install anthropic      # Claude API
pip install openai         # OpenAI API
pip install python-dotenv  # load .env files
pip install pydantic       # structured output + validation
pip install pandas         # data analysis
pip install matplotlib     # charts
pip install pypdf          # read PDFs (Project 1)
pip install rich           # pretty terminal output
```

---

## Learning more

### Prompting
Start with the official guides linked above — they're better than most third-party content, and free.

### Courses worth taking
- [DeepLearning.AI](https://www.deeplearning.ai/) — short, practical courses
- [Anthropic's courses](https://www.anthropic.com/learn) — free
- [Google's Generative AI pathway](https://ai.google.dev/) — free

### Staying current
The field moves monthly. Reliable habits:

- **Follow official provider blogs** for releases
- **Check official pricing pages** before budgeting — never a third-party calculator
- **Treat anything unverified as possibly wrong**, including model names in tutorials

---

## Where to go next

### If you want to build agents
Systems that use tools and take multi-step actions.
- Anthropic: [Build with Claude](https://platform.claude.com/docs/en/build-with-claude/overview)
- OpenAI: [Agents](https://developers.openai.com/api/docs/agents)

### If you want production reliability
- Prompt caching (big cost savings on repeated prefixes)
- Retries with exponential backoff
- **Evals** — you cannot improve what you don't measure
- Monitoring cost and latency per request

### If you care about multimodal
- [Gemini media models](https://ai.google.dev/gemini-api/docs/models) — image (Nano Banana), video (Veo), music (Lyria), TTS
- [OpenAI audio & voice](https://developers.openai.com/api/docs/guides/audio)

### If you care about privacy
- Ollama or LM Studio for local models
- Check provider data-retention and training policies before sending anything sensitive

---

## Community

- [Anthropic Discord](https://www.anthropic.com/discord)
- [OpenAI Community Forum](https://community.openai.com/)
- [Google AI Developers Forum](https://discuss.ai.google.dev/)
- r/LocalLLaMA — for running models yourself

---

## Contributing to this course

Found something wrong, unclear, or out of date?

**Beginner corrections are the most valuable kind** — you remember exactly what was confusing. [Open an issue](https://github.com/Gide26/Gide26/issues) or send a pull request.

---

**[← Back to the syllabus](./README.md)**
