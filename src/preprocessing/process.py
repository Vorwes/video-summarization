import json
import re
from camel_tools.utils.dediac import dediac_ar

def deep_normalize_text(text: str) -> str:
    """Performs deep normalization on Arabic text."""
    if not isinstance(text, str):
        return ""
        
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
    content = content.replace(">>", "")
    
    return content

def process_transcripts_jsonl(input_file: str, output_file: str):
    """
    Reads a JSONL file, normalizes the 'transcript' field, 
    and saves it to a new JSONL file with an incremental ID.
    """
    count = 0
    try:
        # Open both files simultaneously: one to read, one to write
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line in infile:
                # Skip empty lines
                if not line.strip():
                    continue
                    
                # Parse the current line as a JSON object
                record = json.loads(line)
                
                # Extract your specific fields
                transcript = record.get("transcript", "")
                video_id = record.get("video_id", "UNKNOWN")
                
                # Clean the transcript
                cleaned_text = deep_normalize_text(transcript)
                
                # Create the new record format
                new_record = {
                    "id": count,
                    "video_id": video_id,
                    "normalized_transcript": cleaned_text
                }
                
                # Write the new dictionary as a JSON string and add a newline
                outfile.write(json.dumps(new_record, ensure_ascii=False) + "\n")
                count += 1
                
        print(f"Successfully processed {count} records and saved to '{output_file}'.")
        
    except FileNotFoundError:
        print(f"Error: Could not find '{input_file}'. Make sure it is in the same folder.")
    except json.JSONDecodeError:
        print(f"Error: Failed to parse a line in '{input_file}'. Ensure it is valid JSONL.")

if __name__ == "__main__":
    
    process_transcripts_jsonl("../data/dataset.jsonl", "../data/normalized_output.jsonl")