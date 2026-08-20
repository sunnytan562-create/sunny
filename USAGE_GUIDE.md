# 自动化视频剪辑系统 - 使用指南

## 📋 目录

1. [功能概述](#功能概述)
2. [安装指南](#安装指南)
3. [快速开始](#快速开始)
4. [详细用法](#详细用法)
5. [配置参考](#配置参考)
6. [常见问题](#常见问题)

## 功能概述

本系统提供以下核心功能：

### 视频剪辑 (VideoEditor)
- ✂️ 剪辑视频片段 (trim)
- 📐 调整分辨率 (resize)
- 🔄 旋转视频 (rotate)
- ⚡ 改变播放速度 (speed)
- 🖼️ 添加水印 (watermark)
- 🎬 设置帧率 (fps)

### 批量处理 (BatchProcessor)
- 📦 一次处理多个视频
- ⚙️ 使用 JSON 配置文件
- 🔄 支持并行处理
- 📊 生成处理报告

### 视频分析 (VideoAnalyzer)
- 📹 获取视频详细信息
- 📊 分析多个视频
- 📁 批量分析目录
- 📈 生成统计报告

## 安装指南

### 步骤 1: 克隆仓库
```bash
git clone https://github.com/sunnytan562-create/sunny.git
cd sunny
```

### 步骤 2: 安装依赖
```bash
pip install -r requirements.txt
```

### 步骤 3: 安装 FFmpeg

**Windows (使用 Chocolatey):**
```bash
choco install ffmpeg
```

**Windows (手动下载):**
访问 https://ffmpeg.org/download.html

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install ffmpeg
```

### 步骤 4: 验证安装
```bash
python quickstart.py
```

## 快速开始

### 1️⃣ 查看单个视频信息
```bash
python video_info.py info video.mp4
```

输出示例：
```
文件                : video.mp4
文件大小            : 250.50 MB
时长                : 01:05:30 (3930.00s)
帧率                : 30 fps
分辨率              : 1920x1080
宽高比              : 1920:1080
总帧数              : 117900
有音频              : 是
音频采样率          : 48000 Hz
音频通道数          : 2
```

### 2️⃣ 剪辑单个视频
```bash
python video_editor.py trim --input video.mp4 --start 10 --end 60 --output output.mp4
```

### 3️⃣ 批量处理多个视频
```bash
python batch_processor.py batch --config examples/tasks.json --workers 2
```

### 4️⃣ 分析视频目录
```bash
python video_info.py batch-analyze ./videos/
```

## 详细用法

### 视频信息工具 (video_info.py)

#### 获取单个视频信息 (表格格式)
```bash
python video_info.py info input.mp4
```

#### 获取单个视频信息 (JSON 格式)
```bash
python video_info.py info input.mp4 --format json
```

#### 保存视频信息到文件
```bash
python video_info.py info input.mp4 --output video_info.json
```

#### 批量分析目录
```bash
python video_info.py batch-analyze ./videos/ --extensions mp4,avi,mov
```

#### 比较多个视频
```bash
python video_info.py compare video1.mp4 video2.mp4 video3.mp4
```

### 批量处理工具 (batch_processor.py)

#### 执行批量任务
```bash
python batch_processor.py batch --config tasks.json --workers 2 --output-report results.json
```

参数说明：
- `--config`: 配置文件路径 (必需)
- `--workers`: 并行处理数 (默认: 2)
- `--output-report`: 结果报告文件路径 (默认: results.json)

#### 生成配置模板
```bash
python batch_processor.py generate-template --template my_tasks.json
```

### 视频编辑器 (video_editor.py)

#### Python API 使用方法
```python
from video_editor import VideoEditor

# 创建编辑器
editor = VideoEditor('input.mp4')

# 链式调用编辑操作
editor.trim(10, 60)              # 剪辑 10-60 秒
editor.resize(1920, 1080)        # 调整分辨率到 1920x1080
editor.add_watermark(
    'watermark.png',
    position='bottom_right',
    opacity=0.7
)
editor.change_speed(1.5)         # 加速 1.5 倍
editor.export('output.mp4')      # 导出视频

# 获取视频信息
info = editor.get_info()
print(info)

# 关闭编辑器
editor.close()
```

## 配置参考

### 任务配置文件格式 (tasks.json)

```json
{
  "tasks": [
    {
      "name": "任务名称",
      "input": "输入视频路径",
      "output": "输出视频路径",
      "codec": "libx264",
      "audio_codec": "aac",
      "bitrate": "5000k",
      "actions": [
        {
          "type": "trim",
          "start": 0,
          "end": 60
        },
        {
          "type": "resize",
          "width": 1920,
          "height": 1080,
          "maintain_ratio": true
        },
        {
          "type": "watermark",
          "watermark_path": "watermark.png",
          "position": "bottom_right",
          "opacity": 0.7
        }
      ]
    }
  ]
}
```

### 支持的操作类型

| 操作类型 | 参数 | 说明 |
|---------|------|------|
| trim | start, end | 剪辑视频片段 (秒) |
| resize | width, height, maintain_ratio | 调整分辨率 |
| rotate | angle | 旋转视频 (度数) |
| speed | speed | 改变播放速度 (倍数) |
| watermark | watermark_path, position, opacity | 添加水印 |
| fps | fps | 设置帧率 |

### 水印位置选项

- `top_left` - 左上角
- `top_right` - 右上角
- `bottom_left` - 左下角
- `bottom_right` - 右下角 (默认)
- `center` - 中心

### 编码参数

常见比特率：
- `2000k` - 移动端（720p）
- `5000k` - 标准（1080p）
- `8000k` - 高清（1080p+）
- `15000k` - 超清（4K）

编码器选项：
- `libx264` - H.264（推荐，兼容性好）
- `libx265` - H.265（更小文件体积）
- `mpeg4` - MPEG-4

## 常见问题

### Q1: FFmpeg 安装后仍未找到？
**A:** 
1. 重启命令行/IDE
2. 确保 FFmpeg 已添加到系统 PATH
3. 运行 `ffmpeg -version` 验证

### Q2: 处理大视频时出现内存不足错误？
**A:**
1. 减少 `--workers` 参数（使用 1 个并行）
2. 分割视频成更小片段处理
3. 增加系统内存或使用 RAM 盘

### Q3: 如何加快处理速度？
**A:**
1. 增加 `--workers` 参数
2. 使用更低的输出分辨率
3. 使用 H.265 编码器（更慢但文件更小）
4. 启用硬件加速（GPU）

### Q4: 为什么输出视频质量下降？
**A:**
1. 检查比特率设置（bitrate）
2. 使用 `libx264` 编码器
3. 确保输入视频质量足够
4. 避免过度压缩

### Q5: 支持哪些视频格式？
**A:** 支持 FFmpeg 支持的所有格式：
- 视频: MP4, AVI, MOV, MKV, FLV, WMV 等
- 音频: MP3, AAC, WAV, FLAC 等

### Q6: 如何批量处理同一目录中的所有视频？
**A:** 创建配置文件遍历目录：
```python
import os
import json
from pathlib import Path

tasks = []
for video in Path('./videos').glob('*.mp4'):
    tasks.append({
        "name": video.stem,
        "input": str(video),
        "output": f"output/{video.stem}_processed.mp4",
        "actions": [
            {"type": "resize", "width": 1920, "height": 1080}
        ]
    })

with open('batch_tasks.json', 'w') as f:
    json.dump({"tasks": tasks}, f, indent=2)
```

### Q7: 如何恢复已处理的视频？
**A:** 处理不可逆。建议：
1. 备份原始视频
2. 在处理前预览参数
3. 先用小片段测试

## 📚 更多资源

- [FFmpeg 官网](https://ffmpeg.org/)
- [MoviePy 文档](https://zulko.github.io/moviepy/)
- [GitHub 仓库](https://github.com/sunnytan562-create/sunny)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
