# DailyNewsBot V2.0 - Sovereign Automation Stack

An automated, AI-powered system that gathers daily news, summarizes it using Gemini 1.5 Pro, and creates a video briefing. Designed for "Sovereign Automation" using n8n and Google Antigravity.

## Features
-   **Multi-Source Fetching**: NewsAPI, GNews, Google News RSS, and local scraping.
-   **AI Analysis**: Gemini 1.5 Pro filters for importance and generates "Intelligence Reports".
-   **Rich Media**: Automatically generates a `daily_briefing.mp4` video with voiceover.
-   **Sovereign Control**: Orchestrated by n8n (locally hosted) via MCP.
-   **Mobile Trigger**: Run from your phone via n8n Webhook.

## Quick Start (The "Instant" Method)

1.  **Start the Engine**
    Double-click `START_BOT.bat`. 
    *   This will automatically download and start n8n.
    *   It will display a **Tunnel URL** (e.g., `https://xxxx.hooks.n8n.cloud`).

2.  **Connect the Brain (One-time Setup)**
    *   Open `http://localhost:5678` in your browser.
    *   Get your API Key (Settings -> Public API).
    *   Run `python setup_mcp.py` and paste the key.
    *   Import `n8n_workflow.json` into n8n.

3.  **Run It**
    *   Click the Webhook URL (from your phone or browser).
    *   Receive your Video Briefing via Email!

## File Structure
*   `START_BOT.bat`: The main launcher.
*   `bot_core.py`: Core Python logic.
*   `video_generator.py`: Creates the video content.
*   `n8n_workflow.json`: The automation logic for n8n.
*   `.env`: Configuration secrets.

## Requirements
*   Python 3.10+
*   Node.js (for n8n)
*   Google One AI Premium (for Gemini usage)
