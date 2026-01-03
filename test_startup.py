#!/usr/bin/env python3
"""
JANUS 启动诊断脚本
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dispatcher import Dispatcher
from core.providers.antigravity import AntigravityBrainProvider
from core.audit import RuleBasedAuditor
from core.sensors import SensorManager

async def test_startup():
    print("=== JANUS 启动诊断 ===")
    
    # 1. 初始化核心组件
    print("[1/5] 初始化 Provider...")
    provider = AntigravityBrainProvider()
    print("✓ Provider 初始化成功")
    
    print("[2/5] 初始化 Auditor...")
    auditor = RuleBasedAuditor()
    print("✓ Auditor 初始化成功")
    
    print("[3/5] 初始化 Dispatcher...")
    dispatcher = Dispatcher(provider=provider, auditor=auditor)
    print("✓ Dispatcher 初始化成功")
    
    print("[4/5] 初始化 Sensors...")
    workspace_root = os.path.dirname(os.path.abspath(__file__))
    sensor_manager = SensorManager(dispatcher)
    sensor_manager.setup_default_sensors(watch_path=workspace_root)
    print("✓ Sensors 初始化成功")
    
    print("[5/5] 启动 Sensors...")
    await sensor_manager.start_all()
    print("✓ Sensors 启动成功")
    
    print("\n=== 所有组件启动成功 ===")
    print("等待 5 秒后关闭...")
    await asyncio.sleep(5)
    
    print("\n关闭 Sensors...")
    await sensor_manager.stop_all()
    print("✓ 诊断完成")

if __name__ == "__main__":
    try:
        asyncio.run(test_startup())
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
