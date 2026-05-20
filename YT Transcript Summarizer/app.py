import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import os
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Prompt
prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here: """

# ─── Extract video ID from different URL formats ───────────────
def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    else:
        raise ValueError("Invalid YouTube URL format.")

# ─── Extract transcript ────────────────────────────────────────
def extract_transcript_details(youtube_video_url):
    video_id = extract_video_id(youtube_video_url)

    try:
        # Try new API (v0.2.0+)
        ytt = YouTubeTranscriptApi()
        fetched = ytt.fetch(video_id)
        transcript = " ".join([snippet.text for snippet in fetched])
        return transcript

    except Exception as e1:
        try:
            # Fallback: old API style
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([i["text"] for i in transcript_list])
            return transcript

        except Exception as e2:
            raise Exception(
                f"Transcript not available for this video.\n\n"
                f"Possible reasons:\n"
                f"- Video has no subtitles/transcript\n"
                f"- YouTube is blocking the request\n"
                f"- Video is age-restricted or private\n\n"
                f"Please try another YouTube video."
            )

# ─── Generate summary using Groq ───────────────────────────────
def generate_groq_content(transcript_text, prompt):
    # Protect against very large requests by chunking long transcripts.
    # Estimate tokens via characters (approx 4 chars/token) and split by characters.
    def split_text(text, max_chars=16000):
        chunks = []
        start = 0
        length = len(text)
        while start < length:
            end = min(start + max_chars, length)
            if end < length:
                # try to split at sentence boundary
                last_period = text.rfind('.', start, end)
                if last_period != -1 and last_period > start:
                    end = last_period + 1
            chunks.append(text[start:end].strip())
            start = end
        return [c for c in chunks if c]

    def summarize_chunk(chunk_prompt, model="llama-3.3-70b-versatile"):
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": chunk_prompt}]
        )
        return resp.choices[0].message.content

    max_chunk_chars = 16000
    if len(transcript_text) <= max_chunk_chars:
        return summarize_chunk(prompt + transcript_text)

    chunks = split_text(transcript_text, max_chunk_chars)
    chunk_summaries = []
    for i, ch in enumerate(chunks):
        chunk_prompt = (
            f"{prompt}\n\n--- Begin chunk {i+1}/{len(chunks)} ---\n" + ch
        )
        summary = summarize_chunk(chunk_prompt)
        chunk_summaries.append(summary)

    # Combine intermediate summaries and request a final consolidated summary
    combined = "\n\n".join(chunk_summaries)
    final_prompt = (
        "You are a YouTube video summarizer. Combine the following chunk summaries "
        "into a single coherent summary within 250 words:\n\n"
    )
    return summarize_chunk(final_prompt + combined)

# ─── Streamlit UI ──────────────────────────────────────────────
st.set_page_config(page_title="YouTube Summarizer", page_icon="🎬")
st.title("🎬 YouTube Transcript to Detailed Notes")
st.caption("Powered by Groq AI — 100% Free")

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    try:
        video_id = extract_video_id(youtube_link)
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    except:
        st.warning("Please enter a valid YouTube URL.")

if st.button("📋 Get Detailed Notes"):
    if not youtube_link:
        st.warning("Please enter a YouTube link first.")
    else:
        with st.spinner("⏳ Extracting transcript... please wait"):
            try:
                transcript_text = extract_transcript_details(youtube_link)
                st.success("✅ Transcript extracted successfully!")
            except Exception as e:
                st.error(str(e))
                st.stop()

        with st.spinner("🤖 Generating summary with Groq AI..."):
            try:
                summary = generate_groq_content(transcript_text, prompt)
                st.markdown("## 📝 Detailed Notes:")
                st.write(summary)
            except Exception as e:
                st.error(f"Groq Error: {e}")