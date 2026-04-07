---
title: AI Food Safety Transparency
emoji: 🍔
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
app_port: 7860
---

# 🛡️ Obsidian Sentinel: AI Food Safety Dashboard

Welcome to the **Obsidian Sentinel** project! This repository contains a production-ready, **OpenEnv-compatible** reinforcement learning (RL) environment that simulates restaurant food safety communication and risk management. 

This project was built for the OpenEnv Hackathon Round 1, modeling the critical decision-making process of an AI safety officer protecting public health.

---

## 🌟 Project Overview

The **Obsidian Sentinel** environment tasks an AI agent with deciding how to display food safety information to users. The agent analyzes signals like hygiene scores, inspection age, and consumer complaints to take appropriate actions (e.g., showing safety badges, flagging risks, or requesting new inspections). 

The goal? **Maximize global user trust while minimizing public health risks.**

### Key Features
- **OpenEnv Spec Compliance**: Fully implements the `step()`, `reset()`, and `state()` API using strictly typed Pydantic models for Observations, Actions, and Rewards.
- **Dynamic Frontend Dashboard**: A custom-designed UI (HTML/CSS/JS) served via FastAPI that visualizes the current simulated restaurant state in real-time.
- **Tiered Reward System**: Meaningful partial-progress signals (`1.0` Optimal, `0.7` Reasonable, `0.0` Dangerous) that heavily penalize misleading or dangerous actions.
- **"Hidden Risk" Mechanics**: Advanced scenarios where an agent must proactively request inspections to uncover hidden hygiene hazards before flagging a venue.
- **Baseline LLM Agent**: Includes an `inference.py` script to run evaluation tasks sequentially using OpenAI's models.

---

## 💻 Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic (Strong typing)
- **Frontend**: Vanilla HTML5, CSS3, JavaScript
- **AI Integration**: OpenAI Python Client (`openai`)
- **Deployment**: Docker, Hugging Face Spaces

---

## 📊 Environment Specification

### Observation Space
The state is a dictionary containing the `restaurant` object with the following features:
- `hygiene_score`: 0.0 - 100.0 (inspection result)
- `inspection_age_days`: Age of the data
- `complaints_count`: Recent consumer safety complaints
- `verification_status`: `verified`, `pending`, or `suspended`
- `badge_visible` / `flagged`: Current UI state
- `user_trust`: Global platform trust metric (0.0 - 100.0)

### Action Space (Discrete)
- `show_safety_badge`: Promotes the restaurant (highly rewarded if safe, heavily penalized if risky).
- `hide_info`: Removes visibility of safety metrics (cautious/neutral).
- `request_inspection`: Initiates a new health inspection (reveals hidden risks).
- `flag_restaurant`: Publicly marks the restaurant as high-risk.

### Graded Tasks (Difficulty)
1. **Easy**: Clear high-scoring restaurant. Goal: `show_safety_badge`.
2. **Medium**: Stale data with complaints. Goal: `request_inspection` before acting.
3. **Hard**: Low hygiene but "verified" status. Goal: `request_inspection` to reveal the trap, then `flag_restaurant`.

---

## 🚀 Getting Started (Local Development)

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Clone and Setup
```bash
git clone https://github.com/yourusername/obsidian-sentinel-openenv.git
cd obsidian-sentinel-openenv

# create a virtual environment (optional but recommended)
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Dashboard locally
Because the project uses a modular `server/` structure, you need to configure your Python path before running the server:

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH=(Get-Location).Path
python server/app.py
```

**Mac/Linux:**
```bash
PYTHONPATH=$(pwd) python server/app.py
```
*The dashboard will be available at [http://localhost:7860](http://localhost:7860).*

---

## 🤖 Running the Baseline AI Agent

To evaluate the environment using the baseline LLM script, you must provide your OpenAI API credentials.

**DO NOT hardcode your API keys.** Set them securely via environment variables:

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-actual-api-key"
$env:PYTHONPATH=(Get-Location).Path
python scripts/inference.py
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY="sk-your-actual-api-key"
PYTHONPATH=$(pwd) python scripts/inference.py
```

---

## 🐳 Docker Support

To build and run the container locally:

```bash
docker build -t obsidian-sentinel .
docker run -p 7860:7860 obsidian-sentinel
```

---

## ☁️ Hugging Face Deployment

This project is configured for one-click deployment to Hugging Face Spaces (Docker SDK).

1. Ensure your `README.md` contains the required YAML frontmatter (already included).
2. Set your secrets in the Hugging Face repository settings if required by your scripts.
3. The included `scripts/huggingface_deploy.py` can be used to programmatically update the Space with your local changes.
