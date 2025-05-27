from python_a2a import A2AServer, skill, agent, run_server, TaskStatus, TaskState
from fastmcp import Client
import asyncio
import logging
import json
from fastapi import FastAPI
from typing import Dict, Any
from starlette.responses import JSONResponse #안되면 지우기

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI()

@agent(
    name="Movie Music Agent",
    description="TMDB/Spotify MCP 서버를 통합하는 A2A 에이전트",
    version="1.0.0",
    author = "jinatra",
    contact = "jinatra0816@gmail.com"
)
class MovieMusicAgent(A2AServer):
    
    @skill(
        name="Get Movie Info",
        description="Get movie information by title",
        tags=["movie", "tmdb"]
    )
    async def get_movie_info(self, query: str) -> Dict[str, Any]:
        """Get movie information from TMDB."""
        try:
            async with Client("http://localhost:8001/sse") as client:
                clean_query = query.replace("get__info_by_title", "").strip()
                logger.info(f"TMDB MCP 서버 호출: {clean_query}")
                
                # 비동기 호출을 동기적으로 처리
                result = await asyncio.wait_for(
                    client.call_tool("get_movie_info_by_title", {"query": clean_query}),
                    timeout=10.0
                )
                logger.info(f"TMDB MCP 서버 응답: {result}")
                
                if not result or not result[0]:
                    return {
                        "parts": [{
                            "type": "text",
                            "text": "검색 결과가 없습니다."
                        }]
                    }
                
                # TextContent 객체에서 텍스트 추출 후 JSON 파싱
                movie_data = json.loads(result[0].text)
                return {
                    "parts": [{
                        "type": "text",
                        "text": f"제목: {movie_data['title']}\n개봉일: {movie_data['release_date']}\n평점: {movie_data['vote_average']}/10\n줄거리: {movie_data['overview']}"
                    }]
                }
        except asyncio.TimeoutError:
            logger.error("TMDB MCP 서버 호출 시간 초과")
            return {
                "parts": [{
                    "type": "text",
                    "text": "서버 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
                }]
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {str(e)}")
            return {
                "parts": [{
                    "type": "text",
                    "text": "응답 데이터 형식이 올바르지 않습니다."
                }]
            }
        except Exception as e:
            logger.error(f"TMDB MCP 서버 호출 중 오류: {str(e)}")
            return {
                "parts": [{
                    "type": "text",
                    "text": f"오류가 발생했습니다: {str(e)}"
                }]
            }

    @skill(
        name="Get Music Info",
        description="Get music information by title",
        tags=["music", "spotify"]
    )
    async def get_music_info(self, query: str) -> Dict[str, Any]:
        """Get music information from Spotify."""
        try:
            async with Client("http://localhost:8002/sse") as client:
                # 쿼리에서 get__info_by_title 제거
                clean_query = query.replace("get__info_by_title", "").strip()
                logger.info(f"Spotify MCP 서버 호출: {clean_query}")
                
                # 비동기 호출을 동기적으로 처리
                result = await asyncio.wait_for(
                    client.call_tool("get_music_info_by_title", {"query": clean_query}),
                    timeout=10.0
                )
                logger.info(f"Spotify MCP 서버 응답: {result}")
                
                if not result or not result[0]:
                    return {
                        "parts": [{
                            "type": "text",
                            "text": "검색 결과가 없습니다."
                        }]
                    }
                
                # TextContent 객체에서 텍스트 추출 후 JSON 파싱
                music_data = json.loads(result[0].text)
                return {
                    "parts": [{
                        "type": "text",
                        "text": f"제목: {music_data['name']}\n아티스트: {music_data['artist']}\n앨범: {music_data['album']}\n발매일: {music_data['release_date']}"
                    }]
                }
        except asyncio.TimeoutError:
            logger.error("Spotify MCP 서버 호출 시간 초과")
            return {
                "parts": [{
                    "type": "text",
                    "text": "서버 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
                }]
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {str(e)}")
            return {
                "parts": [{
                    "type": "text",
                    "text": "응답 데이터 형식이 올바르지 않습니다."
                }]
            }
        except Exception as e:
            logger.error(f"Spotify MCP 서버 호출 중 오류: {str(e)}")
            return {
                "parts": [{
                    "type": "text",
                    "text": f"오류가 발생했습니다: {str(e)}"
                }]
            }
    
    def handle_task(self, task):
        try:
            # Extract query from message
            message_data = task.message or {}
            content = message_data.get("content", {})
            text = content.get("text", "") if isinstance(content, dict) else ""
            
            logger.info(f"받은 메시지: {text}")
            
            # 영화 검색인지 음악 검색인지 판단
            if "영화" in text or "movie" in text.lower():
                query = text.replace("영화", "").replace("movie", "").strip().rstrip("?.")
                logger.info(f"영화 검색 요청: {query}")
                result = asyncio.run(self.get_movie_info(query))
                task.artifacts = [result]                                                   #검색 결과를 task의 artifacts에 저장 (A2A 프로토콜에서 artifacts는 작업의 결과물을 나타냄)
                task.status = TaskStatus(state=TaskState.COMPLETED)                         #작업이 성공적으로 완료되었음을 나타냄 → 처리된 결과는 Agent Client에게 JSON-RPC 2.0 형식으로 반환됨
                
                # 응답 데이터 로깅 추가
                logger.info("================================")
                logger.info("영화 에이전트 선택 => TMDB MCP 서버 호출")
                logger.info("Agent Client에게 전송될 응답:")
                logger.info(f"Task ID: {task.id}")
                logger.info(f"Status: {task.status.state}")
                logger.info(f"Artifacts: {json.dumps(task.artifacts, indent=2, ensure_ascii=False)}")
                logger.info("================================")
                
            elif "음악" in text or "music" in text.lower() or "노래" in text:
                query = text.replace("음악", "").replace("music", "").replace("노래", "").strip().rstrip("?.")
                logger.info(f"음악 검색 요청: {query}")
                result = asyncio.run(self.get_music_info(query))
                task.artifacts = [result]                                                   #검색 결과를 task의 artifacts에 저장 (A2A 프로토콜에서 artifacts는 작업의 결과물을 나타냄)
                task.status = TaskStatus(state=TaskState.COMPLETED)                         #작업이 성공적으로 완료되었음을 나타냄 → 처리된 결과는 Agent Client에게 JSON-RPC 2.0 형식으로 반환됨
                
                # 응답 데이터 로깅 추가
                logger.info("================================")
                logger.info("음악 에이전트 선택 => Spotify MCP 서버 호출")
                logger.info("Agent Client에게 전송될 응답:")
                logger.info(f"Task ID: {task.id}")
                logger.info(f"Status: {task.status.state}")
                logger.info(f"Artifacts: {json.dumps(task.artifacts, indent=2, ensure_ascii=False)}")
                logger.info("================================")

            else:
                task.status = TaskStatus(
                    state=TaskState.INPUT_REQUIRED,
                    message={"role": "agent", "content": {"type": "text", 
                             "text": "영화나 음악에 대해 물어봐주세요. (예: '인셉션 영화 알려줘' 또는 '아이유 노래 찾아줘')"}}
                )
            return task
            
        except Exception as e:
            logger.error(f"작업 처리 중 오류: {str(e)}")
            task.status = TaskStatus(
                state=TaskState.ERROR,
                message={"role": "agent", "content": {"type": "text", 
                         "text": f"오류가 발생했습니다: {str(e)}"}}
            )
            return task

# FastAPI 라우트 추가 (안되면 지우기)
@app.get("/.well-known/agent.json")
async def get_agent_info():
    agent_info = {
        "name": "Movie Music Agent",
        "description": "TMDB/Spotify MCP 서버를 통합하는 A2A 에이전트",
        "version": "1.0.0",
        "url": "http://localhost:8003/",
        "author": "성우진",
        "contact": "jinatra0816@gmail.com",
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text"],
        "capabilities": {
            "streaming": False,
            "pushNotifications": False
        },
        "authentication": {
            "schemes": ["public"]
        },
        "skills": [
            {
                "id": "get_movie_info",
                "name": "Get Movie Info",
                "description": "Get movie information by title",
                "tags": ["movie", "tmdb"],
                "examples": ["인셉션 영화 알려줘", "movie inception"],
                "inputModes": ["text"],
                "outputModes": ["text"]
            },
            {
                "id": "get_music_info",
                "name": "Get Music Info",
                "description": "Get music information by title",
                "tags": ["music", "spotify"],
                "examples": ["아이유 노래 찾아줘", "music iu"],
                "inputModes": ["text"],
                "outputModes": ["text"]
            }
        ],
        "endpoints": {
            "task": "/task",
            "status": "/status"
        }
    }
    
    # 로그 추가
    logger.info("================================")
    logger.info("Agent 정보 요청 받음")
    logger.info(f"반환할 Agent 정보: {json.dumps(agent_info, indent=2, ensure_ascii=False)}")
    logger.info("================================")
    
    return JSONResponse(agent_info)

# Run the server
if __name__ == "__main__":
    agent = MovieMusicAgent()
    run_server(agent, host="0.0.0.0", port=8003)