#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import logging
from flask import Flask, render_template, request, jsonify
from web_ui import WebUI
from tianyi import TianYiYun

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/tianyi.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
web_ui = WebUI()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """配置管理接口"""
    if request.method == 'GET':
        return web_ui.get_config()
    else:
        return web_ui.update_config(request.json)

@app.route('/api/accounts', methods=['GET', 'POST', 'DELETE'])
def handle_accounts():
    """账号管理接口"""
    if request.method == 'GET':
        return web_ui.get_accounts()
    elif request.method == 'POST':
        return web_ui.add_account(request.json)
    else:
        return web_ui.delete_account(request.json)

@app.route('/api/push', methods=['GET', 'POST'])
def handle_push():
    """推送配置接口"""
    if request.method == 'GET':
        return web_ui.get_push_config()
    else:
        return web_ui.update_push_config(request.json)

@app.route('/api/run', methods=['POST'])
def run_task():
    """执行签到任务"""
    try:
        config = web_ui.get_config_data()
        tianyi = TianYiYun(config)
        result = tianyi.run()
        web_ui.update_run_info()
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/status')
def get_status():
    """获取运行状态"""
    return web_ui.get_status()

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs('/app/data', exist_ok=True)
    os.makedirs('/app/logs', exist_ok=True)
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=5000, debug=False)
