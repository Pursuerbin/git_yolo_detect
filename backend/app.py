# backend/app.py
"""
YOLOv11绝缘子缺陷检测系统 - Flask后端
包含：图片检测、视频检测、摄像头实时检测功能
作者：吴权彬
"""

# ==================== 设备配置 ====================
import os
import torch
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设备选择函数
def get_available_device():
    """获取可用设备，优先使用GPU"""
    try:
        # 从环境变量获取GPU使用策略
        use_gpu = os.getenv('USE_GPU', 'auto').lower()
        
        if use_gpu == 'false':
            print("⚠️ 强制使用CPU模式")
            return "cpu"
        
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            device_count = torch.cuda.device_count()
            print(f"✅ 检测到GPU: {device_name} ({device_count}个)")
            for i in range(device_count):
                print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
            return "cuda:0"  # 默认使用第一个GPU
        else:
            print("⚠️ 未检测到GPU，将使用CPU")
            return "cpu"
    except Exception as e:
        print(f"⚠️ 设备检测失败: {e}，使用CPU")
        return "cpu"

# 全局设备变量
DETECTION_DEVICE = None  # 初始为None，在运行时确定

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import uuid
from werkzeug.utils import secure_filename
import cv2
import numpy as np

from ultralytics import YOLO
import pymysql
import json
import datetime
import threading
import time
import subprocess
from queue import Queue
import base64

# 日志
import logging
from logging.handlers import RotatingFileHandler
import time

# 检测内存占用
import psutil
import threading


# 替换MySQLdb为pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)

# ==================== CORS 配置 ====================
# if os.environ.get('FLASK_ENV') == 'development':
#     CORS(app, supports_credentials=True)
# else:
#     # 允许所有Tailscale网段（100.64.0.0/10）
#     CORS(app, origins=[
#         # 本地开发
#         "http://localhost:5173",
#         "http://127.0.0.1:5173",
#
#         # Tailscale VPN网段（100.64.0.0/10）
#         "http://100.*.*.*:5173",  # 前端Vite
#         "http://100.*.*.*:5000",  # 后端Flask
#         "http://100.*.*.*",  # 任何端口
#
#         # 服务器本地地址
#         "http://10.33.57.83:5173",
#         "http://10.33.57.83:5000",
#
#         # 通配符匹配更多可能的前端地址
#         "http://*:5173",
#         "http://*:5000",
#     ], supports_credentials=True)

# ==================== CORS 配置 ====================
# 从环境变量读取允许的源
allowed_origins_env = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173')
allowed_origins = allowed_origins_env.split(',')

# 根据环境变量配置CORS
if os.environ.get('FLASK_ENV') == 'development':
    CORS(app, supports_credentials=True)
else:
    CORS(app, origins=allowed_origins, supports_credentials=True)


# ==================== 配置参数 ====================
# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),      # 从环境变量获取
    'user': os.getenv('DB_USER', 'root'),           # 从环境变量获取
    'password': os.getenv('DB_PASSWORD', '123456'), # 从环境变量获取
    'database': os.getenv('DB_NAME', 'insulator_detection')  # 从环境变量获取
}

# 文件路径配置
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
RESULT_FOLDER = os.getenv('RESULT_FOLDER', 'results')
VIDEO_FOLDER = os.getenv('VIDEO_FOLDER', 'videos')
MODEL_FOLDER = os.getenv('MODEL_FOLDER', 'models')

# 确保目录存在
for folder in [UPLOAD_FOLDER, RESULT_FOLDER, VIDEO_FOLDER, MODEL_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# 允许的文件扩展名
image_extensions = os.getenv('ALLOWED_IMAGE_EXTENSIONS', 'png,jpg,jpeg')
video_extensions = os.getenv('ALLOWED_VIDEO_EXTENSIONS', 'mp4,avi,mov,mkv')
ALLOWED_IMAGE_EXTENSIONS = set(image_extensions.split(','))
ALLOWED_VIDEO_EXTENSIONS = set(video_extensions.split(','))
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS

# ==================== 端口设置 ====================
# 在配置参数部分添加
DEFAULT_PORT = 5000
# 允许从环境变量获取端口
APP_PORT = int(os.environ.get('SERVER_PORT', DEFAULT_PORT))

# ==================== 端口自动选择 ====================
def find_available_port(start_port=5000, max_attempts=10):
    """查找可用端口"""
    import socket

    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    return None

# ==================== 全局变量 ====================
# 模型管理
models = {}
current_model = None
model_lock = threading.Lock()

# 摄像头管理
camera_thread = None
camera_running = False
camera_queue = Queue(maxsize=10)

# 类别映射（绝缘子缺陷类型）
class_mapping = {
    'ceramic': '瓷质',
    'glass': '玻璃',
    'composite': '复合',
    'pollution': '污秽',
    'rust': '锈蚀',
    'damage': '破损'
}

# 日志配置将在setup_logging()函数中处理

# 错误处理装饰器
def handle_db_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except pymysql.Error as e:
            app.logger.error(f"数据库错误: {e}")
            return jsonify({'error': '数据库操作失败', 'message': str(e)}), 500
        except Exception as e:
            app.logger.error(f"服务器错误: {e}")
            return jsonify({'error': '服务器内部错误', 'message': str(e)}), 500
    wrapper.__name__ = func.__name__
    return wrapper

# ==================== 日志配置 ====================
def setup_logging():
    """配置日志系统 - 确保只初始化一次"""
    # 从环境变量读取日志配置
    LOG_FOLDER = os.getenv('LOG_FOLDER', 'logs')
    os.makedirs(LOG_FOLDER, exist_ok=True)

    # 配置日志格式 - 使用更简洁的格式
    formatter = logging.Formatter(
        '%(levelname)s:%(name)s:%(message)s',
    )

    # 文件日志（按大小轮转）
    file_handler = RotatingFileHandler(
        os.path.join(LOG_FOLDER, 'app.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 控制台日志 - 使用相同的格式
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # 设置日志器级别并添加处理器
    app.logger.setLevel(logging.INFO)
    
    # 清除现有处理器并添加新的
    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    # 让werkzeug使用默认的日志配置，以便看到完整的服务器启动信息
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)
    # 移除我们添加的处理器，让Werkzeug使用默认的输出方式
    werkzeug_logger.handlers = []

    return app.logger


# ==================== 内存监控 ====================
def memory_monitor():
    """内存监控线程 - 每2分钟检测一次"""
    import psutil

    while True:
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()

            # 只记录重要信息，减少日志输出
            if memory_percent > 80:  # 只在内存使用率高时输出警告
                app.logger.warning(f"内存使用: {memory_info.rss / 1024 / 1024:.1f}MB ({memory_percent:.1f}%)")
            elif memory_percent > 90:  # 内存使用超过90%时警告
                app.logger.error(f"⚠️ 内存使用过高: {memory_percent:.1f}%，建议重启服务")

        except Exception as e:
            app.logger.error(f"内存监控错误: {e}")

        time.sleep(120)  # 每2分钟检查一次（原为10秒）


# ==================== API日志中间件 ====================
@app.before_request
def log_request_info():
    """简化请求日志 - 只记录关键API"""
    if request.path.startswith('/api/') and request.method in ['POST', 'PUT', 'DELETE']:
        app.logger.info(f"请求: {request.method} {request.path} - IP: {request.remote_addr}")

@app.after_request
def log_response_info(response):
    """简化响应日志 - 只记录错误响应"""
    if request.path.startswith('/api/') and response.status_code >= 400:
        app.logger.warning(f"错误响应: {request.method} {request.path} - 状态码: {response.status_code}")
    return response

# ==================== 工具函数 ====================
def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== 数据库工具函数 ====================
def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout = 10
        )
        return connection
    except Exception as e:
        app.logger.error(f"数据库连接失败: {e}")
        raise

def create_tables():
    """创建必要的数据库表"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建用户表
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS users
                       (
                           id
                           INT
                           AUTO_INCREMENT
                           PRIMARY
                           KEY,
                           username
                           VARCHAR
                       (
                           50
                       ) NOT NULL UNIQUE,
                           password VARCHAR
                       (
                           255
                       ) NOT NULL
                           )
                       """)

        # 创建检测记录表（包含图片和视频）
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS detection_records
                       (
                           id
                           INT
                           AUTO_INCREMENT
                           PRIMARY
                           KEY,
                           filename
                           VARCHAR
                       (
                           255
                       ) NOT NULL,
                           result_filename VARCHAR
                       (
                           255
                       ),
                           video_path VARCHAR
                       (
                           255
                       ),
                           processed_video_path VARCHAR
                       (
                           255
                       ),
                           detect_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                           model_used VARCHAR
                       (
                           100
                       ),
                           confidence_avg DECIMAL
                       (
                           5,
                           4
                       ),
                           total_objects INT,
                           confidence_threshold FLOAT DEFAULT 0.25,
                           iou_threshold FLOAT DEFAULT 0.45,
                           detections JSON DEFAULT NULL,
                           detection_type ENUM
                       (
                           'image',
                           'video',
                           'camera'
                       ) DEFAULT 'image',
                           duration FLOAT DEFAULT NULL,
                           frame_count INT DEFAULT NULL,
                           fps FLOAT DEFAULT NULL
                           )
                       """)

        # 检查并创建缺失的列
        columns_to_check = [
            ('video_path', 'ALTER TABLE detection_records ADD COLUMN video_path VARCHAR(255) DEFAULT NULL'),
            ('processed_video_path',
             'ALTER TABLE detection_records ADD COLUMN processed_video_path VARCHAR(255) DEFAULT NULL'),
            ('detection_type',
             'ALTER TABLE detection_records ADD COLUMN detection_type ENUM(\'image\', \'video\', \'camera\') DEFAULT \'image\''),
            ('duration', 'ALTER TABLE detection_records ADD COLUMN duration FLOAT DEFAULT NULL'),
            ('frame_count', 'ALTER TABLE detection_records ADD COLUMN frame_count INT DEFAULT NULL'),
            ('fps', 'ALTER TABLE detection_records ADD COLUMN fps FLOAT DEFAULT NULL')
        ]

        for column_name, sql in columns_to_check:
            cursor.execute(f"SHOW COLUMNS FROM detection_records LIKE '{column_name}'")
            if not cursor.fetchone():
                cursor.execute(sql)
                print(f"✅ 已添加列: {column_name}")

        # 创建默认管理员
        cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password) VALUES ('admin', '123456')")

        conn.commit()
        print("✅ 数据库表创建/验证成功")

    except Exception as e:
        print(f"❌ 创建表失败: {e}")
    finally:
        if conn:
            conn.close()


def repair_database():
    """修复数据库表结构"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        print("🔧 开始修复数据库表结构...")

        # 1. 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'detection_records'")
        if not cursor.fetchone():
            print("❌ detection_records 表不存在，重新创建...")
            cursor.execute("""
                           CREATE TABLE detection_records
                           (
                               id                   INT AUTO_INCREMENT PRIMARY KEY,
                               filename             VARCHAR(255) NOT NULL,
                               result_filename      VARCHAR(255),
                               video_path           VARCHAR(255),
                               processed_video_path VARCHAR(255),
                               detect_time          DATETIME DEFAULT CURRENT_TIMESTAMP,
                               model_used           VARCHAR(100),
                               confidence_avg       DECIMAL(5, 4),
                               total_objects        INT,
                               confidence_threshold FLOAT    DEFAULT 0.25,
                               iou_threshold        FLOAT    DEFAULT 0.45,
                               detections           JSON     DEFAULT NULL,
                               detection_type       ENUM('image', 'video', 'camera') DEFAULT 'image',
                               duration             FLOAT    DEFAULT NULL,
                               frame_count          INT      DEFAULT NULL,
                               fps                  FLOAT    DEFAULT NULL
                           )
                           """)
            print("✅ detection_records 表创建成功")

        # 2. 检查所有必需的列是否存在
        required_columns = [
            'id', 'filename', 'result_filename', 'video_path', 'processed_video_path',
            'detect_time', 'model_used', 'confidence_avg', 'total_objects',
            'confidence_threshold', 'iou_threshold', 'detections', 'detection_type',
            'duration', 'frame_count', 'fps'
        ]

        cursor.execute("SHOW COLUMNS FROM detection_records")
        existing_columns = [col[0] for col in cursor.fetchall()]
        print(f"📋 现有列: {existing_columns}")

        # 添加缺失的列
        for column in required_columns:
            if column not in existing_columns:
                print(f"➕ 添加缺失列: {column}")

                if column == 'detections':
                    cursor.execute("ALTER TABLE detection_records ADD COLUMN detections JSON DEFAULT NULL")
                elif column == 'detect_time':
                    cursor.execute(
                        "ALTER TABLE detection_records ADD COLUMN detect_time DATETIME DEFAULT CURRENT_TIMESTAMP")
                elif column == 'confidence_avg':
                    cursor.execute("ALTER TABLE detection_records ADD COLUMN confidence_avg DECIMAL(5,4) DEFAULT NULL")
                elif column == 'total_objects':
                    cursor.execute("ALTER TABLE detection_records ADD COLUMN total_objects INT DEFAULT 0")
                elif column == 'confidence_threshold':
                    cursor.execute("ALTER TABLE detection_records ADD COLUMN confidence_threshold FLOAT DEFAULT 0.25")
                elif column == 'iou_threshold':
                    cursor.execute("ALTER TABLE detection_records ADD COLUMN iou_threshold FLOAT DEFAULT 0.45")
                elif column == 'detection_type':
                    cursor.execute(
                        "ALTER TABLE detection_records ADD COLUMN detection_type ENUM('image', 'video', 'camera') DEFAULT 'image'")
                elif column in ['duration', 'fps']:
                    cursor.execute(f"ALTER TABLE detection_records ADD COLUMN {column} FLOAT DEFAULT NULL")
                elif column in ['frame_count']:
                    cursor.execute(f"ALTER TABLE detection_records ADD COLUMN {column} INT DEFAULT NULL")
                else:
                    cursor.execute(f"ALTER TABLE detection_records ADD COLUMN {column} VARCHAR(255) DEFAULT NULL")

        conn.commit()
        print("✅ 数据库表结构修复完成")

        # 3. 检查是否有数据
        cursor.execute("SELECT COUNT(*) FROM detection_records")
        count = cursor.fetchone()[0]
        print(f"📊 当前记录数: {count}")

        if count == 0:
            print("ℹ️ 表为空，但结构已修复")

    except Exception as e:
        print(f"❌ 修复数据库失败: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        if conn:
            conn.close()

# 读取模型接口（GPU/CPU）
# def load_model(model_name, force_cpu=False):
#     """加载指定的YOLO模型，支持CPU/GPU动态选择"""
#     global current_model, DETECTION_DEVICE
#
#     # 确定设备
#     if force_cpu:
#         DETECTION_DEVICE = "cpu"
#         print("⚙️ 强制使用CPU模式")
#     elif DETECTION_DEVICE is None:
#         DETECTION_DEVICE = get_available_device()
#
#     with model_lock:
#         if model_name in models:
#             current_model = models[model_name]
#             app.logger.info(f"✅ 使用已加载的模型: {model_name} 在设备: {DETECTION_DEVICE}")
#             return True
#
#         model_path = os.path.join(MODEL_FOLDER, model_name)
#         if not os.path.exists(model_path):
#             app.logger.error(f"❌ 模型文件不存在: {model_path}")
#             return False
#
#         try:
#             app.logger.info(f"🔧 正在加载模型: {model_path}")
#
#             # 加载模型到指定设备
#             model = YOLO(model_path)
#
#             # 显示模型信息
#             app.logger.info(f"📊 模型架构: {model.model.__class__.__name__}")
#             app.logger.info(f"📊 模型参数: {sum(p.numel() for p in model.model.parameters()):,}")
#
#             # 将模型移动到指定设备
#             if DETECTION_DEVICE != "cpu":
#                 model.to(DETECTION_DEVICE)
#                 # 测试GPU内存
#                 try:
#                     torch.cuda.empty_cache()
#                     memory_allocated = torch.cuda.memory_allocated() / 1024 ** 3
#                     memory_reserved = torch.cuda.memory_reserved() / 1024 ** 3
#                     app.logger.info(f"🎮 GPU内存 - 已分配: {memory_allocated:.2f}GB, 保留: {memory_reserved:.2f}GB")
#                 except:
#                     pass
#
#             models[model_name] = model
#             current_model = model
#             app.logger.info(f"✅ 模型 {model_name} 加载成功！设备: {DETECTION_DEVICE}")
#
#             return True
#
#         except Exception as e:
#             app.logger.error(f"❌ 模型加载失败: {e}", exc_info=True)
#
#             # 尝试降级到CPU
#             if DETECTION_DEVICE != "cpu":
#                 app.logger.warning("🔄 尝试降级到CPU模式...")
#                 try:
#                     model = YOLO(model_path)
#                     model.to("cpu")
#                     DETECTION_DEVICE = "cpu"
#                     models[model_name] = model
#                     current_model = model
#                     app.logger.info("✅ 降级到CPU模式成功")
#                     return True
#                 except Exception as e2:
#                     app.logger.error(f"❌ CPU模式也失败: {e2}")
#
#             return False

def load_model(model_name, force_cpu=False):
    """加载指定的YOLO模型，支持CPU/GPU动态选择"""
    global current_model, DETECTION_DEVICE

    with model_lock:
        if model_name in models:
            current_model = models[model_name]
            # 已加载模型时不重复记录日志
            return True

        model_path = os.path.join(MODEL_FOLDER, model_name)
        if not os.path.exists(model_path):
            app.logger.error(f"模型文件不存在: {model_path}")
            return False

        try:
            # 设备选择
            if DETECTION_DEVICE is None:
                DETECTION_DEVICE = get_available_device()

            if force_cpu:
                DETECTION_DEVICE = "cpu"
                app.logger.info(f"强制使用CPU模式")

            # 加载模型
            model = YOLO(model_path)

            if DETECTION_DEVICE != "cpu":
                model.to(DETECTION_DEVICE)
                try:
                    torch.cuda.empty_cache()
                    memory_allocated = torch.cuda.memory_allocated() / 1024 ** 3
                    memory_reserved = torch.cuda.memory_reserved() / 1024 ** 3
                    # 只在加载时记录一次GPU内存信息
                    app.logger.info(f"GPU内存 - 已分配: {memory_allocated:.2f}GB, 保留: {memory_reserved:.2f}GB")
                except Exception as e:
                    app.logger.warning(f"获取GPU内存信息失败: {e}")

            models[model_name] = model
            current_model = model

            # 关键：只在这里记录一次加载成功日志
            app.logger.info(f"模型加载成功: {model_name} (设备: {DETECTION_DEVICE})")

            return True

        except Exception as e:
            app.logger.error(f"模型加载失败: {e}")
            # 错误处理...

# ==================== 摄像头处理线程 ====================
def camera_processing_thread(camera_id=0):
    """摄像头实时处理线程"""
    global camera_running, current_model

    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"❌ 无法打开摄像头 {camera_id}")
        return

    print(f"✅ 摄像头 {camera_id} 已启动")

    while camera_running:
        ret, frame = cap.read()
        if not ret:
            break

        # 使用当前模型进行检测
        if current_model:
            try:
                results = current_model(frame, conf=0.25, iou=0.45)
                result_frame = results[0].plot()

                # 将处理后的帧转换为base64
                _, buffer = cv2.imencode('.jpg', result_frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')

                # 放入队列供流式传输使用
                try:
                    camera_queue.put_nowait(frame_base64)
                except:
                    pass  # 队列已满，跳过此帧

            except Exception as e:
                print(f"❌ 摄像头检测失败: {e}")

    cap.release()
    print("✅ 摄像头已停止")


# ==================== API路由 ====================
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    app.logger.info(f"用户注册开始 - 用户名: {username}")

    if not username or not password:
        app.logger.warning(f"注册失败 - 参数为空")
        return jsonify({"success": False, "message": "用户名和密码不能为空"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            app.logger.warning(f"注册失败 - 用户名已存在: {username}")
            return jsonify({"success": False, "message": "用户名已存在"}), 400

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                       (username, password))
        conn.commit()

        app.logger.info(f"注册成功 - 用户名: {username}")
        return jsonify({"success": True, "message": "注册成功"})

    except Exception as e:
        app.logger.error(f"注册异常 - 用户名: {username} - 错误: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "注册失败，请重试"}), 500
    finally:
        if conn:
            conn.close()
            app.logger.debug(f"数据库连接已关闭 - 注册接口")


# 在登录接口添加类似的日志
@app.route('/api/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    app.logger.info(f"用户登录尝试 - 用户名: {username}")

    if not username or not password:
        app.logger.warning(f"登录失败 - 参数为空")
        return jsonify({"success": False, "message": "用户名和密码不能为空"}), 400

    conn = None  # 在 try 外部先声明

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s",
                       (username, password))
        user = cursor.fetchone()

        if user:
            app.logger.info(f"登录成功 - 用户名: {username}")
            return jsonify({"success": True, "message": "登录成功"})
        else:
            app.logger.warning(f"登录失败 - 用户名或密码错误: {username}")
            return jsonify({"success": False, "message": "用户名或密码错误"}), 401

    except Exception as e:
        app.logger.error(f"登录异常 - 用户名: {username} - 错误: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": "服务器错误"}), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/models', methods=['GET'])
def get_models():
    """获取可用模型列表"""
    try:
        model_files = [f for f in os.listdir(MODEL_FOLDER)
                       if f.endswith('.pt') and os.path.isfile(os.path.join(MODEL_FOLDER, f))]
        return jsonify(model_files)
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
        return jsonify([])


@app.route('/api/detect', methods=['POST'])
def detect():
    """图片检测接口"""
    if 'image' not in request.files:
        return jsonify({"error": "未上传文件"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400

    # 获取参数
    model_name = request.form.get('model', os.getenv('DEFAULT_MODEL', 'best.pt'))
    conf_threshold = float(request.form.get('conf', os.getenv('CONF_THRESHOLD', '0.25')))
    iou_threshold = float(request.form.get('iou', os.getenv('IOU_THRESHOLD', '0.45')))

    # 添加GPU调试信息
    import torch
    app.logger.info(f"🔧 检测设备状态: CUDA可用={torch.cuda.is_available()}, 当前设备={DETECTION_DEVICE}")

    # 加载指定模型
    if not load_model(model_name):
        return jsonify({"error": f"模型 {model_name} 加载失败"}), 400

    if file and allowed_file(file.filename):
        # 保存上传的文件
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)

        # 读取图片
        img = cv2.imread(filepath)
        if img is None:
            return jsonify({"error": "无法读取图片"}), 400

        try:
            # 记录开始时间
            import time
            start_time = time.time()

            # 尝试GPU检测，如果失败则回退到CPU
            try:
                if DETECTION_DEVICE == "cpu":
                    app.logger.info("⚙️ 使用CPU进行检测")
                    results = current_model(img, conf=conf_threshold, iou=iou_threshold, device='cpu')
                else:
                    app.logger.info(f"🎮 尝试使用GPU进行检测: {DETECTION_DEVICE}")
                    results = current_model(img, conf=conf_threshold, iou=iou_threshold, device=DETECTION_DEVICE)
            except Exception as gpu_error:
                app.logger.warning(f"⚠️ GPU检测失败: {gpu_error}, 回退到CPU")
                # 强制重新加载模型到CPU
                load_model(model_name, force_cpu=True)
                results = current_model(img, conf=conf_threshold, iou=iou_threshold, device='cpu')

            # 记录结束时间
            end_time = time.time()
            process_time = end_time - start_time
            app.logger.info(f"✅ 检测完成, 耗时: {process_time:.2f}秒")

            # 绘制结果
            result_img = results[0].plot()

            # 保存结果图
            result_filename = f"{uuid.uuid4().hex}.jpg"
            result_filepath = os.path.join(RESULT_FOLDER, result_filename)
            cv2.imwrite(result_filepath, result_img)

            # 提取检测信息
            detections = []
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_name = current_model.names[cls_id]
                chinese_class = class_mapping.get(class_name, class_name)

                detections.append({
                    "class": chinese_class,
                    "confidence": round(confidence, 2),
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2
                })

            # 计算平均置信度
            avg_confidence = sum(d["confidence"] for d in detections) / len(detections) if detections else 0.0

            # 保存到数据库
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                           INSERT INTO detection_records
                           (filename, result_filename, model_used, confidence_avg, total_objects,
                            confidence_threshold, iou_threshold, detections, detection_type)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'image')
                           """, (
                unique_filename,
                result_filename,
                model_name,
                avg_confidence,
                len(detections),
                conf_threshold,
                iou_threshold,
                json.dumps(detections)
            ))
            conn.commit()
            record_id = cursor.lastrowid
            conn.close()

            # 生成URL
            original_url = f"/static/uploads/{unique_filename}"
            result_url = f"/static/results/{result_filename}"

            return jsonify({
                "success": True,
                "original": original_url,
                "result": result_url,
                "detections": detections,
                "record_id": record_id,
                "model_used": model_name,
                "confidence_threshold": conf_threshold,
                "iou_threshold": iou_threshold,
                "total_objects": len(detections),
                "avg_confidence": avg_confidence,
                "device_used": DETECTION_DEVICE,
                "process_time": round(process_time, 2)  # 添加处理时间
            })

        except Exception as e:
            app.logger.error(f"❌ 检测失败: {e}", exc_info=True)
            return jsonify({"success": False, "error": f"检测失败: {str(e)}"}), 500
    else:
        return jsonify({"success": False, "error": "不支持的文件格式"}), 400


@app.route('/api/detect_video', methods=['POST'])
def detect_video():
    """视频检测接口"""
    if 'video' not in request.files:
        return jsonify({"error": "未上传视频文件"}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "未选择视频文件"}), 400

    # 获取参数
    model_name = request.form.get('model', os.getenv('DEFAULT_MODEL', 'best.pt'))
    conf_threshold = float(request.form.get('conf', os.getenv('CONF_THRESHOLD', '0.25')))
    iou_threshold = float(request.form.get('iou', os.getenv('IOU_THRESHOLD', '0.45')))

    # 加载模型
    if not load_model(model_name):
        return jsonify({"error": f"模型 {model_name} 加载失败"}), 400

    if file and file.filename.lower().endswith(tuple(ALLOWED_VIDEO_EXTENSIONS)):
        # 保存上传的视频
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        video_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(video_path)

        try:
            # 打开视频文件
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return jsonify({"error": "无法打开视频文件"}), 400

            # 获取视频信息
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0

            # 准备输出视频
            processed_video_filename = f"processed_{uuid.uuid4().hex}.mp4"
            processed_video_path = os.path.join(RESULT_FOLDER, processed_video_filename)

            # 获取视频尺寸
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # 创建视频写入器
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(processed_video_path, fourcc, fps, (frame_width, frame_height))

            # 逐帧处理视频
            frame_number = 0
            total_detections = 0
            all_detections = []

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # 每10帧处理一次（加快处理速度）
                if frame_number % 10 == 0:
                    results = current_model(frame, conf=conf_threshold, iou=iou_threshold)
                    result_frame = results[0].plot()

                    # 统计检测结果
                    for box in results[0].boxes:
                        cls_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        class_name = current_model.names[cls_id]
                        chinese_class = class_mapping.get(class_name, class_name)

                        all_detections.append({
                            "frame": frame_number,
                            "class": chinese_class,
                            "confidence": round(confidence, 2)
                        })
                        total_detections += 1
                else:
                    result_frame = frame

                out.write(result_frame)
                frame_number += 1

                # 进度提示
                if frame_number % 100 == 0:
                    print(f"✅ 已处理 {frame_number}/{frame_count} 帧")

            # 释放资源
            cap.release()
            out.release()

            # 计算平均置信度
            avg_confidence = sum(d["confidence"] for d in all_detections) / len(
                all_detections) if all_detections else 0.0

            # 保存到数据库
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                           INSERT INTO detection_records
                           (filename, result_filename, video_path, processed_video_path, model_used,
                            confidence_avg, total_objects, confidence_threshold, iou_threshold,
                            detections, detection_type, duration, frame_count, fps)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'video', %s, %s, %s)
                           """, (
                               unique_filename,
                               processed_video_filename,
                               unique_filename,
                               processed_video_filename,
                               model_name,
                               avg_confidence,
                               total_detections,
                               conf_threshold,
                               iou_threshold,
                               json.dumps(all_detections),
                               duration,
                               frame_number,
                               fps
                           ))
            conn.commit()
            record_id = cursor.lastrowid
            conn.close()

            # 生成URL
            video_url = f"/static/uploads/{unique_filename}"
            processed_video_url = f"/static/results/{processed_video_filename}"

            return jsonify({
                "success": True,
                "video_url": video_url,
                "processed_video_url": processed_video_url,
                "total_frames": frame_number,
                "total_detections": total_detections,
                "avg_confidence": avg_confidence,
                "duration": round(duration, 2),
                "fps": round(fps, 2),
                "record_id": record_id,
                "model_used": model_name
            })

        except Exception as e:
            print(f"❌ 视频检测失败: {e}")
            return jsonify({"success": False, "error": f"视频检测失败: {str(e)}"}), 500
    else:
        return jsonify({"success": False, "error": "不支持的视频格式"}), 400


@app.route('/api/device_info', methods=['GET'])
def get_device_info():
    """获取当前设备信息"""
    try:
        import torch

        devices = []

        # CPU信息
        cpu_info = {
            "type": "CPU",
            "name": "CPU",
            "available": True,
            "default": True
        }
        devices.append(cpu_info)

        # GPU信息
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                gpu_info = {
                    "type": "GPU",
                    "name": torch.cuda.get_device_name(i),
                    "index": i,
                    "memory_total": torch.cuda.get_device_properties(i).total_memory / (1024 ** 3),  # GB
                    "memory_used": torch.cuda.memory_allocated(i) / (1024 ** 3),  # GB
                    "available": True
                }
                devices.append(gpu_info)

        # PyTorch版本
        pytorch_version = torch.__version__

        # 当前设备
        current_device = DETECTION_DEVICE if DETECTION_DEVICE else "未设置"

        return jsonify({
            "success": True,
            "devices": devices,
            "pytorch_version": pytorch_version,
            "current_device": current_device,
            "cuda_available": torch.cuda.is_available()
        })

    except Exception as e:
        print(f"❌ 获取设备信息失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "devices": [{"type": "CPU", "name": "CPU", "available": True}]
        })


@app.route('/api/switch_device', methods=['POST'])
def switch_device():
    """切换检测设备"""
    global DETECTION_DEVICE, models, current_model

    data = request.json
    device_type = data.get('device_type', 'auto')  # 'cpu', 'gpu', 'auto'

    try:
        import torch

        old_device = DETECTION_DEVICE

        # 如果已经在该设备上，直接返回
        if device_type == 'cpu' and old_device == 'cpu':
            return jsonify({
                "success": True,
                "message": f"已在CPU模式",
                "device": DETECTION_DEVICE
            })

        if device_type == 'gpu' and old_device != 'cpu':
            return jsonify({
                "success": True,
                "message": f"已在GPU模式",
                "device": DETECTION_DEVICE
            })

        if device_type == 'cpu':
            DETECTION_DEVICE = "cpu"
            print("✅ 切换到CPU模式")

        elif device_type == 'gpu':
            if torch.cuda.is_available():
                DETECTION_DEVICE = "cuda:0"
                print("✅ 切换到GPU模式")
            else:
                return jsonify({
                    "success": False,
                    "error": "GPU不可用"
                }), 400

        elif device_type == 'auto':
            # 只在未设置时才自动选择
            if DETECTION_DEVICE is None:
                DETECTION_DEVICE = get_available_device()
                print(f"✅ 自动选择设备: {DETECTION_DEVICE}")
            else:
                print(f"ℹ️ 设备已设置为: {DETECTION_DEVICE}")
                return jsonify({
                    "success": True,
                    "message": f"设备已设置为 {DETECTION_DEVICE}",
                    "device": DETECTION_DEVICE
                })

        else:
            return jsonify({
                "success": False,
                "error": "无效的设备类型"
            }), 400

        # 如果模型已加载，移动到新设备
        if current_model and old_device != DETECTION_DEVICE:
            try:
                current_model.to(DETECTION_DEVICE)
                # 更新所有已加载模型
                for name, model in models.items():
                    model.to(DETECTION_DEVICE)
                print(f"✅ 模型已移动到 {DETECTION_DEVICE}")
            except Exception as e:
                print(f"⚠️ 模型移动失败: {e}")
                # 回退到CPU
                DETECTION_DEVICE = "cpu"
                if current_model:
                    current_model.to("cpu")

        return jsonify({
            "success": True,
            "message": f"已切换到 {DETECTION_DEVICE}",
            "device": DETECTION_DEVICE
        })

    except Exception as e:
        print(f"❌ 切换设备失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/camera/start', methods=['POST'])
def start_camera():
    """启动摄像头检测"""
    global camera_thread, camera_running

    if camera_running:
        return jsonify({"success": False, "message": "摄像头已在运行"}), 400

    camera_id = request.json.get('camera_id', 0)
    camera_running = True

    # 启动摄像头处理线程
    camera_thread = threading.Thread(target=camera_processing_thread, args=(camera_id,))
    camera_thread.daemon = True
    camera_thread.start()

    return jsonify({
        "success": True,
        "message": "摄像头已启动",
        "stream_url": "/api/camera/stream"
    })


@app.route('/api/camera/stop', methods=['POST'])
def stop_camera():
    """停止摄像头检测"""
    global camera_running

    if not camera_running:
        return jsonify({"success": False, "message": "摄像头未运行"}), 400

    camera_running = False
    time.sleep(1)  # 等待线程结束

    # 清空队列
    while not camera_queue.empty():
        camera_queue.get()

    return jsonify({"success": True, "message": "摄像头已停止"})


@app.route('/api/camera/stream')
def camera_stream():
    """摄像头视频流"""

    def generate():
        while camera_running:
            try:
                frame_base64 = camera_queue.get(timeout=1)
                yield f"data: {frame_base64}\n\n"
            except:
                pass

    return Response(generate(), mimetype='text/event-stream')


# 在 app.py 中修改 /api/history 接口
@app.route('/api/history', methods=['GET'])
def get_history():
    """获取历史检测记录"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()  # 这里修复cursor未解析引用的问题

        # 查询所有历史记录，按检测时间倒序排列
        sql = """
              SELECT * \
              FROM detection_records
              ORDER BY detect_time DESC \
              """
        cursor.execute(sql)
        records = cursor.fetchall()

        cursor.close()
        connection.close()

        # 转换datetime对象为字符串格式
        for record in records:
            if record.get('detect_time') and isinstance(record['detect_time'], datetime.datetime):
                record['detect_time'] = record['detect_time'].isoformat()

        return jsonify(records)

    except Exception as e:
        app.logger.error(f"获取历史记录失败: {e}")
        return jsonify({
            'error': '获取历史记录失败',
            'message': str(e)
        }), 500


@app.route('/api/records/<int:record_id>', methods=['GET'])
def get_record_detail(record_id):
    """获取单条记录的详细信息"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 查询记录基本信息
        sql = "SELECT * FROM detection_records WHERE id = %s"
        cursor.execute(sql, (record_id,))
        record = cursor.fetchone()

        if not record:
            cursor.close()
            connection.close()
            return jsonify({'error': '记录不存在'}), 404

        # 如果detect_time是datetime对象，转换为字符串
        if record.get('detect_time') and isinstance(record['detect_time'], datetime.datetime):
            record['detect_time'] = record['detect_time'].isoformat()

        # 尝试从detections字段解析检测详情
        detections = []
        if record.get('detections'):
            try:
                # 如果detections字段是JSON字符串，解析它
                if isinstance(record['detections'], str):
                    detections = json.loads(record['detections'])
                elif isinstance(record['detections'], list):
                    detections = record['detections']
            except json.JSONDecodeError:
                app.logger.warning(f"记录 {record_id} 的detections字段JSON解析失败")
                detections = []

        cursor.close()
        connection.close()

        return jsonify({
            'record': record,
            'detections': detections
        })

    except Exception as e:
        app.logger.error(f"获取记录详情失败: {e}")
        return jsonify({
            'error': '获取记录详情失败',
            'message': str(e)
        }), 500


@app.route('/api/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除单条记录"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查记录是否存在
        cursor.execute("SELECT filename, result_filename FROM detection_records WHERE id = %s", (record_id,))
        record = cursor.fetchone()

        if not record:
            return jsonify({"success": False, "message": "记录不存在"}), 404

        # 删除文件（可选）
        try:
            if record[0]:  # 原始文件
                original_path = os.path.join(UPLOAD_FOLDER, record[0])
                if os.path.exists(original_path):
                    os.remove(original_path)

            if record[1]:  # 结果文件
                result_path = os.path.join(RESULT_FOLDER, record[1])
                if os.path.exists(result_path):
                    os.remove(result_path)
        except Exception as e:
            print(f"⚠️ 删除文件失败: {e}")

        # 删除数据库记录
        cursor.execute("DELETE FROM detection_records WHERE id = %s", (record_id,))
        conn.commit()

        return jsonify({"success": True, "message": "记录删除成功"})

    except Exception as e:
        print(f"❌ 删除记录失败: {e}")
        return jsonify({"success": False, "message": "删除记录失败"}), 500
    finally:
        if conn:
            conn.close()


@app.route('/api/records/batch_delete', methods=['POST'])
def batch_delete_records():
    """批量删除记录"""
    data = request.json
    record_ids = data.get('record_ids', [])

    if not record_ids:
        return jsonify({"success": False, "message": "未提供记录ID"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 构建查询条件
        placeholders = ','.join(['%s'] * len(record_ids))
        query = f"SELECT id, filename, result_filename FROM detection_records WHERE id IN ({placeholders})"
        cursor.execute(query, record_ids)
        records = cursor.fetchall()

        # 删除文件
        deleted_files = []
        for record in records:
            try:
                # 删除原始文件
                if record[1]:  # filename
                    original_path = os.path.join(UPLOAD_FOLDER, record[1])
                    if os.path.exists(original_path):
                        os.remove(original_path)
                        deleted_files.append(f"原始文件: {record[1]}")

                # 删除结果文件
                if record[2]:  # result_filename
                    result_path = os.path.join(RESULT_FOLDER, record[2])
                    if os.path.exists(result_path):
                        os.remove(result_path)
                        deleted_files.append(f"结果文件: {record[2]}")
            except Exception as e:
                print(f"⚠️ 删除文件失败 (ID: {record[0]}): {e}")
                # 继续处理，不中断批量删除

        # 批量删除数据库记录
        delete_query = f"DELETE FROM detection_records WHERE id IN ({placeholders})"
        cursor.execute(delete_query, record_ids)
        conn.commit()

        deleted_count = cursor.rowcount

        return jsonify({
            "success": True,
            "message": f"批量删除完成",
            "deleted_count": deleted_count,
            "deleted_files": deleted_files
        })

    except Exception as e:
        print(f"❌ 批量删除失败: {e}")
        if conn:
            conn.rollback()
        return jsonify({"success": False, "message": f"批量删除失败: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()


# ==================== 静态文件路由 ====================
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    ext = filename.rsplit('.', 1)[-1].lower()
    mime_type = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'mp4': 'video/mp4',
        'avi': 'video/x-msvideo',
        'mov': 'video/quicktime',
        'mkv': 'video/x-matroska'
    }.get(ext, 'application/octet-stream')

    return send_from_directory(UPLOAD_FOLDER, filename, mimetype=mime_type)


@app.route('/static/results/<filename>')
def result_file(filename):
    """提供结果文件"""
    ext = filename.rsplit('.', 1)[-1].lower()
    mime_type = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'mp4': 'video/mp4'
    }.get(ext, 'application/octet-stream')

    return send_from_directory(RESULT_FOLDER, filename, mimetype=mime_type)


@app.route('/api/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    import torch
    import psutil

    try:
        status = {
            "success": True,
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
            },
            "pytorch": {
                "version": torch.__version__,
                "cuda_available": torch.cuda.is_available(),
                "cuda_version": torch.version.cuda if torch.cuda.is_available() else "N/A",
            },
            "detection": {
                "device": DETECTION_DEVICE,
                "model_loaded": current_model is not None,
                "model_name": list(models.keys())[0] if models else None,
            },
            "service": {
                "flask_port": APP_PORT,
                "upload_folder": os.path.abspath(UPLOAD_FOLDER),
                "result_folder": os.path.abspath(RESULT_FOLDER),
            }
        }

        # 添加GPU信息
        if torch.cuda.is_available():
            status["gpu"] = []
            for i in range(torch.cuda.device_count()):
                gpu_info = {
                    "index": i,
                    "name": torch.cuda.get_device_name(i),
                    "memory_allocated": torch.cuda.memory_allocated(i) / 1024 ** 3,
                    "memory_reserved": torch.cuda.memory_reserved(i) / 1024 ** 3,
                    "memory_total": torch.cuda.get_device_properties(i).total_memory / 1024 ** 3,
                }
                status["gpu"].append(gpu_info)

        return jsonify(status)

    except Exception as e:
        app.logger.error(f"❌ 获取系统状态失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== 日志API接口 ====================
@app.route('/api/logs', methods=['POST'])
def receive_client_logs():
    """接收前端批量日志"""
    try:
        data = request.json
        logs = data.get('logs', [])

        for log in logs:
            level = log.get('level', 'INFO')
            message = log.get('message', '')
            timestamp = log.get('timestamp', '')

            # 根据日志级别记录到后端日志
            log_message = f"前端日志 - [{level}] {timestamp}: {message}"

            if level == 'ERROR':
                app.logger.error(log_message, extra={
                    'frontend_data': log.get('data', {}),
                    'url': log.get('url', ''),
                    'user_agent': log.get('userAgent', '')
                })
            elif level == 'WARN':
                app.logger.warning(log_message, extra={
                    'frontend_data': log.get('data', {}),
                    'url': log.get('url', ''),
                    'user_agent': log.get('userAgent', '')
                })
            elif level == 'DEBUG':
                app.logger.debug(log_message, extra={
                    'frontend_data': log.get('data', {})
                })
            else:
                app.logger.info(log_message, extra={
                    'frontend_data': log.get('data', {}),
                    'url': log.get('url', '')
                })

        return jsonify({"success": True, "received": len(logs)})

    except Exception as e:
        app.logger.error(f"处理前端日志失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/logs/batch', methods=['POST'])
def receive_client_logs_batch():
    """接收前端批量日志（兼容旧版本）"""
    try:
        data = request.json
        logs = data.get('logs', [])

        # 只记录ERROR级别的日志
        error_logs = [log for log in logs if log.get('level') == 'ERROR']

        for log in error_logs:
            level = log.get('level', 'INFO')
            message = log.get('message', '')
            timestamp = log.get('timestamp', '')

            log_message = f"前端日志 - [{level}] {timestamp}: {message}"

            if level == 'ERROR':
                app.logger.error(log_message, extra={
                    'username': log.get('data', {}).get('username'),
                    'url': log.get('url', ''),
                    'errorCode': log.get('data', {}).get('errorCode')
                })

        return jsonify({"success": True, "received": len(logs), "processed": len(error_logs)})
    except Exception as e:
        app.logger.error(f"处理批量日志失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

# 原有的单个日志接口可以保留或删除
@app.route('/api/log', methods=['POST'])
def receive_client_log():
    """接收前端单个日志（兼容旧版本）"""
    try:
        log_data = request.json
        app.logger.info(f"前端日志 - 级别: {log_data.get('level')} - "
                        f"消息: {log_data.get('message')} - "
                        f"数据: {log_data.get('data')}")
        return jsonify({"success": True})
    except Exception as e:
        app.logger.error(f"处理前端日志失败: {str(e)}")
        return jsonify({"success": False}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()

        return jsonify({
            "status": "healthy",
            "service": "yolov11-insulator-detection",
            "timestamp": datetime.datetime.now().isoformat(),
            "database": "connected",
            "model_loaded": current_model is not None,
            "device": DETECTION_DEVICE
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


# ==================== 主程序 ====================
if __name__ == '__main__':
    # 初始化日志系统（确保只配置一次）
    setup_logging()

    # 记录启动信息（统一使用app.logger）
    app.logger.info("[启动] YOLOv11绝缘子缺陷检测系统后端启动")

    # 获取IP地址信息
    import socket

    hostname = socket.gethostname()
    ip_list = socket.gethostbyname_ex(hostname)[2]

    app.logger.info(f"[主机]主机名: {hostname}")
    for ip in ip_list:
        app.logger.info(f"[IP]服务器IP: {ip}:{APP_PORT}")

    app.logger.info(f"[目录]上传目录: {os.path.abspath(UPLOAD_FOLDER)}")
    app.logger.info(f"[目录]结果目录: {os.path.abspath(RESULT_FOLDER)}")

    # 检测设备（使用统一日志）
    import torch

    app.logger.info(f"[工具]PyTorch版本: {torch.__version__}")

    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            app.logger.info(f"[设备]GPU {i}: {torch.cuda.get_device_name(i)}")
        DETECTION_DEVICE = "cuda:0"
    else:
        app.logger.info("[错误]未检测到GPU，使用CPU模式")
        DETECTION_DEVICE = "cpu"

    # 初始化数据库（简化日志）
    try:
        create_tables()
        app.logger.info("[成功]数据库初始化成功")
    except Exception as e:
        app.logger.error(f"[错误]数据库初始化失败: {e}")

    # 加载默认模型
    default_model = os.getenv('DEFAULT_MODEL', 'best.pt')
    model_path = os.path.join(MODEL_FOLDER, default_model)

    if os.path.exists(model_path):
        if load_model(default_model):
            # 不重复记录成功日志，已在load_model中记录
            pass
        else:
            app.logger.error(f"[警告]默认模型加载失败: {model_path}")
    else:
        app.logger.error(f"[警告]默认模型不存在: {model_path}")

    # 启动内存监控
    try:
        memory_thread = threading.Thread(target=memory_monitor, daemon=True)
        memory_thread.start()
        app.logger.info("[成功]内存监控已启动（每2分钟检测一次）")
    except Exception as e:
        app.logger.error(f"[错误]内存监控启动失败: {e}")

    # 启动服务器
    host = '0.0.0.0'

    # 尝试获取环境变量端口，如果被占用则查找可用端口
    desired_port = int(os.environ.get('PORT', APP_PORT))
    actual_port = find_available_port(desired_port, 10)

    if actual_port is None:
        app.logger.error(f"❌ 无法找到可用端口（尝试{desired_port}到{desired_port + 9}）")
        exit(1)

    if actual_port != desired_port:
        app.logger.warning(f"⚠️ 端口{desired_port}被占用，使用备用端口{actual_port}")

    app.logger.info(f"服务启动在: {host}:{actual_port}")

    app.logger.info("-" * 50)

    # ============================ 系统信息 ============================

    print("\n" + "=" * 50)
    print("🚀 YOLOv11绝缘子缺陷检测系统启动")
    print("=" * 50)

    # print(f"🌐 内网地址: http://172.19.20.152:{port}")
    # print(f"🌐 公网地址: http://8.163.2.84:{port}")
    # print(f"🌐 内网地址: http://10.33.57.83:{port}")  # 修改为新的内网IP
    # print(f"🌐 VPN地址: http://100.78.250.8:{port}")  # 添加Tailscale VPN地址

    print(f"📡 本地地址: http://localhost:{actual_port}")
    for ip in ip_list:
        print(f"🌐 内网地址: http://{ip}:{actual_port}")

    # print(f"🌐 内网地址: {ip_list}:{port}")
    print(f"📁 上传目录: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"📁 结果目录: {os.path.abspath(RESULT_FOLDER)}")
    print(f"🔧 检测设备: {DETECTION_DEVICE}")
    print("=" * 50 + "\n")

    # 启动服务器
    app.run(host=host, port=actual_port, debug=False, threaded=True, use_reloader=False)