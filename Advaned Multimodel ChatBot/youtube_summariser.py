import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import os

class YoutubeSummariser:
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def extract_transcript_details(self, youtube_video_url):
        try:
            # Extract video ID using URL parsing
            video_id = self.extract_video_id(youtube_video_url)

            if not video_id:
                return "Invalid YouTube link. Please ensure the link is in the correct format."

            # Get the transcript using YouTubeTranscriptApi
            transcript_text = YouTubeTranscriptApi.get_transcript(video_id)

            # Combine transcript text into a single string
            transcript = " ".join([item["text"] for item in transcript_text])

            return transcript

        except YouTubeTranscriptApi.CouldNotRetrieveTranscript:
            return "Could not retrieve transcript. This video might not have a transcript available."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    def extract_video_id(self, url):
        # Parse the URL to handle various formats
        parsed_url = urlparse(url)

        # Handle the 'youtu.be' short link format
        if parsed_url.netloc in ["youtu.be"]:
            return parsed_url.path.strip("/")

        # Handle standard YouTube URL formats
        if parsed_url.netloc in ["www.youtube.com", "youtube.com"]:
            query_params = parse_qs(parsed_url.query)
            return query_params.get("v", [None])[0]

        # Handle any other potential URL structure
        return None

    def get_summary(self, yt_transcribe_text, prompt):
        try:
            # Generate content using the generative model
            response = self.model.generate_content(prompt + yt_transcribe_text)
            return response.text
        except Exception as e:
            return f"An error occurred while generating the summary: {str(e)}"
