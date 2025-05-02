# mcp-a2a/tmdb-mcp-server/tmdb_agent.py
# TMDB API와 통신하는 함수 정의

import os
import logging
import requests
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    load_dotenv()
    TMDB_API_KEY = os.getenv("TMDB_API_KEY")
    if not TMDB_API_KEY:
        raise ValueError("TMDB_API_KEY가 설정되지 않았습니다.")
    logger.info("TMDB API환경 변수 로드 성공")
    
    TMDB_API_URL = "https://api.themoviedb.org/3"

    def search_movie_by_title(query):
        """
        영화 제목으로 검색하여 결과를 반환합니다.
        :param query: 검색할 영화 제목
        :return: 검색 결과
        """
        logger.info(f"TMDB API 호출: {query}")
        url = f"{TMDB_API_URL}/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": query,
            "language": "ko-KR"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("results", [])
        logger.info(f"TMDB API 응답: {len(results)}개 결과")
        return results

except Exception as e:
    logger.error(f"TMDB 에이전트 초기화 중 오류 발생: {str(e)}", exc_info=True)
    raise