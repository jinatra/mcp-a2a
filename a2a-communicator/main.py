from mcp.server.fastmcp import FastMCP
from fastmcp import Client
import openai
import os
from dotenv import load_dotenv
import logging
import json

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

try:
    mcp = FastMCP(name="a2a_communicator")
    logger.info("MCP 서버 초기화 성공")

    async def determine_target_mcp(query: str) -> str:
        """사용자 질문을 분석하여 적절한 MCP 서버를 결정합니다."""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 사용자의 질문을 분석하여 영화(TMDB) 또는 음악(Spotify) 중 어떤 서비스에 대한 질문인지 판단하는 AI입니다. 'movie' 또는 'music' 중 하나만 반환하세요."},
                    {"role": "user", "content": query}
                ]
            )
            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            logger.error(f"OpenAI API 호출 중 오류 발생: {str(e)}")
            raise Exception("서비스 분석 중 오류가 발생했습니다.")

    async def forward_to_mcp(query: str, target: str) -> dict:
        """선택된 MCP 서버로 요청을 전달합니다."""
        try:
            if target == "movie":
                async with Client("http://localhost:8001/sse") as client:
                    response = await client.call_tool("get_movie_info_by_title", {"query": query})
                    return {"response": response, "source": "TMDB"}
            else:  # music
                async with Client("http://localhost:8002/sse") as client:
                    response = await client.call_tool("get_music_info_by_title", {"query": query})
                    return {"response": response, "source": "Spotify"}
        except Exception as e:
            logger.error(f"MCP 서버 통신 중 오류 발생: {str(e)}")
            raise Exception("MCP 서버 통신 중 오류가 발생했습니다.")

    @mcp.tool()
    async def process_query(query: str) -> dict:
        """사용자 질문을 처리하고 적절한 MCP 서버로 전달합니다."""
        try:
            # 1. 적절한 MCP 서버 결정
            target = await determine_target_mcp(query)
            
            # 2. 선택된 MCP 서버로 요청 전달
            response = await forward_to_mcp(query, target)
            
            return response
        except Exception as e:
            logger.error(f"쿼리 처리 중 오류 발생: {str(e)}")
            raise Exception(str(e))

    if __name__ == "__main__":
        logger.info("A2A Communicator 서버 시작")
        mcp.run(transport="sse")

except Exception as e:
    logger.error(f"서버 실행 중 오류 발생: {str(e)}", exc_info=True)