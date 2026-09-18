 # Vicious CLI

An AI-powered command-line assistant for Termux/Android, with an optional Kivy GUI control panel and a packaged Android APK build via Buildozer.

## What it does

Vicious CLI is a terminal bridge that sends your prompts to an AI provider (Groq or Gemini) and returns a response, keeping a rolling history of recent exchanges for context. It can run in:

- **One-shot mode** — `vicious "your prompt here"`
- **Interactive loop mode** — just run `vicious` with no arguments

## Features

- Pluggable AI providers: Groq (default, `openai/gpt-oss-120b`) or Gemini, switchable via `config/settings.json` or the GUI
- Persistent conversation history (`config/history.json`), automatically injected into new prompts for context
- Shell command execution with live streaming output and logging
- Context handover file (`vicious_context.md`) that tracks recent session history, auto-truncated to a max length
- Self-update via `vicious update` — pulls the latest `main` branch and reinstalls
- Kivy-based GUI control panel for adjusting provider settings and reviewing history
- Packaged as an Android APK via Buildozer + GitHub Actions CI

## Installation (Termux)

```bash
git clone https://github.com/renaealisha54-debug/Vicious-cli.git ~/vicious-cli
cd ~/vicious-cli
bash install.sh
```

This creates a virtual environment, installs dependencies, and adds a `vicious` command to `~/.local/bin`. Make sure that directory is in your `PATH`.

## Configuration

Edit `config/settings.json` to choose a provider and model:

```json
{
  "provider": "groq",
  "model": "openai/gpt-oss-120b"
}
```

API keys are expected to be available as environment variables for the selected provider.

## Building the Android APK

The project uses [Buildozer](https://github.com/kivy/buildozer) to package the Kivy GUI (`src/gui_main.py`) into an APK. CI is configured in `.github/workflows/build_apk.yml`, using a [patched fork](https://github.com/renaealisha54-debug/buildozer-action-fork) of `ArtemSBulgakov/buildozer-action` to work around upstream base-image issues.

To build locally with Buildozer already installed:

```bash
buildozer android debug
```

## Project structure

```
src/
  main.py             # CLI entry point (one-shot + interactive modes)
  ai_chat.py           # AI provider calls, settings & history persistence
  executor.py           # Shell command execution with streaming output
  context_manager.py    # Session context handover file management
  updater.py             # Self-update via git pull + reinstall
  gui_main.py             # Kivy GUI control panel
  logger.py                # Logging setup
config/
  settings.json         # Active provider/model
  paths.json            # Local path references
install.sh               # Sets up venv, dependencies, and the `vicious` binary
buildozer.spec            # Android packaging configuration
```

## License

MIT — see [LICENSE](./LICENSE).
