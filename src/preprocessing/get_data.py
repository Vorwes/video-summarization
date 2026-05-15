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
