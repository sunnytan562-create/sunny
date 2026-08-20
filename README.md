# 自动化视频剪辑系统 (Automated Video Editing System)

一个基于 Python 的自动化视频剪辑解决方案，支持批量处理、智能裁剪和多格式导出。

## 功能特性

- ✂️ **批量剪辑** - 支持同时处理多个视频文件
- 🎬 **片段剪辑** - 按时间戳自动剪辑指定片段
- 📐 **自动裁剪** - 支持分辨率调整和宽高比转换
- 🎵 **音频处理** - 音量调整、音频提取、音频合成
- 🖼️ **字幕添加** - 自动添加字幕和水印
- 💾 **多格式支持** - MP4、AVI、MOV、MKV 等
- ⚙️ **配置化管理** - 使用 JSON 配置文件定义任务
- 📊 **进度监控** - 实时显示处理进度和日志

## 系统要求

- Python 3.7+
- FFmpeg
- FFprobe

## 安装

### 1. 克隆仓库
```bash
git clone https://github.com/sunnytan562-create/sunny.git
cd sunny
```

### 2. 安装 Python 依赖
```bash
pip install -r requirements.txt
```

### 3. 安装 FFmpeg（系统依赖）

**Windows:**
```bash
choco install ffmpeg
# 或下载: https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

## 使用方法

### 快速开始

```bash
# 处理单个视频
python video_editor.py --input video.mp4 --output output.mp4 --trim 10 60

# 使用配置文件批量处理
python batch_processor.py batch --config tasks.json

# 显示视频信息
python video_info.py info video.mp4
```

### 配置文件示例 (tasks.json)

```json
{
  "tasks": [
    {
      "name": "clip_1",
      "input": "video1.mp4",
      "output": "output/clip_1.mp4",
      "actions": [
        {
          "type": "trim",
          "start": 10,
          "end": 60
        },
        {
          "type": "resize",
          "width": 1920,
          "height": 1080
        }
      ]
    }
  ]
}
```

## 项目结构

```
sunny/
├── video_editor.py          # 核心剪辑模块
├── batch_processor.py       # 批量处理器
├── video_info.py            # 视频信息查询工具
├── requirements.txt         # 依赖列表
├── examples/                # 使用示例
│   └── tasks.json          # 任务配置示例
├── output/                  # 输出目录
└── .github/
    └── workflows/
        └── video-processing.yml  # GitHub Actions 工作流
```

## API 文档

### VideoEditor 类

```python
from video_editor import VideoEditor

editor = VideoEditor('input.mp4')
editor.trim(start=10, end=60)          # 剪辑 10-60 秒
editor.resize(width=1920, height=1080) # 调整分辨率
editor.export('output.mp4')             # 导出
```

### 支持的操作

- **trim** - 剪辑片段
- **resize** - 调整分辨率
- **rotate** - 旋转视频
- **speed** - 改变播放速度
- **watermark** - 添加水印
- **fps** - 设置帧率

## 高级功能

### 水印添加
```python
editor.add_watermark('watermark.png', position='bottom_right', opacity=0.7)
```

### 速度调整
```python
editor.change_speed(1.5)  # 加速 1.5 倍
```

### 视频合并
```python
from video_editor import VideoProcessor
VideoProcessor.concatenate(['video1.mp4', 'video2.mp4'], 'output.mp4')
```

## 故障排除

- **FFmpeg 未找到**: 确保已安装 FFmpeg 并添加到 PATH
- **内存不足**: 使用流式处理大文件
- **编码错误**: 检查输入视频格式兼容性

## 性能优化

- 使用硬件加速（GPU）处理
- 并行处理多个文件（最多 2 个）
- 自适应比特率编码

## CI/CD 集成

本项目包含 GitHub Actions 工作流，支持自动化视频处理：

1. 编辑 `examples/tasks.json` 定义任务
2. 推送到 GitHub
3. Actions 自动运行并生成处理结果

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- GitHub: [@sunnytan562-create](https://github.com/sunnytan562-create)
