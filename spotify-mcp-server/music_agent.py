# mcp-a2a/spotify-mcp-server/music_agent.py
# Spotigy API와 통신하는 함수 정의

from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
import logging
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise ValueError("SPOTIFY_CLIENT_ID 또는 SPOTIFY_CLIENT_SECRET이 설정되지 않았습니다.")
    logger.info("스포티파이 API 환경 변수 로드 성공")
    
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))

    def search_music_by_title(query):
        """
        음악 제목으로 검색하여 결과를 반환합니다
        :param query: 검색할 음악 제목
        :return: 검색 결과
        """
        logger.info(f"스포티파이 API 호출: {query}")
        results = sp.search(q=query, type='track', limit=5)
        logger.info(f"Spotify API 결과: {results}")
        tracks = []
        for item in results['tracks']['items']:
            tracks.append({
                'name': item['name'],
                'artist': item['artists'][0]['name'],
                'album': item['album']['name'],
                'url': item['external_urls']['spotify'],
                'release_date': item['album']['release_date']
            })
        return tracks  

except Exception as e:
    logger.error(f"Spotify 에이전트 초기화 중 오류 발생: {str(e)}", exc_info=True)
    raise