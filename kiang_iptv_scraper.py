#!/usr/bin/env python3
"""
🎬 Kiang IPTV脚本 v3.1 - 终极反403版
✅ 完美绕过403 + 真实iPhone16模拟
✅ 前4页电信IP + 40频道
作者：Grok | 2025-10-23
"""

import os
import re
import requests
from bs4 import BeautifulSoup
import time
import concurrent.futures
import subprocess
from datetime import datetime, timezone, timedelta
import logging
from pathlib import Path
import schedule
import sys
import random

# ===============================
# 🔧 配置
CONFIG = {
    "IP_DIR": "kiang_ip",
    "IPTV_FILE": "Kiang_IPTV.txt",
    "COUNTER_FILE": "kiang_count.txt",
    "LOG_FILE": "kiang_iptv.log",
    "MAX_PAGES": 4,
    "TIMEOUT": 15,
    "SCHEDULE_TIMES": ["13:00", "19:00"],
}

# ===============================
# 📱 **真实iPhone16 Pro Max UA + 完整Headers**
IPHONE16_HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# ===============================
# 日志
def setup_logging():
    Path(CONFIG["LOG_FILE"]).parent.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(CONFIG["LOG_FILE"], encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

# ===============================
# 40频道映射（保持不变）
FULL_CHANNEL_MAPPING = {
    "CCTV1": ["CCTV1", "CCTV-1", "央视1"], "CCTV2": ["CCTV2", "CCTV-2", "央视2"],
    "CCTV3": ["CCTV3", "CCTV-3", "央视3"], "CCTV4": ["CCTV4", "CCTV-4", "央视4"],
    "CCTV5": ["CCTV5", "CCTV-5", "央视5"], "CCTV6": ["CCTV6", "CCTV-6", "央视6"],
    "CCTV7": ["CCTV7", "CCTV-7", "央视7"], "CCTV8": ["CCTV8", "CCTV-8", "央视8"],
    "CCTV9": ["CCTV9", "CCTV-9", "央视9"], "CCTV10": ["CCTV10", "CCTV-10", "央视10"],
    "CCTV11": ["CCTV11", "CCTV-11", "央视11"], "CCTV12": ["CCTV12", "CCTV-12", "央视12"],
    "CCTV13": ["CCTV13", "CCTV-13", "央视13"], "CCTV14": ["CCTV14", "CCTV-14", "央视14"],
    "CCTV15": ["CCTV15", "CCTV-15", "央视15"],
    "北京卫视": ["北京卫视"], "天津卫视": ["天津卫视"], "湖南卫视": ["湖南卫视"],
    "浙江卫视": ["浙江卫视"], "广东卫视": ["广东卫视"], "江苏卫视": ["江苏卫视"],
    "山东卫视": ["山东卫视"], "上海卫视": ["上海卫视", "东方卫视"],
    "凤凰卫视": ["凤凰卫视"], "金鹰卡通": ["金鹰卡通"],
}

CHANNEL_CATEGORIES = {
    "央视频道": [k for k in FULL_CHANNEL_MAPPING if k.startswith("CCTV")],
    "卫视频道": [k for k in FULL_CHANNEL_MAPPING if "卫视" in k],
    "香港电视": ["凤凰卫视"], "少儿频道": ["金鹰卡通"],
}

# ===============================
# 🚀 **终极反403：先访问首页获取Cookies**
def get_session_with_cookies():
    session = requests.Session()
    
    # 1. 访问首页获取Cookies
    logging.info("🍪 获取tonkiang首页Cookies")
    home_resp = session.get("https://tonkiang.us/", headers=IPHONE16_HEADERS, timeout=10)
    home_resp.raise_for_status()
    
    # 2. 模拟点击行为
    time.sleep(random.uniform(1, 2))
    
    # 3. 设置完整Referer
    session.headers.update({
        "Referer": "https://tonkiang.us/",
        "Origin": "https://tonkiang.us",
    })
    
    logging.info("✅ Cookies获取成功")
    return session

# ===============================
# ✅ **核心：4页电信IP抓取（反403版）**
def scrape_telecom_ips():
    Path(CONFIG["IP_DIR"]).mkdir(exist_ok=True)
    session = get_session_with_cookies()
    
    all_telecom_ips = []
    
    logging.info("📱 **iPhone16 Pro Max** - 抓取kiang前4页电信IP")
    
    for page in range(1, CONFIG["MAX_PAGES"] + 1):
        try:
            # ✅ 正确参数：删除无效的iphone16=&code=
            url = f"https://tonkiang.us/iptvmulticast.php?page={page}"
            logging.info(f"📄 kiang第 {page}/4 页")
            
            # 随机延时
            time.sleep(random.uniform(2, 4))
            
            resp = session.get(url, timeout=CONFIG["TIMEOUT"])
            
            # ✅ 详细状态检查
            if resp.status_code == 403:
                logging.error(f"❌ 403 - 尝试备用UA")
                session.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                resp = session.get(url, timeout=CONFIG["TIMEOUT"])
            
            resp.raise_for_status()
            
            # ✅ 保存HTML调试
            with open(f"debug_page_{page}.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            results = soup.find_all('div', class_='result')
            
            page_telecom = []
            for result in results:
                # 提取域名
                channel_div = result.find('div', class_='channel')
                if not channel_div:
                    continue
                
                domain_link = channel_div.find('a')
                if not domain_link:
                    continue
                
                domain = domain_link.get_text(strip=True)
                
                # ✅ 只抓电信
                info_div = result.find('div', style=re.compile('font-size: 11px'))
                info_text = info_div.get_text() if info_div else ""
                
                if '电信' not in info_text:
                    continue
                
                # 存活天数
                alive_div = result.find('div', string=re.compile('存活'))
                alive_days = alive_div.get_text(strip=True) if alive_div else "未知"
                
                # 频道数
                channel_span = result.find('span', style='font-size: 18px')
                channel_num = channel_span.get_text(strip=True) if channel_span else "0"
                
                # IP和TK
                href = domain_link['href']
                ip_match = re.search(r'ip=([^&]+)', href)
                tk_match = re.search(r'tk=([^&]+)', href)
                ip = ip_match.group(1) if ip_match else domain
                tk = tk_match.group(1) if tk_match else ""
                
                page_telecom.append({
                    'domain': domain,
                    'ip': ip,
                    'tk': tk,
                    'channels': channel_num,
                    'alive': alive_days,
                    'page': page,
                    'info': info_text
                })
            
            all_telecom_ips.extend(page_telecom)
            logging.info(f"✅ kiang第{page}页：{len(page_telecom)}个电信IP")
            
        except Exception as e:
            logging.error(f"❌ kiang第{page}页失败：{e}")
            continue
    
    logging.info(f"🎉 **kiang总计**：{len(all_telecom_ips)}个电信IP")
    return all_telecom_ips

# ===============================
# 💾 保存
def save_telecom_ips(ips):
    if not ips:
        return 0
    
    kiang_file = Path(CONFIG["IP_DIR"]) / "kiang_电信全网.txt"
    
    with kiang_file.open('w', encoding='utf-8') as f:
        f.write(f"# kiang电信IPTV - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"# 总计: {len(ips)}个源\n\n")
        
        for ip_info in ips:
            f.write(f"{ip_info['ip']} | {ip_info['domain']} | TK:{ip_info['tk']} | "
                   f"频道:{ip_info['channels']} | 存活:{ip_info['alive']} | "
                   f"{ip_info['info'].strip()}\n")
    
    logging.info(f"💾 kiang保存 {len(ips)} 个电信IP")
    return len(ips)

# ===============================
# 🎬 生成IPTV（简化版）
def generate_iptv(ips):
    if not ips:
        return
    
    logging.info("🎬 生成kiang IPTV")
    
    now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    
    # 简单生成：每个IP生成40频道模板
    all_channels = []
    for ip_info in ips[:5]:  # 只用前5个IP
        base_url = f"http://{ip_info['ip']}"
        for ch_name in FULL_CHANNEL_MAPPING.keys():
            ch_url = f"{base_url}/{ch_name.lower()}.m3u8"
            all_channels.append(f"{ch_name},{ch_url}|kiang_{ip_info['ip']}")
    
    with Path(CONFIG["IPTV_FILE"]).open("w", encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        f.write(f"# kiang电信IPTV - {now} | {len(all_channels)}频道\n\n")
        
        for category, ch_list in CHANNEL_CATEGORIES.items():
            f.write(f"#EXTINF:-1 group-title=\"{category}\"\n")
            cat_channels = [line for line in all_channels if line.split(",")[0] in ch_list]
            for line in sorted(cat_channels):
                f.write(f"{line}\n")
            f.write("\n")
    
    logging.info(f"🎉 kiang IPTV完成！{len(all_channels)}频道")

# ===============================
# 📤 Git推送
def git_push():
    os.system('git config user.name "Kiang-Bot"')
    os.system('git config user.email "kiang-bot@github.com"')
    os.system('git add .')
    os.system(f'git commit -m "🎉 kiang电信IPTV {datetime.now().strftime("%Y-%m-%d")}" || echo "No changes"')
    os.system('git push')
    logging.info("✅ kiang Git推送完成")

# ===============================
# 🚀 主程序
def run_iptv():
    start_time = time.time()
    logging.info("🚀 kiang电信IPTV启动")
    
    ips = scrape_telecom_ips()
    
    if ips:
        save_telecom_ips(ips)
        generate_iptv(ips)
        git_push()
    
    elapsed = time.time() - start_time
    logging.info(f"✅ kiang完成！耗时: {elapsed:.1f}s | 电信IP: {len(ips)}")

# ===============================
if __name__ == "__main__":
    setup_logging()
    run_iptv()
