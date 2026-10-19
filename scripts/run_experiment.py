import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client = OpenAI(
    api_key=os.getenv("NEBULA_API_KEY"),
    base_url=os.getenv("NEBULA_BASE_URL"),
)
model = os.getenv("NEBULA_MODEL")
transcriptsfold = Path("transcripts")
promptsfold = Path("prompts")
outputsfold = Path("outputs")
outputsfold.mkdir(exist_ok=True)
prompt_files = {
    "zero-shot": promptsfold / "zs.txt",
    "zero-thought chain of thought": promptsfold / "zs-cot.txt",
    "few-shot": promptsfold / "fs.txt",
    "few-shot chain of thought": promptsfold / "fs-cot.txt",
}

for prompt_name, prompt_path in prompt_files.items():
    prompt_text = prompt_path.read_text(encoding="utf-8")
    for transcript_file in transcriptsfold.glob("*.txt"):
        transcript = transcript_file.read_text(encoding="cp1252")
        messages = [
            {"role": "system", "content": "You are a clinical functional-status extraction system. return only structured JSON."},
            {"role": "user", "content": f"{prompt_text}\n\nTranscript:\n{transcript}"}
        ]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )
        firstone = response.choices[0]
        message = firstone.message
        content = message.content
        out_file = outputsfold / f"{transcript_file.stem}_{prompt_name}.json"
        out_file.write_text(content, encoding="utf-8")
        print(f"ok: {out_file}")
        