import os
import requests
from google import genai

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)

prompt = """
あなたはX投稿案を作るSNS運用アシスタントです。

以下の条件で、投資アカウント用のX投稿案を1つ作ってください。

条件:
- 一般サラリーマン目線
- 投資初心者〜中級未満
- 積立投資ではなく、個別株・高配当株を適宜買っている
- 将来不安、会社の給料だけに依存したくないという動機
- 断定的な投資助言にしない
- 銘柄推奨をしない
- 煽らない
- アフィリエイト感を出さない
- そのままXにコピペできる形式
- ハッシュタグは最大2個
- 200字以内

出力は投稿文だけ。
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
)

message = f"""【投資アカ 投稿案】

{response.text}
"""

requests.post(
    DISCORD_WEBHOOK,
    json={"content": message}
)
