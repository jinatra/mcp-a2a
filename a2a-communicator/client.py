from fastmcp import Client
import asyncio

async def main():
    print("영화나 음악에 대해 질문해주세요. (종료하려면 'q' 입력)")
    print("예시: '인셉션 영화 정보 알려줘', 'BTS의 Butter 노래 정보 알려줘'")
    
    async with Client("http://localhost:8003/sse") as client:
        while True:
            query = input("\n질문: ").strip()
            if query.lower() == 'q':
                break
                
            try:
                result = await client.call_tool("process_query", {"query": query})
                print("\n결과:")
                print(f"출처: {result['source']}")
                print("응답:", result['response'])
            except Exception as e:
                print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 