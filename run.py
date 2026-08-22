#!/usr/bin/env python3
"""
本地视频自动剪辑系统 - 启动脚本
一条命令启动完整的视频剪辑系统
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     🎬 本地视频自动剪辑系统 - Local Video Processor      ║
    ║                                                           ║
    ║        智能检测 • 自动剪辑 • 快速导出                    ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

def check_dependencies():
    """检��依赖"""
    print("\n✓ 检查依赖...")
    
    required = ['moviepy', 'flask', 'numpy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  缺失依赖: {', '.join(missing)}")
        print("正在安装依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print("✅ 依赖安装完成\n")

def create_directories():
    """创建必要的目录"""
    print("✓ 创建目录...")
    
    directories = [
        './video_library/raw_videos',
        './video_library/processed_videos',
        './video_library/favorites',
        './video_library/trash',
        './templates',
        './uploads',
        './output'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")

def print_usage():
    """打印使用说明"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                      🚀 系统已启动！                      ║
╚═══════════════════════════════════════════════════════════╝

📱 Web 界面:
   🌐 http://localhost:5000

📁 重要目录:
   📂 ./video_library/      - 视频库文件夹
   📂 ./output/             - 导出文件夹
   📂 ./uploads/            - 上传文件夹

🔧 主要功能:
   ✅ 本地视频管理 - 扫描、上传、组织视频
   ✅ 智能分析 - 检测静音、黑屏、场景切换
   ✅ 自动剪辑 - 一键移除无用片段
   ✅ 手动编辑 - 裁剪、缩放、调整
   ✅ 快速导出 - 多种编码器和比特率

💡 快速开始:
   1. 打开浏览器访问 http://localhost:5000
   2. 上传或扫描本地视频
   3. 选择视频进行分析
   4. 点击"自动剪辑"或"手动编辑"
   5. 导出成品视频

⚙️  API 端点:
   GET    /api/videos              - 获取视频列表
   POST   /api/upload              - 上传视频
   POST   /api/scan                - 扫描目录
   GET    /api/analyze/<hash>      - 分析视频
   POST   /api/auto-cut            - 自动剪辑
   POST   /api/export              - 导出视频
   POST   /api/edit                - 手动编辑
   DELETE /api/delete/<hash>       - 删除视频

📋 Python 代码示例:
   
   from local_video_manager import LocalVideoManager
   from auto_cut_engine import AutoCutEngine
   
   # 初始化
   manager = LocalVideoManager("./video_library")
   engine = AutoCutEngine()
   
   # 扫描视频
   manager.scan_directory("./my_videos")
   
   # 列出视频
   videos = manager.list_videos()
   
   # 分析和剪辑
   for video in videos:
       engine.smart_cut(video.path)
       engine.apply_cuts(video.path, "output.mp4")

🛑 停止服务:
   按 Ctrl+C 停止服务

📧 问题报告:
   如遇到问题，请检查日志输出

═══════════════════════════════════════════════════════════
    """)

def main():
    """主函数"""
    print_banner()
    
    # 检查 Python 版本
    if sys.version_info < (3, 7):
        print("❌ 需要 Python 3.7 或更高版本")
        sys.exit(1)
    
    print(f"Python 版本: {sys.version.split()[0]}")
    print(f"操作系统: {platform.system()}")
    
    # 检查依赖
    check_dependencies()
    
    # 创建目录
    create_directories()
    
    # 打印使用说明
    print_usage()
    
    # 启动 Flask 应用
    print("\n" + "="*60)
    print("🚀 启动 Flask 服务...")
    print("="*60 + "\n")
    
    try:
        # 导入 Flask 应用
        from app import app
        
        # 启动服务
        app.run(debug=False, host='0.0.0.0', port=5000)
    
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
