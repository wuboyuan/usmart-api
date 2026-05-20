# -*- coding: utf-8 -*-
"""
WebSocket行情推送示例
"""

import time
import json
from usmart_api import USmartClient


def simple_push_example():
    """简单推送示例"""
    
    client = USmartClient(
        X_Channel='your_channel',
        phoneNumber='your_phone',
        login_password='your_password',
        trade_passwrod='your_trade_password',
        public_key='your_public_key',
        private_key='your_private_key'
    )
    
    # 登录
    client.login()
    
    # 定义回调函数
    def handler(topic: str, data: str):
        print(f"[收到] {topic}: {data[:100]}...")
    
    # 启动推送
    client.start_quote_push(handler)
    time.sleep(3)
    
    # 订阅
    client.subscribe_quote(["rt.us.TSLA", "ob.us.TSLA"])
    print("已订阅，接收数据60秒...")
    
    time.sleep(60)
    
    # 停止
    client.stop_quote_push()


def advanced_push_example():
    """高级推送示例 - 不同类型数据处理"""
    
    client = USmartClient(
        X_Channel='your_channel',
        phoneNumber='your_phone',
        login_password='your_password',
        trade_passwrod='your_trade_password',
        public_key='your_public_key',
        private_key='your_private_key'
    )
    
    client.login()
    
    def handler(topic: str, data: str):
        """处理不同类型的行情数据"""
        try:
            data_obj = json.loads(data)
            
            if topic.startswith("rt."):
                # 实时行情
                price = data_obj.get('latestPrice')
                change = data_obj.get('changeRate')
                print(f"[实时] {topic}: 价格={price}, 涨跌幅={change}%")
                
            elif topic.startswith("ob."):
                # 买卖盘
                bids = data_obj.get('data', [])
                if bids:
                    bid1 = bids[0].get('bidPrice')
                    ask1 = bids[0].get('askPrice')
                    print(f"[盘口] {topic}: 买一={bid1}, 卖一={ask1}")
                    
            elif topic.startswith("tk."):
                # 逐笔成交
                print(f"[逐笔] {topic}: {data_obj}")
                
        except Exception as e:
            print(f"[错误] 处理 {topic} 失败: {e}")
    
    # 启动并订阅多个类型
    client.start_quote_push(handler)
    time.sleep(3)
    
    client.subscribe_quote([
        "rt.hk.00700",   # 腾讯实时行情
        "ob.hk.00700",   # 腾讯买卖盘
        "rt.us.TSLA",    # 特斯拉实时行情
    ])
    
    print("接收数据，按Ctrl+C停止...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止接收")
    
    client.stop_quote_push()


def dynamic_handler_example():
    """动态切换处理器示例"""
    
    client = USmartClient(
        X_Channel='your_channel',
        phoneNumber='your_phone',
        login_password='your_password',
        trade_passwrod='your_trade_password',
        public_key='your_public_key',
        private_key='your_private_key'
    )
    
    client.login()
    
    # 启动（使用默认处理器）
    client.start_quote_push()
    time.sleep(3)
    
    client.subscribe_quote(["rt.us.TSLA"])
    
    # 20秒后切换到分析处理器
    time.sleep(20)
    
    def analyze_handler(topic: str, data: str):
        data_obj = json.loads(data)
        price = data_obj.get('latestPrice')
        if price:
            price = float(price)
            if price > 250:
                print(f"[预警] {topic} 突破250: {price}")
            elif price < 200:
                print(f"[预警] {topic} 跌破200: {price}")
    
    print("切换到分析处理器...")
    client.set_quote_handler(analyze_handler)
    
    time.sleep(40)
    client.stop_quote_push()


if __name__ == '__main__':
    # simple_push_example()
    # advanced_push_example()
    # dynamic_handler_example()
    pass
