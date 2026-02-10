import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import os
import sys
import time
from datetime import datetime
import json
import webbrowser
import locale


class ServiceLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("前后端服务启动器 v2.0")
        self.root.geometry("900x700")

        # 设置样式
        self.setup_styles()

        # 日志目录
        self.logs_dir = r"D:\project\start_logs"
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        # 配置文件路径
        self.config_file = os.path.join(os.path.dirname(__file__), "launcher_config.json")

        # 加载配置
        self.config = self.load_config()

        # 获取系统编码
        self.system_encoding = locale.getpreferredencoding() or 'gbk'
        self.log_message(f"系统编码检测为: {self.system_encoding}", "系统")

        # 后端进程和前端进程
        self.backend_process = None
        self.frontend_process = None

        # 服务状态
        self.backend_running = False
        self.frontend_running = False

        # 日志文件
        self.backend_log_file = None
        self.frontend_log_file = None

        # 创建UI
        self.create_widgets()

        # 窗口关闭时清理资源
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 启动时检查服务状态
        self.root.after(1000, self.check_services_on_startup)

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')

        # 自定义颜色
        self.root.configure(bg='#f0f0f0')

        # 按钮样式
        style.configure('Success.TButton', foreground='green')
        style.configure('Danger.TButton', foreground='red')
        style.configure('Info.TButton', foreground='blue')

    def load_config(self):
        """加载配置"""
        default_config = {
            "backend_path": r"D:\project\start_backend.bat",
            "frontend_path": r"D:\project\start_frontend.bat",
            "auto_start": False,
            "log_retention_days": 7,
            "backend_port": 5000,
            "frontend_port": 5173
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置，保留默认值
                    default_config.update(loaded_config)
            except:
                pass

        return default_config

    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except:
            pass

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 顶部标题栏
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(
            title_frame,
            text="前后端服务启动器",
            font=("微软雅黑", 18, "bold"),
            foreground="#2c3e50"
        )
        title_label.pack(side=tk.LEFT)

        # 版本标签
        version_label = ttk.Label(
            title_frame,
            text="v2.0",
            font=("微软雅黑", 10),
            foreground="#7f8c8d"
        )
        version_label.pack(side=tk.RIGHT, padx=5)

        # 状态指示器框架
        status_frame = ttk.LabelFrame(main_frame, text="服务状态", padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        # 使用网格布局状态指示器
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill=tk.X)

        # 后端状态
        backend_status_frame = ttk.Frame(status_grid)
        backend_status_frame.grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)

        self.backend_status_indicator = tk.Canvas(
            backend_status_frame,
            width=24,
            height=24,
            highlightthickness=0
        )
        self.backend_status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.draw_status_indicator(self.backend_status_indicator, "stopped")

        backend_status_text = ttk.Frame(backend_status_frame)
        backend_status_text.pack(side=tk.LEFT)

        self.backend_status_label = ttk.Label(
            backend_status_text,
            text="后端服务",
            font=("微软雅黑", 11, "bold")
        )
        self.backend_status_label.pack(anchor=tk.W)

        self.backend_detail_label = ttk.Label(
            backend_status_text,
            text="状态: 已停止",
            font=("微软雅黑", 9),
            foreground="#7f8c8d"
        )
        self.backend_detail_label.pack(anchor=tk.W)

        # 前端状态
        frontend_status_frame = ttk.Frame(status_grid)
        frontend_status_frame.grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)

        self.frontend_status_indicator = tk.Canvas(
            frontend_status_frame,
            width=24,
            height=24,
            highlightthickness=0
        )
        self.frontend_status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self.draw_status_indicator(self.frontend_status_indicator, "stopped")

        frontend_status_text = ttk.Frame(frontend_status_frame)
        frontend_status_text.pack(side=tk.LEFT)

        self.frontend_status_label = ttk.Label(
            frontend_status_text,
            text="前端服务",
            font=("微软雅黑", 11, "bold")
        )
        self.frontend_status_label.pack(anchor=tk.W)

        self.frontend_detail_label = ttk.Label(
            frontend_status_text,
            text="状态: 已停止",
            font=("微软雅黑", 9),
            foreground="#7f8c8d"
        )
        self.frontend_detail_label.pack(anchor=tk.W)

        # 分隔线
        separator = ttk.Separator(status_grid, orient='vertical')
        separator.grid(row=0, column=2, padx=20, pady=5, sticky='ns')

        # 快速链接
        links_frame = ttk.Frame(status_grid)
        links_frame.grid(row=0, column=3, padx=20, pady=5, sticky=tk.W)

        links_label = ttk.Label(
            links_frame,
            text="快速访问",
            font=("微软雅黑", 11, "bold")
        )
        links_label.pack(anchor=tk.W, pady=(0, 5))

        # 后端链接按钮
        self.backend_link_btn = ttk.Button(
            links_frame,
            text="打开后端 (localhost:5000)",
            command=lambda: self.open_url(f"http://localhost:{self.config['backend_port']}"),
            width=25,
            style='Info.TButton'
        )
        self.backend_link_btn.pack(anchor=tk.W, pady=2)
        self.backend_link_btn.state(['disabled'])

        # 前端链接按钮
        self.frontend_link_btn = ttk.Button(
            links_frame,
            text="打开前端 (localhost:5173)",
            command=lambda: self.open_url(f"http://localhost:{self.config['frontend_port']}"),
            width=25,
            style='Info.TButton'
        )
        self.frontend_link_btn.pack(anchor=tk.W, pady=2)
        self.frontend_link_btn.state(['disabled'])

        # 控制按钮框架
        control_frame = ttk.LabelFrame(main_frame, text="服务控制", padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # 第一行按钮
        button_row1 = ttk.Frame(control_frame)
        button_row1.pack(fill=tk.X, pady=(0, 10))

        self.start_backend_btn = ttk.Button(
            button_row1,
            text="▶ 启动后端服务",
            command=self.start_backend,
            width=18,
            style='Success.TButton'
        )
        self.start_backend_btn.pack(side=tk.LEFT, padx=5)

        self.stop_backend_btn = ttk.Button(
            button_row1,
            text="■ 停止后端服务",
            command=self.stop_backend,
            width=18,
            state=tk.DISABLED,
            style='Danger.TButton'
        )
        self.stop_backend_btn.pack(side=tk.LEFT, padx=5)

        self.start_frontend_btn = ttk.Button(
            button_row1,
            text="▶ 启动前端服务",
            command=self.start_frontend,
            width=18,
            style='Success.TButton'
        )
        self.start_frontend_btn.pack(side=tk.LEFT, padx=5)

        self.stop_frontend_btn = ttk.Button(
            button_row1,
            text="■ 停止前端服务",
            command=self.stop_frontend,
            width=18,
            state=tk.DISABLED,
            style='Danger.TButton'
        )
        self.stop_frontend_btn.pack(side=tk.LEFT, padx=5)

        # 第二行按钮
        button_row2 = ttk.Frame(control_frame)
        button_row2.pack(fill=tk.X)

        self.start_all_btn = ttk.Button(
            button_row2,
            text="▶ 一键启动所有服务",
            command=self.start_all_services,
            width=25,
            style='Success.TButton'
        )
        self.start_all_btn.pack(side=tk.LEFT, padx=5)

        self.stop_all_btn = ttk.Button(
            button_row2,
            text="■ 一键停止所有服务",
            command=self.stop_all_services,
            width=25,
            state=tk.DISABLED,
            style='Danger.TButton'
        )
        self.stop_all_btn.pack(side=tk.LEFT, padx=5)

        self.open_logs_btn = ttk.Button(
            button_row2,
            text="📁 打开日志目录",
            command=self.open_logs_directory,
            width=18
        )
        self.open_logs_btn.pack(side=tk.RIGHT, padx=5)

        # 日志输出框
        log_frame = ttk.LabelFrame(main_frame, text="实时日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 日志工具栏
        log_toolbar = ttk.Frame(log_frame)
        log_toolbar.pack(fill=tk.X, pady=(0, 5))

        # 日志筛选
        filter_label = ttk.Label(log_toolbar, text="筛选:")
        filter_label.pack(side=tk.LEFT, padx=(0, 5))

        self.log_filter_var = tk.StringVar(value="all")
        filter_options = ["全部", "后端", "前端", "系统"]
        for option in filter_options:
            rb = ttk.Radiobutton(
                log_toolbar,
                text=option,
                variable=self.log_filter_var,
                value=option.lower(),
                command=self.filter_logs
            )
            rb.pack(side=tk.LEFT, padx=2)

        ttk.Separator(log_toolbar, orient='vertical').pack(side=tk.LEFT, padx=10, fill='y')

        # 清空日志按钮
        clear_log_btn = ttk.Button(
            log_toolbar,
            text="清空日志",
            command=self.clear_log,
            width=10
        )
        clear_log_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 保存日志按钮
        save_log_btn = ttk.Button(
            log_toolbar,
            text="保存日志",
            command=self.save_current_log,
            width=10
        )
        save_log_btn.pack(side=tk.RIGHT, padx=5)

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=100,
            height=20,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#ffffff"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 底部状态栏
        statusbar = ttk.Frame(main_frame, relief=tk.SUNKEN)
        statusbar.pack(fill=tk.X, pady=(0, 5))

        self.status_label = ttk.Label(
            statusbar,
            text="就绪",
            font=("微软雅黑", 9),
            foreground="#2c3e50"
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=2)

        # 日志文件信息
        self.log_info_label = ttk.Label(
            statusbar,
            text="",
            font=("微软雅黑", 9),
            foreground="#7f8c8d"
        )
        self.log_info_label.pack(side=tk.RIGHT, padx=10, pady=2)

    def draw_status_indicator(self, canvas, status):
        """绘制状态指示灯"""
        canvas.delete("all")

        # 不同状态的颜色
        colors = {
            "stopped": "#e74c3c",  # 红色
            "starting": "#f39c12",  # 橙色
            "running": "#2ecc71",  # 绿色
            "error": "#e74c3c"  # 红色
        }

        color = colors.get(status, "#95a5a6")

        # 绘制指示灯
        canvas.create_oval(2, 2, 22, 22, fill=color, outline="", width=0)

        # 添加发光效果
        canvas.create_oval(4, 4, 20, 20, fill=color, outline="", width=0)

        if status == "running":
            # 添加运行中的动画效果
            canvas.create_oval(6, 6, 18, 18, fill="#ffffff", outline="", width=0, stipple="gray50")

    def filter_logs(self):
        """筛选日志"""
        filter_value = self.log_filter_var.get()
        # 这里可以实现日志筛选逻辑
        self.log_message(f"切换到 {filter_value} 日志视图", "系统")

    def log_message(self, message, service=None, level="info"):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 等级颜色
        colors = {
            "info": "#d4d4d4",
            "success": "#2ecc71",
            "warning": "#f39c12",
            "error": "#e74c3c",
            "debug": "#3498db"
        }

        color = colors.get(level, "#d4d4d4")

        if service:
            prefix = f"[{service}] "
        else:
            prefix = ""

        log_entry = f"[{timestamp}] {prefix}{message}\n"

        # 在主线程中更新UI
        self.root.after(0, self._update_log, log_entry, color)

        # 同时写入日志文件
        if service == "后端" and self.backend_log_file:
            try:
                self.backend_log_file.write(f"[{timestamp}] {message}\n")
                self.backend_log_file.flush()
            except Exception as e:
                print(f"写入后端日志失败: {e}")
        elif service == "前端" and self.frontend_log_file:
            try:
                self.frontend_log_file.write(f"[{timestamp}] {message}\n")
                self.frontend_log_file.flush()
            except Exception as e:
                print(f"写入前端日志失败: {e}")

    def _update_log(self, log_entry, color):
        """在UI线程中更新日志"""
        # 保存当前滚动位置
        scroll_pos = self.log_text.yview()

        # 插入带颜色的文本
        self.log_text.insert(tk.END, log_entry)

        # 标记最后一行
        start_index = f"{int(self.log_text.index('end-1c').split('.')[0]) - 1}.0"
        end_index = "end-1c"

        # 应用标签颜色
        tag_name = f"color_{color.replace('#', '')}"
        self.log_text.tag_configure(tag_name, foreground=color)
        self.log_text.tag_add(tag_name, start_index, end_index)

        # 恢复滚动位置并滚动到底部
        self.log_text.yview_moveto(scroll_pos[0])
        self.log_text.see(tk.END)

    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)

    def update_log_info(self, message):
        """更新日志信息"""
        self.log_info_label.config(text=message)

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("日志已清空", "系统")

    def save_current_log(self):
        """保存当前日志到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gui_log_{timestamp}.txt"
        filepath = os.path.join(self.logs_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log_message(f"日志已保存到: {filename}", "系统", "success")
        except Exception as e:
            self.log_message(f"保存日志失败: {str(e)}", "系统", "error")

    def open_logs_directory(self):
        """打开日志目录"""
        try:
            os.startfile(self.logs_dir)
            self.log_message(f"已打开日志目录: {self.logs_dir}", "系统")
        except Exception as e:
            self.log_message(f"打开日志目录失败: {str(e)}", "系统", "error")

    def open_url(self, url):
        """打开URL"""
        try:
            webbrowser.open(url)
            self.log_message(f"已打开: {url}", "系统")
        except Exception as e:
            self.log_message(f"打开URL失败: {str(e)}", "系统", "error")

    def create_log_file(self, service_name):
        """创建日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{service_name}_{timestamp}.log"
        filepath = os.path.join(self.logs_dir, filename)

        try:
            log_file = open(filepath, 'w', encoding='utf-8')
            log_file.write(f"{service_name} 服务启动日志 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write("=" * 50 + "\n\n")
            return log_file, filename
        except Exception as e:
            self.log_message(f"创建日志文件失败: {str(e)}", "系统", "error")
            return None, None

    def start_backend(self):
        """启动后端服务"""
        if self.backend_running:
            self.log_message("后端服务已经在运行中", "后端", "warning")
            return

        self.log_message("正在启动后端服务...", "后端")
        self.update_status("正在启动后端服务...")

        # 创建日志文件
        self.backend_log_file, log_filename = self.create_log_file("backend")
        if self.backend_log_file:
            self.update_log_info(f"后端日志: {log_filename}")

        # 更新状态
        self.backend_running = True
        self.backend_detail_label.config(text="状态: 启动中...")
        self.draw_status_indicator(self.backend_status_indicator, "starting")

        # 启用/禁用按钮
        self.start_backend_btn.config(state=tk.DISABLED)
        self.stop_backend_btn.config(state=tk.NORMAL)
        self.start_all_btn.config(state=tk.DISABLED)
        self.backend_link_btn.state(['!disabled'])

        # 在新的线程中启动服务
        thread = threading.Thread(target=self._run_backend, daemon=True)
        thread.start()

    def _run_backend(self):
        """运行后端服务的实际代码"""
        try:
            backend_bat_path = self.config["backend_path"]

            # 检查文件是否存在
            if not os.path.exists(backend_bat_path):
                self.log_message(f"错误: 找不到后端启动文件 {backend_bat_path}", "后端", "error")
                self.root.after(0, self._backend_start_failed, "找不到启动文件")
                return

            self.log_message(f"执行启动脚本: {backend_bat_path}", "后端")

            # 启动后端服务 - 使用系统编码
            self.backend_process = subprocess.Popen(
                ["cmd", "/k", backend_bat_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False,  # 不使用文本模式，我们自己解码
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            # 标记为运行中
            self.root.after(0, self._backend_started)

            # 读取输出 - 使用系统编码解码
            while True:
                line = self.backend_process.stdout.readline()
                if not line and self.backend_process.poll() is not None:
                    break
                if line:
                    try:
                        # 尝试用系统编码解码
                        decoded_line = line.decode(self.system_encoding, errors='replace').rstrip('\n\r')
                        self.log_message(decoded_line, "后端")
                    except Exception as decode_error:
                        # 如果解码失败，尝试其他编码
                        try:
                            decoded_line = line.decode('utf-8', errors='replace').rstrip('\n\r')
                            self.log_message(decoded_line, "后端")
                        except:
                            self.log_message(f"[二进制数据，无法解码]", "后端")

            # 进程结束
            self.root.after(0, self._backend_stopped)

        except Exception as e:
            self.log_message(f"启动后端服务时出错: {str(e)}", "后端", "error")
            self.root.after(0, self._backend_start_failed, str(e))

    def _backend_started(self):
        """后端服务启动成功"""
        self.draw_status_indicator(self.backend_status_indicator, "running")
        self.backend_detail_label.config(text="状态: 运行中")
        self.log_message("后端服务启动成功", "后端", "success")
        self.update_status(f"后端服务运行中 - http://localhost:{self.config['backend_port']}")
        self.start_all_btn.config(state=tk.DISABLED)
        self.stop_all_btn.config(state=tk.NORMAL)

    def _backend_start_failed(self, error_msg):
        """后端服务启动失败"""
        self.backend_running = False
        self.backend_detail_label.config(text="状态: 启动失败")
        self.draw_status_indicator(self.backend_status_indicator, "error")
        self.log_message(f"后端服务启动失败: {error_msg}", "后端", "error")
        self.update_status("后端服务启动失败")

        # 关闭日志文件
        if self.backend_log_file:
            self.backend_log_file.close()
            self.backend_log_file = None

        # 恢复按钮状态
        self.start_backend_btn.config(state=tk.NORMAL)
        self.stop_backend_btn.config(state=tk.DISABLED)
        self.backend_link_btn.state(['disabled'])

        if not self.frontend_running:
            self.start_all_btn.config(state=tk.NORMAL)
            self.stop_all_btn.config(state=tk.DISABLED)

    def _backend_stopped(self):
        """后端服务停止"""
        self.backend_running = False
        self.backend_detail_label.config(text="状态: 已停止")
        self.draw_status_indicator(self.backend_status_indicator, "stopped")
        self.log_message("后端服务已停止", "后端")
        self.update_status("后端服务已停止")

        # 关闭日志文件
        if self.backend_log_file:
            try:
                self.backend_log_file.write(f"\n后端服务停止 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                self.backend_log_file.close()
            except:
                pass
            self.backend_log_file = None

        # 恢复按钮状态
        self.start_backend_btn.config(state=tk.NORMAL)
        self.stop_backend_btn.config(state=tk.DISABLED)
        self.backend_link_btn.state(['disabled'])

        if not self.frontend_running:
            self.start_all_btn.config(state=tk.NORMAL)
            self.stop_all_btn.config(state=tk.DISABLED)

    def stop_backend(self):
        """停止后端服务"""
        if not self.backend_running or not self.backend_process:
            return

        self.log_message("正在停止后端服务...", "后端")
        self.update_status("正在停止后端服务...")

        try:
            # 发送Ctrl+C信号
            import signal
            try:
                self.backend_process.send_signal(signal.CTRL_C_EVENT)
            except:
                # 如果发送信号失败，尝试终止
                self.backend_process.terminate()

            # 等待一段时间
            time.sleep(2)

            # 如果进程还在运行，强制终止
            if self.backend_process.poll() is None:
                self.backend_process.kill()
                self.log_message("后端服务已被强制终止", "后端", "warning")
            else:
                self.log_message("后端服务已正常停止", "后端", "success")

        except Exception as e:
            self.log_message(f"停止后端服务时出错: {str(e)}", "后端", "error")

    def start_frontend(self):
        """启动前端服务"""
        if self.frontend_running:
            self.log_message("前端服务已经在运行中", "前端", "warning")
            return

        self.log_message("正在启动前端服务...", "前端")
        self.update_status("正在启动前端服务...")

        # 创建日志文件
        self.frontend_log_file, log_filename = self.create_log_file("frontend")
        if self.frontend_log_file:
            self.update_log_info(f"前端日志: {log_filename}")

        # 更新状态
        self.frontend_running = True
        self.frontend_detail_label.config(text="状态: 启动中...")
        self.draw_status_indicator(self.frontend_status_indicator, "starting")

        # 启用/禁用按钮
        self.start_frontend_btn.config(state=tk.DISABLED)
        self.stop_frontend_btn.config(state=tk.NORMAL)
        self.start_all_btn.config(state=tk.DISABLED)
        self.frontend_link_btn.state(['!disabled'])

        # 在新的线程中启动服务
        thread = threading.Thread(target=self._run_frontend, daemon=True)
        thread.start()

    def _run_frontend(self):
        """运行前端服务的实际代码"""
        try:
            frontend_bat_path = self.config["frontend_path"]

            # 检查文件是否存在
            if not os.path.exists(frontend_bat_path):
                self.log_message(f"错误: 找不到前端启动文件 {frontend_bat_path}", "前端", "error")
                self.root.after(0, self._frontend_start_failed, "找不到启动文件")
                return

            self.log_message(f"执行启动脚本: {frontend_bat_path}", "前端")

            # 启动前端服务 - 使用系统编码
            self.frontend_process = subprocess.Popen(
                ["cmd", "/k", frontend_bat_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=False,  # 不使用文本模式，我们自己解码
                bufsize=1,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )

            # 标记为运行中
            self.root.after(0, self._frontend_started)

            # 读取输出 - 使用系统编码解码
            while True:
                line = self.frontend_process.stdout.readline()
                if not line and self.frontend_process.poll() is not None:
                    break
                if line:
                    try:
                        # 尝试用系统编码解码
                        decoded_line = line.decode(self.system_encoding, errors='replace').rstrip('\n\r')
                        self.log_message(decoded_line, "前端")
                    except Exception as decode_error:
                        # 如果解码失败，尝试UTF-8
                        try:
                            decoded_line = line.decode('utf-8', errors='replace').rstrip('\n\r')
                            self.log_message(decoded_line, "前端")
                        except:
                            self.log_message(f"[二进制数据，无法解码]", "前端")

            # 进程结束
            self.root.after(0, self._frontend_stopped)

        except Exception as e:
            self.log_message(f"启动前端服务时出错: {str(e)}", "前端", "error")
            self.root.after(0, self._frontend_start_failed, str(e))

    def _frontend_started(self):
        """前端服务启动成功"""
        self.draw_status_indicator(self.frontend_status_indicator, "running")
        self.frontend_detail_label.config(text="状态: 运行中")
        self.log_message("前端服务启动成功", "前端", "success")
        self.update_status(f"前端服务运行中 - http://localhost:{self.config['frontend_port']}")
        self.start_all_btn.config(state=tk.DISABLED)
        self.stop_all_btn.config(state=tk.NORMAL)

    def _frontend_start_failed(self, error_msg):
        """前端服务启动失败"""
        self.frontend_running = False
        self.frontend_detail_label.config(text="状态: 启动失败")
        self.draw_status_indicator(self.frontend_status_indicator, "error")
        self.log_message(f"前端服务启动失败: {error_msg}", "前端", "error")
        self.update_status("前端服务启动失败")

        # 关闭日志文件
        if self.frontend_log_file:
            self.frontend_log_file.close()
            self.frontend_log_file = None

        # 恢复按钮状态
        self.start_frontend_btn.config(state=tk.NORMAL)
        self.stop_frontend_btn.config(state=tk.DISABLED)
        self.frontend_link_btn.state(['disabled'])

        if not self.backend_running:
            self.start_all_btn.config(state=tk.NORMAL)
            self.stop_all_btn.config(state=tk.DISABLED)

    def _frontend_stopped(self):
        """前端服务停止"""
        self.frontend_running = False
        self.frontend_detail_label.config(text="状态: 已停止")
        self.draw_status_indicator(self.frontend_status_indicator, "stopped")
        self.log_message("前端服务已停止", "前端")
        self.update_status("前端服务已停止")

        # 关闭日志文件
        if self.frontend_log_file:
            try:
                self.frontend_log_file.write(f"\n前端服务停止 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                self.frontend_log_file.close()
            except:
                pass
            self.frontend_log_file = None

        # 恢复按钮状态
        self.start_frontend_btn.config(state=tk.NORMAL)
        self.stop_frontend_btn.config(state=tk.DISABLED)
        self.frontend_link_btn.state(['disabled'])

        if not self.backend_running:
            self.start_all_btn.config(state=tk.NORMAL)
            self.stop_all_btn.config(state=tk.DISABLED)

    def stop_frontend(self):
        """停止前端服务"""
        if not self.frontend_running or not self.frontend_process:
            return

        self.log_message("正在停止前端服务...", "前端")
        self.update_status("正在停止前端服务...")

        try:
            # 发送Ctrl+C信号
            import signal
            try:
                self.frontend_process.send_signal(signal.CTRL_C_EVENT)
            except:
                # 如果发送信号失败，尝试终止
                self.frontend_process.terminate()

            # 等待一段时间
            time.sleep(2)

            # 如果进程还在运行，强制终止
            if self.frontend_process.poll() is None:
                self.frontend_process.kill()
                self.log_message("前端服务已被强制终止", "前端", "warning")
            else:
                self.log_message("前端服务已正常停止", "前端", "success")

        except Exception as e:
            self.log_message(f"停止前端服务时出错: {str(e)}", "前端", "error")

    def start_all_services(self):
        """一键启动所有服务"""
        self.log_message("正在启动所有服务...", "系统")
        self.update_status("正在启动所有服务...")

        # 禁用一键启动按钮，启用一键停止按钮
        self.start_all_btn.config(state=tk.DISABLED)
        self.stop_all_btn.config(state=tk.NORMAL)

        # 先启动后端，然后前端
        self.start_backend()

        # 延迟3秒后启动前端
        self.root.after(3000, self.start_frontend)

    def stop_all_services(self):
        """一键停止所有服务"""
        self.log_message("正在停止所有服务...", "系统")
        self.update_status("正在停止所有服务...")

        # 先停止前端，然后后端
        self.stop_frontend()
        self.stop_backend()

        # 禁用一键停止按钮
        self.stop_all_btn.config(state=tk.DISABLED)

        # 延迟3秒后检查状态并更新按钮
        self.root.after(3000, self._check_and_update_all_buttons)

    def _check_and_update_all_buttons(self):
        """检查服务状态并更新一键按钮"""
        if not self.backend_running and not self.frontend_running:
            self.start_all_btn.config(state=tk.NORMAL)
            self.update_status("所有服务已停止")

    def check_services_on_startup(self):
        """启动时检查服务状态"""
        self.log_message("检查服务状态...", "系统")

        # 检查后端服务
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', self.config['backend_port']))
            if result == 0:
                self.backend_running = True
                self.backend_detail_label.config(text="状态: 运行中")
                self.draw_status_indicator(self.backend_status_indicator, "running")
                self.start_backend_btn.config(state=tk.DISABLED)
                self.stop_backend_btn.config(state=tk.NORMAL)
                self.backend_link_btn.state(['!disabled'])
                self.log_message("检测到后端服务已在运行", "系统", "warning")
        except:
            pass

        # 检查前端服务
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', self.config['frontend_port']))
            if result == 0:
                self.frontend_running = True
                self.frontend_detail_label.config(text="状态: 运行中")
                self.draw_status_indicator(self.frontend_status_indicator, "running")
                self.start_frontend_btn.config(state=tk.DISABLED)
                self.stop_frontend_btn.config(state=tk.NORMAL)
                self.frontend_link_btn.state(['!disabled'])
                self.log_message("检测到前端服务已在运行", "系统", "warning")
        except:
            pass

        # 更新一键按钮状态
        if self.backend_running or self.frontend_running:
            self.start_all_btn.config(state=tk.DISABLED)
            self.stop_all_btn.config(state=tk.NORMAL)

        self.log_message("服务状态检查完成", "系统", "success")

    def on_closing(self):
        """窗口关闭时的清理工作"""
        if self.backend_running or self.frontend_running:
            if messagebox.askyesno("确认", "有服务正在运行，确定要退出吗？"):
                # 停止所有服务
                if self.backend_running:
                    self.stop_backend()
                if self.frontend_running:
                    self.stop_frontend()

                # 延迟关闭窗口
                self.root.after(1000, self.root.destroy)
        else:
            self.root.destroy()


def main():
    """主函数"""
    root = tk.Tk()
    app = ServiceLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()