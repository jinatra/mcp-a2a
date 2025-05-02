# mcp-a2a/spotify-mcp-server/main.py
# MCP 서버 구동

import logging
from mcp.server.fastmcp import FastMCP
from music_agent import search_music_by_title

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    mcp = FastMCP("spotify_music_agent")
    logger.info("MCP 서버 초기화 성공")

    @mcp.tool()
    def get_music_info_by_title(query: str) -> list:
        """
        음악 제목으로 검색하여 결과를 반환합니다
        """
        logger.info(f"음악 검색 요청: {query}")
        results = search_music_by_title(query)
        logger.info(f"검색 결과: {len(results)}개 발견")
        return [
            {
                "name": music['name'],
                "artist": music['artist'],
                "album": music['album'],
                "release_date": music['release_date'],                
            }
            for music in results[:5]
        ]

    if __name__ == "__main__":
        logger.info("MCP 서버 시작")
        mcp.run()

except Exception as e:
    logger.error(f"MCP 서버 초기화 중 오류 발생: {str(e)}", exc_info=True)
