import sys
import os
from dotenv import load_dotenv

# Add src to path so tests can find spotify_pipeline package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

load_dotenv("/Users/andrinashrestha/Desktop/Andrina-study-journey/projects/spotify-pipeline/.env")