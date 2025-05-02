# mcp-a2a/tmdb-mcp-server/main.py
# MCP 서버 구동

import logging
from mcp.server.fastmcp import FastMCP
from tmdb_agent import search_movie_by_title

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    mcp = FastMCP("tmdb_movie_agent")
    logger.info("MCP 서버 초기화 성공")

    @mcp.tool()
    def get_movie_info_by_title(query: str) -> list:
        """
        영화 제목으로 TMDB에서 검색 후 결과 반환
        """
        logger.info(f"영화 검색 요청: {query}")
        results = search_movie_by_title(query)
        logger.info(f"검색 결과: {len(results)}개 발견")
        return [
            {
                "title": movie["title"],
                "release_date": movie["release_date"],
                "overview": movie["overview"],
                "vote_average": movie["vote_average"],
            }
            for movie in results[:5]
        ]

    if __name__ == "__main__":
        logger.info("MCP 서버 시작")
        mcp.run()

except Exception as e:
    logger.error(f"서버 실행 중 오류 발생: {str(e)}", exc_info=True)