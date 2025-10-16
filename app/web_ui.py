#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from flask import jsonify

class WebUI:
    def __init__(self):
        self.config_file = '/app/data/config.json'
        self.default_config = {
            "accounts": [],
            "push_config": {
                "wxpusher_app_token": "",
                "wxpusher_uids": [],
                "sct_key": ""
            },
            "settings": {
                "account_interval": 5,
                "task_interval": 3
            },
            "last_run": None,
            "run_count": 0
        }
        self.load_config()

    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                self.config = self.default_config.copy()
                self.save_config()
        except Exception as e:
            self.config = self.default_config.copy()
            self.save_config()

    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            return False

    def get_config_data(self):
        """获取配置数据"""
        return self.config

    def get_config(self):
        """获取配置"""
        return jsonify({
            "success": True,
            "data": self.config
        })

    def update_config(self, new_config):
        """更新配置"""
        try:
            if 'settings' in new_config:
                self.config['settings'].update(new_config['settings'])
            
            self.save_config()
            return jsonify({
                "success": True,
                "message": "配置更新成功"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    def get_accounts(self):
        """获取账号列表"""
        return jsonify({
            "success": True,
            "data": self.config['accounts']
        })

    def add_account(self, account_data):
        """添加账号"""
        try:
            if not account_data.get('username') or not account_data.get('password'):
                return jsonify({
                    "success": False,
                    "error": "用户名和密码不能为空"
                }), 400

            # 检查是否已存在
            for account in self.config['accounts']:
                if account['username'] == account_data['username']:
                    return jsonify({
                        "success": False,
                        "error": "账号已存在"
                    }), 400

            # 添加新账号
            self.config['accounts'].append({
                "username": account_data['username'],
                "password": account_data['password'],
                "enabled": account_data.get('enabled', True)
            })

            self.save_config()
            return jsonify({
                "success": True,
                "message": "账号添加成功"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    def delete_account(self, data):
        """删除账号"""
        try:
            username = data.get('username')
            if not username:
                return jsonify({
                    "success": False,
                    "error": "用户名不能为空"
                }), 400

            # 删除账号
            self.config['accounts'] = [
                acc for acc in self.config['accounts'] 
                if acc['username'] != username
            ]

            self.save_config()
            return jsonify({
                "success": True,
                "message": "账号删除成功"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    def get_push_config(self):
        """获取推送配置"""
        return jsonify({
            "success": True,
            "data": self.config['push_config']
        })

    def update_push_config(self, push_config):
        """更新推送配置"""
        try:
            self.config['push_config'].update(push_config)
            self.save_config()
            return jsonify({
                "success": True,
                "message": "推送配置更新成功"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    def get_status(self):
        """获取运行状态"""
        return jsonify({
            "success": True,
            "data": {
                "last_run": self.config.get('last_run'),
                "run_count": self.config.get('run_count', 0),
                "account_count": len(self.config['accounts']),
                "enabled_accounts": len([acc for acc in self.config['accounts'] if acc.get('enabled', True)])
            }
        })

    def update_run_info(self):
        """更新运行信息"""
        self.config['last_run'] = datetime.now().isoformat()
        self.config['run_count'] = self.config.get('run_count', 0) + 1
        self.save_config()
