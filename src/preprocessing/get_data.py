import json

from youtube_transcript_api import YouTubeTranscriptApi


def get_arabic_transcript(ytt_api: YouTubeTranscriptApi, video_id: str) -> str | None:
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
    entry = {"video_id": video_id, "transcript": transcript}

    with open("dataset.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
