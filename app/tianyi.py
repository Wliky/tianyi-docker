#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import random
import base64
import hashlib
import rsa
import requests
import re
from urllib.parse import urlparse

BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")
B64MAP = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

class TianYiYun:
    def __init__(self, config):
        self.config = config
        self.accounts = [acc for acc in config['accounts'] if acc.get('enabled', True)]
        self.push_config = config.get('push_config', {})
        self.settings = config.get('settings', {})
        self.session = requests.Session()
        
    def mask_phone(self, phone):
        """隐藏手机号中间四位"""
        phone = str(phone).strip()
        if len(phone) == 11:
            return phone[:3] + "****" + phone[-4:]
        elif len(phone) > 4:
            return phone[:3] + "****" + phone[-4:]
        else:
            return "***" + phone

    def int2char(self, a):
        return BI_RM[a]

    def b64tohex(self, a):
        d = ""
        e = 0
        c = 0
        for i in range(len(a)):
            if list(a)[i] != "=":
                v = B64MAP.index(list(a)[i])
                if 0 == e:
                    e = 1
                    d += self.int2char(v >> 2)
                    c = 3 & v
                elif 1 == e:
                    e = 2
                    d += self.int2char(c << 2 | v >> 4)
                    c = 15 & v
                elif 2 == e:
                    e = 3
                    d += self.int2char(c)
                    d += self.int2char(v >> 2)
                    c = 3 & v
                else:
                    e = 0
                    d += self.int2char(c << 2 | v >> 4)
                    d += self.int2char(15 & v)
        if e == 1:
            d += self.int2char(c << 2)
        return d

    def rsa_encode(self, j_rsakey, string):
        rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
        result = self.b64tohex((base64.b64encode(rsa.encrypt(f'{string}'.encode(), pubkey))).decode())
        return result

    def login(self, username, password):
        """登录天翼云盘"""
        print("🔄 正在执行登录流程...")
        try:
            urlToken = "https://m.cloud.189.cn/udb/udb_login.jsp?pageId=1&pageKey=default&clientType=wap&redirectURL=https://m.cloud.189.cn/zhuanti/2021/shakeLottery/index.html"
            r = self.session.get(urlToken, timeout=10)
            match = re.search(r"https?://[^\s'\"]+", r.text)
            if not match:
                print("❌ 错误：未找到动态登录页")
                return False
                
            url = match.group()
            r = self.session.get(url, timeout=10)
            match = re.search(r"<a id=\"j-tab-login-link\"[^>]*href=\"([^\"]+)\"", r.text)
            if not match:
                print("❌ 错误：登录入口获取失败")
                return False
                
            href = match.group(1)
            r = self.session.get(href, timeout=10)
            
            captchaToken = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
            lt = re.findall(r'lt = "(.+?)"', r.text)[0]
            returnUrl = re.findall(r"returnUrl= '(.+?)'", r.text)[0]
            paramId = re.findall(r'paramId = "(.+?)"', r.text)[0]
            j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
            self.session.headers.update({"lt": lt})

            username_enc = self.rsa_encode(j_rsakey, username)
            password_enc = self.rsa_encode(j_rsakey, password)
            
            data = {
                "appKey": "cloud",
                "accountType": '01',
                "userName": f"{{RSA}}{username_enc}",
                "password": f"{{RSA}}{password_enc}",
                "validateCode": "",
                "captchaToken": captchaToken,
                "returnUrl": returnUrl,
                "mailSuffix": "@189.cn",
                "paramId": paramId
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0',
                'Referer': 'https://open.e.189.cn/',
            }
            
            r = self.session.post(
                "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do",
                data=data,
                headers=headers,
                timeout=10
            )
            
            result = r.json()
            if result.get('result', 1) != 0:
                print(f"❌ 登录错误：{result.get('msg', '未知错误')}")
                return False
                
            self.session.get(result['toUrl'], timeout=10)
            print("✅ 登录成功")
            return True
            
        except Exception as e:
            print(f"⚠️ 登录异常：{str(e)}")
            return False

    def sign_in(self):
        """执行签到"""
        try:
            rand = str(round(time.time() * 1000))
            sign_url = f'https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
                "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
                "Host": "m.cloud.189.cn",
            }
            resp = self.session.get(sign_url, headers=headers, timeout=10).json()
            return resp
        except Exception as e:
            print(f"❌ 签到请求异常：{str(e)}")
            return {"error": str(e)}

    def lottery(self):
        """执行抽奖"""
        try:
            time.sleep(random.randint(2, 5))
            lottery_url = 'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
                "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
                "Host": "m.cloud.189.cn",
            }
            resp = self.session.get(lottery_url, headers=headers, timeout=10).json()
            return resp
        except Exception as e:
            print(f"❌ 抽奖请求异常：{str(e)}")
            return {"error": str(e)}

    def send_wxpusher(self, msg):
        """WxPusher推送"""
        if not self.push_config.get('wxpusher_app_token') or not self.push_config.get('wxpusher_uids'):
            print("⚠️ 未配置WxPusher，跳过消息推送")
            return False
        
        url = "https://wxpusher.zjiecode.com/api/send/message"
        headers = {"Content-Type": "application/json"}
        
        success_count = 0
        for uid in self.push_config['wxpusher_uids']:
            data = {
                "appToken": self.push_config['wxpusher_app_token'],
                "content": msg,
                "contentType": 3,
                "topicIds": [],
                "uids": [uid],
            }
            try:
                resp = requests.post(url, json=data, headers=headers, timeout=10)
                result = resp.json()
                if result.get('code') == 1000:
                    print(f"✅ WxPusher推送成功 -> UID: {uid}")
                    success_count += 1
                else:
                    print(f"❌ WxPusher推送失败：{result.get('msg', '未知错误')}")
            except Exception as e:
                print(f"❌ WxPusher推送异常：{str(e)}")
        
        return success_count > 0

    def send_server_chan(self, title, msg):
        """Server酱推送"""
        if not self.push_config.get('sct_key'):
            print("⚠️ 未配置Server酱，跳过消息推送")
            return False
        
        url = f"https://sctapi.ftqq.com/{self.push_config['sct_key']}.send"
        data = {
            "title": title,
            "desp": msg
        }
        
        try:
            resp = requests.post(url, data=data, timeout=10)
            result = resp.json()
            if result.get('code') == 0:
                print("✅ Server酱推送成功")
                return True
            else:
                print(f"❌ Server酱推送失败：{result.get('message', '未知错误')}")
                return False
        except Exception as e:
            print(f"❌ Server酱推送异常：{str(e)}")
            return False

    def push_message(self, title, msg):
        """统一推送消息"""
        wx_success = self.send_wxpusher(msg)
        sct_success = self.send_server_chan(title, msg)
        
        # 记录推送状态
        if not wx_success and not sct_success:
            print("⚠️ 所有推送服务均未配置或全部失败")
        return wx_success or sct_success

    def process_account(self, username, password):
        """处理单个账号"""
        masked_phone = self.mask_phone(username)
        account_result = {"username": masked_phone, "sign": "", "lottery": ""}
        
        print(f"\n🔔 处理账号：{masked_phone}")
        
        # 登录流程
        if not self.login(username, password):
            account_result["sign"] = "❌ 登录失败"
            account_result["lottery"] = "❌ 登录失败"
            return account_result
        
        # 签到流程
        sign_result = self.sign_in()
        if "error" in sign_result:
            account_result["sign"] = f"❌ {sign_result['error']}"
        elif sign_result.get('isSign') == "false":
            account_result["sign"] = f"✅ +{sign_result.get('netdiskBonus', '?')}M"
        else:
            account_result["sign"] = f"⏳ 已签到+{sign_result.get('netdiskBonus', '?')}M"
        
        # 抽奖流程
        lottery_result = self.lottery()
        if "error" in lottery_result:
            account_result["lottery"] = f"❌ {lottery_result['error']}"
        elif "errorCode" in lottery_result:
            account_result["lottery"] = f"❌ {lottery_result.get('errorCode')}"
        else:
            prize = lottery_result.get('prizeName') or lottery_result.get('description', '未知奖品')
            account_result["lottery"] = f"🎁 {prize}"
        
        print(f"  {account_result['sign']} | {account_result['lottery']}")
        return account_result

    def run(self):
        """主运行函数"""
        if not self.accounts:
            return {"success": False, "error": "没有可用的账号"}
            
        print("\n" + "="*50)
        print("⛅ 天翼云盘签到开始")
        print("="*50)
        
        all_results = []
        success_count = 0
        
        for acc in self.accounts:
            result = self.process_account(acc["username"], acc["password"])
            all_results.append(result)
            if "❌" not in result["sign"]:
                success_count += 1
            
            # 账号间延迟
            if acc != self.accounts[-1]:
                interval = self.settings.get('account_interval', 5)
                time.sleep(random.randint(interval-2, interval+2))
        
        # 生成汇总表格
        table = "### ⛅ 天翼云盘签到汇总\n\n"
        table += "| 账号 | 签到结果 | 每日抽奖 |\n"
        table += "|:-:|:-:|:-:|\n"
        for res in all_results:
            table += f"| {res['username']} | {res['sign']} | {res['lottery']} |\n"
        
        # 添加统计信息
        table += f"\n**统计**：成功 {success_count}/{len(self.accounts)} 个账号"
        
        # 发送推送
        push_title = f"天翼云盘签到({success_count}/{len(self.accounts)})"
        push_success = self.push_message(push_title, table)
        
        print(f"\n✅ 所有账号处理完成！成功：{success_count}/{len(self.accounts)}")
        
        return {
            "success": True,
            "results": all_results,
            "success_count": success_count,
            "total_count": len(self.accounts),
            "push_sent": push_success
        }
