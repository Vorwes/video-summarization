# Arabic Video Summarization
### This repository contains a complete pipeline for extracting, processing, and summarizing Arabic YouTube video transcripts. It converts multiple Arabic dialects into concise Modern Standard Arabic (MSA) summaries using a fine-tuned Large Language Model.

## Features
- Data Extraction: Automated fetching of Arabic transcripts using the YouTube Transcript API.
- Text Normalization: Deep cleaning of Arabic text, including dediacritization and noise removal via camel_tools.
- Model Fine-Tuning: Parameter-Efficient Fine-Tuning (QLoRA) of google/gemma-4-E4B-it for targeted instruction following. '
- Evaluation: Automated scoring of generated summaries against gold standards using Arabic BERTScore.

## Installation
```bash
# clone the repository
git clone git@github.com:Vorwes/video-summarization.git

# install dependencies
uv sync
```
## Project Structure and Usage
1. Fetches raw transcripts from YouTube based on a predefined configuration.
```bash
uv run python -m get_data.py
```
- Input: data/videos/cleaned_urls.yaml 
- Output: data/dataset.jsonl 

2. Preprocessing
- Normalizes the raw transcripts by removing URLs, brackets, special characters, and diacritics.
```bash
uv run python -m preprocess.py
```
- Input: data/dataset.jsonl 
- Output: data/normalized_output.jsonl

3. Model Fine-Tuning
- Fine-tunes the LLM to generate 5-line MSA bullet-point summaries and evaluates the performance on a held-out test set.
- Environment: Optimized for execution on cloud-based GPU instances (e.g., Lightning AI).
- Input: data/normalized_output.jsonl (transcripts) and data/summarized_last.jsonl (gold standard summaries)
- Output: Fine-tuned adapter weights saved to ./final_summary_adapters2 and BERTScore evaluation metrics printed to the console.
