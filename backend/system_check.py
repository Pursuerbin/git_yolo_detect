#!/usr/bin/env python3
"""
系统状态检测脚本
检测Python环境、依赖包、GPU可用性、模型文件、数据库连接和目录结构
"""

import os
import sys
import importlib
import socket
import time

# 检测Python环境
def check_python_env():
    """检测Python环境"""
    print("\n检测Python环境:")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print("✅ Python环境正常")

# 检测依赖包
def check_dependencies():
    """检测关键依赖包"""
    print("\n检测关键依赖包:")
    
    dependencies = [
        'torch', 'torchvision', 'numpy', 'cv2',  # opencv-python
        'flask', 'flask_cors', 'pymysql', 'dotenv',  # flask-cors, python-dotenv
        'ultralytics', 'psutil'
    ]
    
    missing_packages = []
    
    for pkg in dependencies:
        try:
            importlib.import_module(pkg)
            print(f"✅ {pkg} 已安装")
        except ImportError:
            print(f"❌ {pkg} 未安装")
            missing_packages.append(pkg)
    
    return missing_packages

# 检测GPU可用性
def check_gpu():
    """检测GPU可用性"""
    print("\n检测GPU可用性:")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            print(f"✅ GPU可用，共 {device_count} 个GPU")
            
            for i in range(device_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
                print(f"  GPU {i}: {gpu_name} ({gpu_memory:.2f}GB)")
                
            return True
        else:
            print("⚠️  未检测到GPU，将使用CPU")
            return False
    except ImportError:
        print("❌ PyTorch未安装，无法检测GPU")
        return False

# 检测模型文件
def check_model_files():
    """检测模型文件"""
    print("\n检测模型文件:")
    
    model_dir = "models"
    if os.path.exists(model_dir):
        model_files = [f for f in os.listdir(model_dir) if f.endswith('.pt')]
        
        if model_files:
            print(f"✅ 模型目录存在，找到 {len(model_files)} 个模型文件:")
            for model_file in model_files:
                model_path = os.path.join(model_dir, model_file)
                model_size = os.path.getsize(model_path) / (1024**2)
                print(f"  - {model_file} ({model_size:.2f}MB)")
            return True
        else:
            print("❌ 模型目录存在，但未找到.pt模型文件")
            return False
    else:
        print("❌ 模型目录不存在")
        return False

# 检测目录结构
def check_directories():
    """检测必要的目录结构"""
    print("\n检测目录结构:")
    
    required_dirs = [
        'uploads', 'results', 'videos', 'models', 'logs'
    ]
    
    all_dirs_exist = True
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name} 目录存在")
        else:
            print(f"⚠️  {dir_name} 目录不存在，将自动创建")
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ 已创建 {dir_name} 目录")
            except Exception as e:
                print(f"❌ 创建 {dir_name} 目录失败: {e}")
                all_dirs_exist = False
    
    return all_dirs_exist

# 检测后端服务状态
def check_backend_service():
    """检测后端服务是否运行"""
    print("\n检测后端服务状态:")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    
    try:
        result = sock.connect_ex(("localhost", 5000))
        if result == 0:
            print("✅ 后端服务正在运行")
            return True
        else:
            print("⚠️  后端服务未运行")
            return False
    finally:
        sock.close()

# 检测数据库连接
def check_database():
    """检测数据库连接"""
    print("\n检测数据库连接:")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        import pymysql
        
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', '123456'), # 数据库密码修改这里
            'database': os.getenv('DB_NAME', 'insulator_detection')
        }
        
        conn = pymysql.connect(**db_config, connect_timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        
        print("✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"⚠️  数据库连接失败: {e}")
        print("提示: 首次运行时会自动创建数据库")
        return False

# 主函数
def main():
    """主函数"""
    print("=" * 70)
    print("🔍 系统状态检测脚本")
    print("=" * 70)
    print(f"检测时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = time.time()
    
    # 检测Python环境
    check_python_env()
    
    # 检测依赖包
    missing_packages = check_dependencies()
    if missing_packages:
        print(f"\n❌ 缺少 {len(missing_packages)} 个依赖包")
        print("提示: 运行 pip install -r requirements.txt 安装所有依赖")
    
    # 检测GPU可用性
    gpu_available = check_gpu()
    
    # 检测模型文件
    model_available = check_model_files()
    
    # 检测目录结构
    directories_ok = check_directories()
    
    # 检测数据库连接
    db_connected = check_database()
    
    # 检测后端服务状态
    backend_running = check_backend_service()
    
    # 检测结果汇总
    print("\n" + "=" * 70)
    print("📊 检测结果汇总:")
    print("=" * 70)
    
    checks = [
        ("Python环境", True),
        ("依赖包", len(missing_packages) == 0),
        ("GPU可用性", gpu_available),
        ("模型文件", model_available),
        ("目录结构", directories_ok),
        ("数据库连接", db_connected),
        ("后端服务", backend_running)
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "⚠️"
        print(f"{status} {check_name}: {'正常' if passed else '异常'}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 系统状态良好，可以正常运行")
    else:
        print("⚠️  系统存在一些问题，建议检查并修复")
    
    end_time = time.time()
    print(f"检测耗时: {end_time - start_time:.2f} 秒")
    print("=" * 70)

if __name__ == "__main__":
    main()
