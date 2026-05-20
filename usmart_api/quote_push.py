# -*- coding: utf-8 -*-
"""
行情推送模块（WebSocket）

提供实时行情推送功能，基于WebSocket协议。

使用示例:
    >>> from usmart_api import user
    >>> from usmart_api.quote_push import QuotePushClient
    >>> 
    >>> # 登录获取token
    >>> ctx = user.get_user_context()
    >>> result = ctx.login()
    >>> token = result['data']['token']
    >>> 
    >>> # 创建推送客户端
    >>> def my_handler(topic, data):
    ...     print(f"收到 {topic}: {data}")
    >>> 
    >>> client = QuotePushClient(token=token, handler=my_handler)
    >>> client.start()
    >>> 
    >>> # 订阅行情
    >>> client.subscribe(["rt.hk.00700", "ob.hk.00700"])
    >>> 
    >>> # 取消订阅
    >>> client.unsubscribe(["rt.hk.00700"])
    >>> 
    >>> # 停止客户端
    >>> client.stop()

Author: wuboyuan
Email: wuboyuan92@126.com

Disclaimer:
    本库参考 uSMART 官方 API 文档开发，仅供学习交流使用。
    使用本库进行交易产生的任何风险和损失由使用者自行承担，作者不承担任何责任。

主题格式说明:
    格式: <行情类型>.<市场>.<股票代码>
    
    行情类型:
        - rt: realtime，实时行情
        - ob: orderbook，买卖盘
        - tk: tick，逐笔成交
    
    市场:
        - hk: 港股
        - us: 美股
        - sh: 上海
        - sz: 深圳
    
    示例:
        - rt.hk.00700: 腾讯实时行情
        - ob.us.TSLA: 特斯拉买卖盘
        - tk.hk.00700: 腾讯逐笔成交
"""

import json
import base64
import threading
import queue
from typing import Callable, Optional, List

import websocket


# WebSocket操作类型
OP_AUTH = "auth"
OP_PING = "ping"
OP_PONG = "pong"
OP_SUB = "sub"
OP_UNSUB = "unsub"
OP_UPDATE = "update"


class QuotePushClient:
    """
    行情推送客户端
    
    基于WebSocket的实时行情推送客户端。
    
    Attributes:
        token (str): 登录token
        ws_host (str): WebSocket服务器地址
        ws_origin (str): WebSocket来源地址
        handler (callable): 数据接收回调函数
        auth_flag (bool): 是否已完成鉴权
    
    Example:
        >>> def handler(topic, data):
        ...     print(f"{topic}: {data}")
        >>> 
        >>> client = QuotePushClient(token='your_token', handler=handler)
        >>> client.start()
        >>> client.subscribe(["rt.hk.00700"])
    """
    
    def __init__(self, token: str, ws_host: Optional[str] = None,
                 ws_origin: Optional[str] = None, handler: Optional[Callable] = None):
        """
        初始化行情推送客户端
        
        Args:
            token: 登录token
            ws_host: WebSocket服务器地址
            ws_origin: WebSocket来源地址
            handler: 数据接收回调函数，接收(topic, data)两个参数
        """
        self.token = token
        self.ws_host = ws_host or self._get_default_ws_host()
        self.ws_origin = ws_origin or self._get_default_ws_origin()
        self.handler = handler or self._default_handler
        
        self._isrun = False
        self.auth_flag = False
        self._q = queue.Queue()
        self._ws = None
        self._run_thread = None
        self._op_thread = None
    
    def _get_default_ws_host(self) -> str:
        """获取默认WebSocket地址"""
        import os
        config_path = os.path.join(
            os.environ.get('API_DEMO_HOMEPATH', ''),
            'conf', 'config.json'
        )
        try:
            with open(config_path, 'r') as f:
                import json
                config = json.load(f)
                return config.get('ws_host', 'wss://open-hz.yxzq.com:8443/wss/v1')
        except:
            return 'wss://open-hz.yxzq.com:8443/wss/v1'

    def _get_default_ws_origin(self) -> str:
        """获取默认WebSocket来源"""
        import os
        config_path = os.path.join(
            os.environ.get('API_DEMO_HOMEPATH', ''),
            'conf', 'config.json'
        )
        try:
            with open(config_path, 'r') as f:
                import json
                config = json.load(f)
                return config.get('ws_origin', 'https://open-hz.yxzq.com')
        except:
            return 'https://open-hz.yxzq.com'
    
    def _default_handler(self, topic: str, data: str):
        """默认数据处理函数"""
        print(f"[QuotePush] {topic}: {data}")
    
    def set_handler(self, handler: Callable[[str, str], None]):
        """
        设置数据接收回调函数
        
        Args:
            handler: 回调函数，接收(topic, data)两个参数
        """
        self.handler = handler
    
    def subscribe(self, topics: List[str]):
        """
        订阅行情主题
        
        Args:
            topics: 主题列表，格式为["类型.市场.代码", ...]
                - 类型: rt(实时行情), ob(买卖盘), tk(逐笔)
                - 市场: hk(港股), us(美股), sh(上海), sz(深圳)
                - 代码: 股票代码
        
        Example:
            >>> client.subscribe(["rt.hk.00700", "ob.hk.00700"])
        """
        self._send(json.dumps({
            "op": OP_SUB,
            "topiclist": topics
        }))
    
    def unsubscribe(self, topics: List[str]):
        """
        取消订阅行情主题
        
        Args:
            topics: 要取消订阅的主题列表
        
        Example:
            >>> client.unsubscribe(["rt.hk.00700"])
        """
        self._send(json.dumps({
            "op": OP_UNSUB,
            "topiclist": topics
        }))
    
    def _send(self, message: str):
        """发送消息（内部方法）"""
        if self.auth_flag and self._ws:
            self._ws.send(message)
        else:
            self._q.put(message)
    
    def start(self):
        """
        启动WebSocket连接
        
        在后台线程中启动WebSocket连接，自动完成鉴权。
        """
        self._isrun = True
        self._ws = websocket.WebSocketApp(
            self.ws_host,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        self._run_thread = threading.Thread(target=self._run)
        self._run_thread.start()
    
    def _run(self):
        """运行WebSocket（内部方法）"""
        websocket.enableTrace(False)
        self._op_thread = threading.Thread(target=self._process_queue)
        self._op_thread.start()
        self._ws.run_forever(origin=self.ws_origin)
    
    def _process_queue(self):
        """处理消息队列（内部方法）"""
        import time
        while self._isrun:
            try:
                message = self._q.get(timeout=1)
                if not self._isrun:
                    break
                
                if self.auth_flag and self._ws:
                    self._ws.send(message)
                else:
                    # 延迟处理
                    self._q.put(message)
                    time.sleep(1)
            except queue.Empty:
                continue
    
    def _on_open(self, ws):
        """连接打开回调（内部方法）"""
        ws.send(json.dumps({
            "op": OP_AUTH,
            "accessToken": self.token
        }))
    
    def _on_message(self, ws, message):
        """消息接收回调（内部方法）"""
        try:
            recv = json.loads(message)
            
            # 处理错误
            if recv.get('code', 0) != 0:
                print(f'[QuotePush] Error: {recv}')
            
            # 处理心跳
            if recv.get("op") == "ping":
                ws.send(json.dumps({"op": OP_PONG}))
            
            # 处理鉴权结果
            if recv.get("op") == "auth":
                if recv.get("code") == 0:
                    print('[QuotePush] Auth success')
                    self.auth_flag = True
                else:
                    print(f'[QuotePush] Auth failed: {recv}')
            
            # 处理行情数据
            if recv.get("op") == "update":
                data = base64.b64decode(recv["data"]).decode("utf-8")
                self.handler(recv["topic"], data)
            
            # 处理强制下线
            if recv.get("op") == "offline":
                print("[QuotePush] Force offline")
                ws.close()
                
        except Exception as e:
            print(f'[QuotePush] Message processing error: {e}')
    
    def _on_error(self, ws, error):
        """错误回调（内部方法）"""
        print(f'[QuotePush] Error: {error}')
    
    def _on_close(self, ws, close_status_code=None, close_msg=None):
        """连接关闭回调（内部方法）"""
        self._isrun = False
        self.auth_flag = False
        print("[QuotePush] Connection closed")
    
    def stop(self):
        """
        停止WebSocket连接
        
        关闭WebSocket连接并释放资源。
        """
        self._isrun = False
        if self._ws:
            self._ws.close()
        print("[QuotePush] Client stopped")
