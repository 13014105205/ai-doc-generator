# -*- coding: utf-8 -*-
from flask import Flask, request, send_file
from docx import Document
import requests, os

app = Flask(__name__)

# 读取API密钥（直接复制你申请的密钥替换下面内容）
API_KEY = open('key.txt').read().strip()


def ask_deepseek(question):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": question}]
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()['choices'][0]['message']['content']


@app.route('/')
def home():
    return '''
    <form action="/gen" method="post">
        <textarea name="ask" placeholder="输入需求..."></textarea>
        <button>生成文档</button>
    </form>
    '''


@app.route('/gen', methods=['POST'])
def generate():
    # 获取用户需求
    user_ask = request.form['ask']

    # 调用DeepSeek生成内容
    ai_content = ask_deepseek(f"根据以下需求生成正式文档：{user_ask}")

    # 替换模板内容
    doc = Document('模板.docx')
    for p in doc.paragraphs:
        if '{{!标题}}' in p.text:
            p.text = ai_content.split('\n')[0]
        if '{{!正文}}' in p.text:
            p.text = '\n'.join(ai_content.split('\n')[1:])

    # 保存并返回文件
    doc.save('output.docx')
    return send_file('output.docx', as_attachment=True)


if __name__ == '__main__':
    app.run(port=5000)