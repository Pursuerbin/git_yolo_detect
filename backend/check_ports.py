#!/usr/bin/env python3
"""
端口占用检测脚本
检测系统的5000和5173端口是否被占用
"""

import socket
import sys

def check_port(port):
    """检测指定端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(("localhost", port))
        if result == 0:
            print(f"⚠️  端口 {port} 已被占用")
            return True
        else:
            print(f"✅  端口 {port} 可用")
            return False
    finally:
        sock.close()

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 端口占用检测脚本")
    print("=" * 60)
    
    # 检测5000端口（后端服务）
    print("\n检测后端服务端口 (5000):")
    backend_port_used = check_port(5000)
    
    # 检测5173端口（前端服务）
    print("\n检测前端服务端口 (5173):")
    frontend_port_used = check_port(5173)
    
    print("\n" + "=" * 60)
    print("检测结果汇总:")
    print("=" * 60)
    
    if backend_port_used:
        print("🔴 后端服务端口 (5000) 已被占用，可能需要停止占用该端口的进程")
    else:
        print("🟢 后端服务端口 (5000) 可用，可以启动后端服务")
    
    if frontend_port_used:
        print("🔴 前端服务端口 (5173) 已被占用，可能需要停止占用该端口的进程")
    else:
        print("🟢 前端服务端口 (5173) 可用，可以启动前端服务")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
