import json
import re
from collections import Counter
from typing import Dict, List, Tuple

import torch
from camel_tools.utils.dediac import dediac_ar
from transformers import pipeline


class ArabicTranscriptProcessor:
    """A comprehensive processor for Arabic transcripts that performs deep normalization, robust dialect identification, and generates LLM system prompts based on detected dialects."""

    def __init__(self, device: int | None = None):
        if device is None:
            device = 0 if torch.cuda.is_available() else -1

        model_name = "CAMeL-Lab/bert-base-arabic-camelbert-mix-did-madar-corpus26"

        self.did_pipeline = pipeline(
            "text-classification", model=model_name, device=device
        )

        self.dialect_map = {
            "Amman": "Jordanian/Levantine",
            "Beirut": "Lebanese/Levantine",
            "Damascus": "Syrian/Levantine",
            "Jerusalem": "Palestinian/Levantine",
            "Riyadh": "Saudi/Gulf",
            "Doha": "Qatari/Gulf",
            "Cairo": "Egyptian",
            "Alexandria": "Egyptian",
            "Tunis": "Tunisian/Maghrebi",
            "Algiers": "Algerian/Maghrebi",
            "Rabat": "Moroccan/Maghrebi",
            "Baghdad": "Iraqi",
        }

    def deep_normalize_text(self, text: str) -> str:
        """Performs deep normalization on Arabic text, including URL and mention removal, diacritic stripping, character normalization, and reduction of repeated characters."""
        content = re.sub(r"http\S+|www.\S+|@\w+", "", text)
        content = re.sub(r"\[.*?\]|\(.*?\)", "", content)
        content = dediac_ar(content)

        content = re.sub(r"[ـ]+", "", content)
        content = re.sub(r"[^\w\s\u0600-\u06FF]", " ", content)

        content = re.sub(r"(.)\1{2,}", r"\1", content)

        content = re.sub(r"\b(\w+)(?:\s+\1\b)+", r"\1", content)
        content = re.sub(r"([a-zA-Z]+)", r" \1 ", content)
        content = re.sub(r"\s+", " ", content).strip()
        content = content.replace("<<", "")

        return content

    def identify_robust_dialect(
        self, text: str, chunk_word_size: int = 300
    ) -> Tuple[str, float]:
        """Identifies the Arabic dialect of the given text by splitting it into manageable chunks, classifying each chunk, and then aggregating the results to determine the most likely dialect and its confidence score."""
        words = text.split()
        if not words:
            return "Unknown", 0.0

        chunks = [
            " ".join(words[i : i + chunk_word_size])
            for i in range(0, len(words), chunk_word_size)
        ]

        predictions = self.did_pipeline(chunks, truncation=True, max_length=512)

        labels = [pred["label"] for pred in predictions]
        most_common_label = Counter(labels).most_common(1)[0][0]

        winning_scores = [
            pred["score"] for pred in predictions if pred["label"] == most_common_label
        ]
        avg_confidence = sum(winning_scores) / len(winning_scores)

        return most_common_label, avg_confidence

    def get_llm_system_prompt(self, raw_label: str) -> str:
        """Generates an LLM system prompt based on the detected dialect."""
        mapped_dialect = self.dialect_map.get(raw_label, "Arabic")
        return (
            f"You are an expert Arabic linguist. The following transcript is spoken in the "
            f"{mapped_dialect} dialect. Summarize the core points into Modern Standard Arabic."
        )

    def clean_transcript(self, transcript_segments: List[str]) -> Dict:
        """Cleans and processes the transcript segments by performing deep normalization, identifying the dialect, and preparing the data for LLM summarization."""
        if not transcript_segments:
            return {
                "processed_text": "",
                "detected_dialect": "Unknown",
                "system_prompt": self.get_llm_system_prompt("Unknown"),
                "confidence": 0.0,
                "word_count": 0,
            }

        full_text = " ".join(transcript_segments)

        normalized_text = self.deep_normalize_text(full_text)
        dialect_label, confidence = self.identify_robust_dialect(normalized_text)
        word_count = len(normalized_text.split())

        return {
            "processed_text": normalized_text,
            "detected_dialect": dialect_label,
            "system_prompt": self.get_llm_system_prompt(dialect_label),
            "confidence": round(confidence, 4),
            "word_count": word_count,
        }

    def process_jsonl(self, input_path: str, output_path: str, text_key: str = "text"):
        """Processes a JSONL file containing Arabic transcripts, applying the cleaning and dialect identification pipeline to each record, and writes the results to a new JSONL file."""
        with (
            open(input_path, "r", encoding="utf-8") as infile,
            open(output_path, "w", encoding="utf-8") as outfile,
        ):
            for line in infile:
                if not line.strip():
                    continue

                record = json.loads(line)
                raw_data = record.get(text_key, "")

                if isinstance(raw_data, str):
                    segments = [raw_data]
                elif isinstance(raw_data, list):
                    segments = [
                        seg["text"]
                        if isinstance(seg, dict) and "text" in seg
                        else str(seg)
                        for seg in raw_data
                    ]
                else:
                    segments = []

                processed_data = self.clean_transcript(segments)

                new_record = {"video_id": record.get("video_id", "UNKNOWN_ID")}
                new_record.update(processed_data)

                outfile.write(json.dumps(new_record, ensure_ascii=False) + "\n")
