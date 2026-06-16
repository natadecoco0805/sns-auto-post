import os
import requests
import datetime
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from google import genai

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

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

import time

def generate_post(prompt):
    models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
    ]

    last_error = None

    for model in models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                return response.text.strip()

            except Exception as e:
                last_error = e
                time.sleep(5 * (attempt + 1))

    return f"投稿案生成に失敗しました。\n理由: {last_error}"

now = get_jst_now()
current_time = now.strftime("%Y/%m/%d %H:%M")

# 8時だけ投資アカに時事ネタを入れる
use_news = now.hour == 8
investment_news = fetch_investment_news() if use_news else "今回は時事ネタを使わず、通常の投資記録系投稿を作成する。"

investment_prompt = f"""
あなたはX投稿案を作るSNS運用アシスタントです。

【対象アカウント】
投資アカウント

【アカウントの立ち位置】
一般サラリーマン。
将来が不安なのと、会社の給料だけに依存したくないという理由で投資を始めた。
積立投資メインではなく、個別株・高配当株を適宜買っている。
投資の専門家ではなく、勉強中の会社員として発信する。

【今回の時事ネタ】
{investment_news}

【投稿内容】
・個別株を見て感じたこと
・高配当株への考え
・給料依存を減らしたいという不安
・投資を始めて変わった考え方
・失敗しないように気をつけていること
・投資初心者〜中級未満のリアルな記録
・1日1回程度は時事ネタを自然に取り入れる

【禁止】
・銘柄推奨
・断定的な投資助言
・短期で儲かるような煽り
・「絶対」「必ず」「これを買え」
・積立NISAだけを前提にした内容
・アフィリエイト感
・金融の専門家のような口調

【文体】
・普通の会社員目線
・少し現実的で不安もある
・無理に前向きすぎない
・改行多め
・読みやすく短く
・180字以内
・ハッシュタグは0〜2個

【出力】
投稿文だけを出力してください。
"""

beauty_prompt = """
あなたはX投稿案を作るSNS運用アシスタントです。

【対象アカウント】
メンズ美容アカウント

【アカウントの立ち位置】
美容ガチ勢ではなく、メンズ美容初心者。
昔はスキンケアにほぼ興味がなかったが、肌荒れや清潔感を気にするようになり、少しずつ美容を勉強している社会人。
専門家ではなく、初心者が実際に試しながら改善していく視点で発信する。

【投稿内容】
・肌荒れへの共感
・洗顔、保湿、日焼け止めなどの基本
・清潔感を上げるために始めたこと
・美容初心者の失敗談
・続けやすいスキンケア
・男でも最低限やった方がいいと思ったこと

【禁止】
・医療効果の断定
・薬機法的に危ない表現
・「必ず治る」「ニキビが消える」などの断定
・美容の専門家ぶった口調
・商品を無理に売る表現
・アフィリエイト感
・過剰にキラキラした美容インフルエンサー口調
・会社員という表現

【文体】
・初心者目線
・共感寄り
・自然体
・改行多め
・読みやすく短く
・180字以内
・ハッシュタグは0〜2個

【出力】
投稿文だけを出力してください。
"""

gadget_prompt = """
あなたはX投稿案を作るSNS運用アシスタントです。

【対象アカウント】
ガジェットアカウント

【アカウントの立ち位置】
ガジェット専門家ではなく、社会人が仕事・副業・日常を少し快適にするためにガジェットやデスク環境を試しているアカウント。
高級品よりも、コスパや実用性を重視する。

【投稿内容】
・買ってよかったガジェット
・デスク環境改善
・作業効率化
・PC周辺機器
・外出先作業
・失敗した買い物
・安くても便利だったもの
・仕事や副業に使える小物

【禁止】
・商品を無理に売る表現
・アフィリエイト感
・スペックだけの羅列
・ガジェット上級者すぎる専門用語連発
・「絶対買え」「人生変わる」などの煽り
・使っていない商品の断定レビュー

【文体】
・普通の社会人目線
・実用性重視
・少し冷静
・コスパ重視
・改行多め
・読みやすく短く
・180字以内
・ハッシュタグは0〜2個

【出力】
投稿文だけを出力してください。
"""

investment_post = generate_post(investment_prompt)
beauty_post = generate_post(beauty_prompt)
gadget_post = generate_post(gadget_prompt)

message = f"""
━━━━━━━━━━━━━━
SNS投稿案
生成日時：{current_time}
━━━━━━━━━━━━━━

【投資アカ】
{investment_post}

━━━━━━━━━━━━━━

【美容アカ】
{beauty_post}

━━━━━━━━━━━━━━

【ガジェットアカ】
{gadget_post}

━━━━━━━━━━━━━━
添削後、Xへコピペ投稿。
"""

requests.post(
    DISCORD_WEBHOOK,
    json={"content": message}
)
