import json
import os

from youtube_transcript_api import YouTubeTranscriptApi


def get_arabic_transcript(ytt_api: YouTubeTranscriptApi, video_id: str) -> str | None:
    """Fetches the Arabic transcript for a given YouTube video ID."""
    try:
        transcript = ytt_api.fetch(video_id, languages=["ar"])
        raw_transcript = transcript.to_raw_data()
        final_transcript = ""
        for segment in raw_transcript:
            text = segment["text"].strip()
            if text:
                final_transcript += " " + text

        return final_transcript

    except Exception as e:
        print(f"Error accessing {video_id}: {e}")
        return None


def append_to_jsonl(video_id: str, transcript: str) -> None:
    """Appends a new entry to the dataset JSONL file."""
    entry = {"video_id": video_id, "transcript": transcript}

    os.makedirs("data", exist_ok=True)

    with open("data/dataset.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def is_duplicate(video_id: str, file_path: str = "data/dataset.jsonl") -> bool:
    """Checks if a video ID already exists in the dataset."""
    search_string = f'"video_id": "{video_id}"'

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if search_string in line:
                    return True
    except FileNotFoundError:
        return False

    return False


if __name__ == "__main__":
    video_id = "l9Rp6-YoXIs"

    if is_duplicate(video_id):
        print("Video already exists in the dataset.")
        exit()

    ytt_api = YouTubeTranscriptApi()
    fetched_transcript = get_arabic_transcript(ytt_api, video_id)

    if fetched_transcript:
        append_to_jsonl(video_id, fetched_transcript)
    else:
        print(f"No Arabic transcript found for video ID: {video_id}")
