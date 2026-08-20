#!/usr/bin/env python3
"""
快速开始脚本 - 一键启动视频批量处理
"""

import os
import sys
import json
from pathlib import Path

def main():
    print("=" * 70)
    print("🎬 自动化视频剪辑系统 - 快速启动")
    print("=" * 70)
    print()
    
    # 检查环境
    print("📋 环境检查...")
    
    # 检查 Python 版本
    if sys.version_info < (3, 7):
        print("❌ 错误: Python 版本需要 3.7 或更高")
        sys.exit(1)
    print("✅ Python 版本: OK")
    
    # 检查依赖
    try:
        import moviepy
        print("✅ MoviePy: OK")
    except ImportError:
        print("❌ MoviePy 未安装，请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    try:
        import click
        print("✅ Click: OK")
    except ImportError:
        print("❌ Click 未安装，请运行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 检查 FFmpeg
    os.system("ffmpeg -version > /dev/null 2>&1")
    if os.system("ffmpeg -version > /dev/null 2>&1") == 0:
        print("✅ FFmpeg: OK")
    else:
        print("❌ FFmpeg 未安装或不在 PATH 中")
        print("   Windows: choco install ffmpeg")
        print("   macOS: brew install ffmpeg")
        print("   Linux: sudo apt-get install ffmpeg")
        sys.exit(1)
    
    print()
    print("=" * 70)
    print("🚀 快速启动选项")
    print("=" * 70)
    print()
    print("1️⃣  查看视频信息")
    print("   python video_info.py info video.mp4")
    print()
    print("2️⃣  执行批量处理")
    print("   python batch_processor.py batch --config examples/tasks.json")
    print()
    print("3️⃣  生成配置模板")
    print("   python batch_processor.py generate-template --template my_tasks.json")
    print()
    print("4️⃣  批量分析视频")
    print("   python video_info.py batch-analyze ./videos/")
    print()
    print("=" * 70)
    print("📖 详细文档: 查看 README.md")
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
