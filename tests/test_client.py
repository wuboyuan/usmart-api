# -*- coding: utf-8 -*-
"""
测试文件
"""

import pytest
from unittest.mock import Mock, patch
from usmart_api import USmartClient, QuotePushClient


class TestUSmartClient:
    """USmartClient测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        return USmartClient(
            X_Channel='test_channel',
            phoneNumber='12345678901',
            login_password='test_pass',
            trade_passwrod='trade_pass',
            public_key='test_public_key',
            private_key='test_private_key'
        )
    
    def test_init(self, client):
        """测试初始化"""
        assert client.token is None
        assert client.trade_unlocked is False
    
    @patch('usmart_api.client.RequestUtil')
    def test_login_success(self, mock_request, client):
        """测试登录成功"""
        mock_request.return_value.post_with_sign_by_trade.return_value = {
            'code': '0',
            'data': {'token': 'test_token'}
        }
        
        result = client.login()
        
        assert result['success'] is True
        assert result['token'] == 'test_token'
    
    @patch('usmart_api.client.RequestUtil')
    def test_login_failure(self, mock_request, client):
        """测试登录失败"""
        mock_request.return_value.post_with_sign_by_trade.return_value = {
            'code': '1',
            'msg': '密码错误'
        }
        
        result = client.login()
        
        assert result['success'] is False
        assert '密码错误' in result['error']


class TestQuotePushClient:
    """QuotePushClient测试类"""
    
    @pytest.fixture
    def push_client(self):
        """创建测试推送客户端"""
        return QuotePushClient(token='test_token')
    
    def test_init(self, push_client):
        """测试初始化"""
        assert push_client.token == 'test_token'
        assert push_client.auth_flag is False
    
    def test_set_handler(self, push_client):
        """测试设置处理器"""
        handler = Mock()
        push_client.set_handler(handler)
        assert push_client.handler == handler
    
    def test_default_handler(self, push_client, capsys):
        """测试默认处理器"""
        push_client._default_handler('test.topic', 'test_data')
        captured = capsys.readouterr()
        assert 'test.topic' in captured.out
        assert 'test_data' in captured.out


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
