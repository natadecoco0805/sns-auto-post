import os
import json
import time
import datetime
import requests
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from google import genai

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

WEBHOOKS = {
    "investment": os.environ["DISCORD_WEBHOOK_INVESTMENT"],
    "beauty": os.environ["DISCORD_WEBHOOK_BEAUTY"],
    "gadget": os.environ["DISCORD_WEBHOOK_GADGET"],
}

client = genai.Client(api_key=GEMINI_API_KEY)


def get_jst_now():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=9)


def fetch_investment_news():
    url = "https://news.google.com/rss/search?q=%E6%97%A5%E6%9C%AC%E6%A0%AA%20%E6%96%B0NISA%20%E9%AB%98%E9%85%8D%E5%BD%93%E6%A0%AA&hl=ja&gl=JP&ceid=JP:ja"

    try:
        with urlopen(url, timeout=10) as response:
            data = response.read()

        root = ET.fromstring(data)
        items = root.findall(".//item")[:5]

        titles = []
        for item in items:
            title = item.find("title")
            if title is not None and title.text:
                titles.append(title.text)

        return "\n".join([f"- {t}" for t in titles])

    except Exception as e:
        return f"ニュース取得失敗: {e}"


def generate_posts(prompt):
    models = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]

    last_error = None

    for model in models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                text = response.text.strip()

                if text.startswith("```json"):
                    text = text.replace("```json", "").replace("```", "").strip()
                elif text.startswith("```"):
                    text = text.replace("```", "").strip()

                return json.loads(text)

            except Exception as e:
                last_error = e
                time.sleep(5 * (attempt + 1))

    return {
        "investment": f"投稿生成に失敗しました。\n理由: {last_error}",
        "beauty": f"投稿生成に失敗しました。\n理由: {last_error}",
        "gadget": f"投稿生成に失敗しました。\n理由: {last_error}",
    }


def send_to_discord(account_key, account_name, post_text, current_time):
    message = f"""
━━━━━━━━━━━━━━
【{account_name} 投稿案】

生成日時：{current_time}
━━━━━━━━━━━━━━

{post_text}

━━━━━━━━━━━━━━
添削後、Xへコピペ投稿。
"""

    requests.post(
        WEBHOOKS[account_key],
        json={"content": message}
    )


now = get_jst_now()
current_time = now.strftime("%Y/%m/%d %H:%M")

use_news = now.hour == 8
investment_news = fetch_investment_news() if use_news else "今回は時事ネタを使わず、通常の投資記録系投稿を作成する。"

prompt = f"""
あなたはX投稿案を作るSNS運用アシスタントです。

以下の3アカウント用に、X投稿案をそれぞれ1つずつ作成してください。

必ずJSONのみで出力してください。
説明文、補足、コードブロックは禁止です。

出力形式:
{{
  "investment": "投資アカウント用の投稿文",
  "beauty": "美容アカウント用の投稿文",
  "gadget": "ガジェットアカウント用の投稿文"
}}

共通条件:
- そのままXにコピペできる文章
- 改行を入れて読みやすくする
- 180字以内
- ハッシュタグは0〜2個
- アフィリエイト感を出さない
- 煽らない
- 投稿文だけを書く

━━━━━━━━━━━━━━
【投資アカウント】

立ち位置:
一般サラリーマン。
将来が不安なのと、会社の給料だけに依存したくないという理由で投資を始めた。
積立投資メインではなく、個別株・高配当株を適宜買っている。
投資の専門家ではなく、勉強中の会社員として発信する。

今回の時事ネタ:
{investment_news}

投稿内容:
・個別株を見て感じたこと
・高配当株への考え
・給料依存を減らしたいという不安
・投資を始めて変わった考え方
・失敗しないように気をつけていること
・投資初心者〜中級未満のリアルな記録
・1日1回程度は時事ネタを自然に取り入れる

禁止:
・銘柄推奨
・断定的な投資助言
・短期で儲かるような煽り
・「絶対」「必ず」「これを買え」
・積立NISAだけを前提にした内容
・金融の専門家のような口調

文体:
・普通の会社員目線
・少し現実的で不安もある
・無理に前向きすぎない
・改行多め

━━━━━━━━━━━━━━
【美容アカウント】

立ち位置:
美容ガチ勢ではなく、メンズ美容初心者。
昔はスキンケアにほぼ興味がなかったが、肌荒れや清潔感を気にするようになり、少しずつ美容を勉強している社会人。
専門家ではなく、初心者が実際に試しながら改善していく視点で発信する。

投稿内容:
・肌荒れへの共感
・洗顔、保湿、日焼け止めなどの基本
・清潔感を上げるために始めたこと
・美容初心者の失敗談
・続けやすいスキンケア
・男でも最低限やった方がいいと思ったこと

禁止:
・医療効果の断定
・薬機法的に危ない表現
・「必ず治る」「ニキビが消える」などの断定
・美容の専門家ぶった口調
・商品を無理に売る表現
・過剰にキラキラした美容インフルエンサー口調
・会社員という表現

文体:
・初心者目線
・共感寄り
・自然体
・改行多め

━━━━━━━━━━━━━━
【ガジェットアカウント】

立ち位置:
ガジェット専門家ではなく、社会人が仕事・副業・日常を少し快適にするためにガジェットやデスク環境を試しているアカウント。
高級品よりも、コスパや実用性を重視する。

投稿内容:
・買ってよかったガジェット
・デスク環境改善
・作業効率化
・PC周辺機器
・外出先作業
・失敗した買い物
・安くても便利だったもの
・仕事や副業に使える小物

禁止:
・商品を無理に売る表現
・スペックだけの羅列
・ガジェット上級者すぎる専門用語連発
・「絶対買え」「人生変わる」などの煽り
・使っていない商品の断定レビュー

文体:
・普通の社会人目線
・実用性重視
・少し冷静
・コスパ重視
・改行多め
"""

posts = generate_posts(prompt)

send_to_discord("investment", "投資アカ", posts["investment"], current_time)
send_to_discord("beauty", "美容アカ", posts["beauty"], current_time)
send_to_discord("gadget", "ガジェットアカ", posts["gadget"], current_time)
