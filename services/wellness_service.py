"""
DayScore - Wellness Service
Handles fetching audio URLs from Firebase Storage for the Wellness Center.
"""

import streamlit as st
from datetime import timedelta
from config.firebase_config import get_firebase_storage

class WellnessService:
    def __init__(self):
        self.bucket = get_firebase_storage()

    def get_audio_url(self, audio_name: str) -> str:
        """
        Get a temporary signed URL for an audio file in Firebase Storage.
        Returns None if the file doesn't exist or storage is unavailable.
        """
        if not self.bucket:
            return None

        try:
            # Map display names to specific filenames in your bucket
            name_map = {
                "🌧️ Rain": "rain.mp3",
                "🌲 Forest": "forest.mp3",
                "📻 White Noise": "white_noise.mp3",
                "🎵 432Hz Tone": "432hz.mp3",
                "🎶 528Hz Tone": "528hz.mp3",
                "🌊 Ocean Waves": "ocean.mp3"
            }
            
            filename = name_map.get(audio_name)
            if not filename:
                return None

            blob = self.bucket.blob(f"wellness_sounds/{filename}")
            
            if blob.exists():
                # Generate a signed URL that lasts for 1 hour
                return blob.generate_signed_url(expiration=timedelta(hours=1))
            return None
        except Exception as e:
            print(f"Error fetching audio from Firebase Storage: {e}")
            return None

    def get_all_audio_urls(self, sound_names: list) -> dict:
        """Fetch URLs for a list of sound names."""
        urls = {}
        for name in sound_names:
            url = self.get_audio_url(name)
            if url:
                urls[name] = url
        return urls
