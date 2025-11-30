---
title: codeGreen
emoji: 🌱
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# codeGreen Demo

A proof-of-concept visualization of the GreenCode PyCharm plugin functionality.

## Features

- **Static Analysis**: Instant code efficiency scoring using `eco-code-analyzer`
- **Runtime Analysis**: Carbon emissions measurement during code execution using `codecarbon`
- **Issue Detection**: Highlights inefficient code patterns with line numbers

## Usage

1. Click "Load Dummy Code" to load an example inefficient Python script
2. Click "Analyze Code" for instant static analysis scoring
3. Click "Run & Measure" to execute the code and measure actual carbon emissions

## Tech Stack

- FastAPI backend
- Vanilla HTML/CSS/JS frontend
- eco-code-analyzer for static analysis
- codecarbon for runtime emissions tracking
