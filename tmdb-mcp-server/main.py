# mcp-a2a/tmdb-mcp-server/main.py
# MCP 서버 구동

import logging
from mcp.server.fastmcp import FastMCP
from tmdb_agent import search_movie_by_title
from starlette.requests import Request
from starlette.responses import JSONResponse

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    mcp = FastMCP(name="tmdb_movie_agent") # MCP 서버의 고유 식별자 → 다른 서버들이 이 MCP 서버를 식별 가능
    logger.info(f"MCP 서버 초기화 성공")

    @mcp.tool() # mcp.tool() 데코레이터로 등록된 함수들이 MCP 서버의 도구로 등록
    def get_movie_info_by_title(query: str) -> list:
        try:
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
        except Exception as e:
            logger.error(f"get_movie_info_by_title 에러: {str(e)}", exc_info=True)
            # 에러 메시지를 클라이언트에도 반환 (디버깅용)
            return [{"error": str(e)}]

    @mcp.custom_route("/echo", methods=["POST"])
    async def echo(request: Request):
        logger.info("echo 요청 받음")
        data = await request.json()
        logger.info(f"echo 요청 데이터: {data}")
        return JSONResponse({"echo": data})

    if __name__ == "__main__":
        logger.info("TMDB MCP 서버 시작")
        mcp.run(transport="sse")

except Exception as e:
    logger.error(f"서버 실행 중 오류 발생: {str(e)}", exc_info=True)