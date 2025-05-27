import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from python_a2a import A2AClient

# 환경 변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

def analyze_query(query: str) -> dict:
    """OpenAI API를 사용하여 사용자 쿼리 분석"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """
                사용자의 질문을 분석하여 다음 정보를 JSON 형식으로 반환해주세요:
                - type: "movie" 또는 "music"
                - search_term: 실제 검색어
                - confidence: 0.0 ~ 1.0 사이의 신뢰도
                """},
                {"role": "user", "content": query}
            ],
            response_format={ "type": "json_object" }
        )
        
        result = response.choices[0].message.content
        logger.info(f"OpenAI 분석 결과: {result}")
        return eval(result)
        
    except Exception as e:
        logger.error(f"OpenAI API 호출 중 오류: {str(e)}")
        raise

def main():
    # A2A 클라이언트 초기화 (movie-music-agent 연결)
    a2a_client = A2AClient("http://localhost:8003")
    
    while True:
        query = input("\n무엇을 찾아볼까요? (종료하려면 'q' 입력): ")
        if query.lower() == 'q':
            break
            
        try:
            # 1. OpenAI로 쿼리 분석
            analysis = analyze_query(query)
            search_type = analysis["type"]
            search_term = analysis["search_term"]
            confidence = analysis["confidence"]
            
            logger.info(f"분석 결과 - 타입: {search_type}, 검색어: {search_term}, 신뢰도: {confidence}")
            
            # 2. A2A 에이전트 호출
            if search_type == "movie":
                result = a2a_client.ask(f"get_movie_info_by_title {search_term}")
                print("\n🎬 영화 정보:")
                print(result)  # 문자열로 직접 출력
                    
            else:  # music
                result = a2a_client.ask(f"get_music_info_by_title {search_term}")
                print("\n🎵 음악 정보:")
                print(result)  # 문자열로 직접 출력
                    
        except Exception as e:
            print(f"오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    print("영화/음악 검색 서비스에 오신 것을 환영합니다!")
    print("예시: '8월의 크리스마스 영화 알려줘' 또는 '아이유 노래 찾아줘'")
    main()