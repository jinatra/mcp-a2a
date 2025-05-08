from fastmcp import Client
import asyncio

async def main():
    async with Client("http://localhost:8001/sse") as client:
        result = await client.call_tool("get_movie_info_by_title", {"query": "인셉션"})
        print(result)

if __name__ == "__main__":
    asyncio.run(main())