import requests
import os

webhook_url = os.environ["DISCORD_WEBHOOK"]

requests.post(
    webhook_url,
    json={
        "content": "GitHub Actionsテスト成功"
    }
)
