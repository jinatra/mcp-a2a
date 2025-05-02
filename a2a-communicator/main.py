from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TMDB_URL = "http://localhost:5001/movie/search"      # tmdb-mcp-server 주소
SPOTIFY_URL = "http://localhost:5002/music/search"   # spotify-mcp-server 주소

@app.route('/recommend')
def recommend():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # 두 MCP 서버에 동시에 쿼리
    movie_resp = requests.get(TMDB_URL, params={'query': query})
    music_resp = requests.get(SPOTIFY_URL, params={'query': query})

    movie_data = movie_resp.json() if movie_resp.status_code == 200 else {}
    music_data = music_resp.json() if music_resp.status_code == 200 else {}

    # 결과가 있는 쪽만 반환 (둘 다 있으면 둘 다)
    result = {}
    if movie_data.get('movies'):
        result['movie'] = movie_data['movies']
    if music_data.get('tracks'):
        result['music'] = music_data['tracks']

    if not result:
        return jsonify({'message': '검색 결과가 없습니다.'}), 404

    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)