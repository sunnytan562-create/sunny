<!-- markdownlint-disable -->
# 🎬 本地视频自动剪辑系统

![Python](https://img.shields.io/badge/Python-3.7+-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-green)
![MoviePy](https://img.shields.io/badge/MoviePy-1.0+-orange)
![License](https://img.shields.io/badge/License-MIT-red)

一个功能强大的本地视频自动剪辑系统，支持智能检测、自动剪辑、手动编辑和快速导出。无需上传到云端，完全离线处理，保护您的隐私。

---

## ✨ 主要功能

### 🎯 核心特性
- ✅ **本地视频管理** - 扫描、上传、组织本地视频库
- ✅ **智能分析** - 自动检测静音、黑屏、场景切换
- ✅ **自动剪辑** - 一键移除无用片段，节省视频时长
- ✅ **手动编辑** - 裁剪、缩放、调整视频参数
- ✅ **快速导出** - 支持多种编码器和比特率
- ✅ **Web界面** - 美观易用的网页控制面板
- ✅ **Python API** - 支持程序化调用

---

## 📋 系统要求

### 必需条件
- **Python** 3.7+
- **FFmpeg** (用于视频处理)
- **8GB+** 内存（处理大文件时推荐）

### 支持的视频格式
- MP4, AVI, MOV, MKV, FLV, WMV, WebM

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
# 克隆仓库
git clone https://github.com/sunnytan562-create/sunny.git
cd sunny
git checkout feature/local-video-processor

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2️⃣ 安装 FFmpeg

**Windows:**
```bash
# 使用 Chocolatey
choco install ffmpeg

# 或手动下载: https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

### 3️⃣ 启动服务

```bash
python run.py
```

输出示例：
```
╔═══════════════════════════════════════════════════════════╗
║     🎬 本地视频自动剪辑系统 - Local Video Processor      ║
╚═══════════════════════════════════════════════════════════╝

✓ 检查依赖...
  ✅ moviepy
  ✅ flask
  ✅ numpy

✓ 创建目录...
  ✅ ./video_library/raw_videos
  ...

🌐 Web 界面: http://localhost:5000
```

### 4️⃣ 打开浏览器

访问 **http://localhost:5000**

---

## 💻 Web UI 使用指南

### 📁 视频管理标签页

#### 上传视频
1. 点击上传区域或选择文件
2. 支持拖拽上传多个文件
3. 系统自动分析视频信息

#### 扫描目录
1. 输入本地目录路径，如 `/home/user/videos`
2. 点击"扫描"按钮
3. 系统自动发现目录中的所有视频

#### 视频列表
显示所有已导入的视频：
- 📹 视频名称
- ⏱️ 时长
- 💾 文件大小
- 📐 分辨率

---

### ✂️ 自动剪辑标签页

#### 分析视频
1. 在"分析"标签页选择视频
2. 点击"开始分析"
3. 系统检测：
   - 静音区间数量
   - 黑屏区间数量
   - 场景切换点数量

#### 自动剪辑
1. 在"自动剪辑"标签页选择视频
2. 勾选要移除的内容：
   - ☑️ 移除静音区间
   - ☑️ 移除黑屏区间
3. 可选：设置目标时长（秒）
4. 点击"开始剪辑"
5. 查看剪辑结果：
   - 原始时长
   - 保留时长
   - 节省比例

#### 导出视频
1. 选择输出文件名
2. 选择编码器：
   - **H.264** (推荐，兼容性好)
   - **H.265** (高压缩比)
3. 选择比特率：
   - 2000k (720p)
   - 5000k (1080p，推荐)
   - 8000k (高清)
4. 点击"导出视频"
5. 等待处理完成，文件保存到 `./output/` 文件夹

---

### ✏️ 手动编辑标签页

#### 裁剪视频
1. 选择视频
2. 设置开始时间（秒）
3. 设置结束时间（秒）
4. 点击"开始编辑"

#### 缩放视频
1. 选择视频
2. 输入目标宽度和高度
3. 点击"开始编辑"

#### 组合操作
同时进行裁剪和缩放：
- 设置开始/结束时间
- 设置宽度/高度
- 一次完成所有编辑

---

## 🐍 Python API 使用

### 基础示例

```python
from local_video_manager import LocalVideoManager
from auto_cut_engine import AutoCutEngine

# 初始化管理器
manager = LocalVideoManager("./video_library")

# 扫描目录
videos = manager.scan_directory("./my_videos", recursive=True)
print(f"发现 {len(videos)} 个视频")

# 列出所有视频
all_videos = manager.list_videos()
for video in all_videos:
    print(f"{video.name}: {video.duration}秒")
```

### 自动剪辑示例

```python
from auto_cut_engine import AutoCutEngine

engine = AutoCutEngine()

# 智能自动剪辑
cuts = engine.smart_cut(
    "video.mp4",
    target_duration=600,      # 10分钟
    remove_silence=True,      # 移除静音
    remove_black=True         # 移除黑屏
)

# 查看剪辑点
segments = engine.get_cut_segments()
for i, seg in enumerate(segments):
    print(f"片段 {i+1}: {seg['start']:.2f}s - {seg['end']:.2f}s ({seg['duration']:.2f}s)")

# 导出
engine.apply_cuts("video.mp4", "output.mp4")
```

### 视频分析示例

```python
from auto_cut_engine import AutoCutEngine

engine = AutoCutEngine()

# 检测静音
silence_regions = engine.detect_silence("video.mp4", threshold=0.01)
print(f"静音区间: {silence_regions}")

# 检测黑屏
black_regions = engine.detect_black_frames("video.mp4", threshold=30)
print(f"黑屏区间: {black_regions}")

# 检测场景切换
scenes = engine.detect_scene_changes("video.mp4")
print(f"场景切换: {scenes}")
```

### 视频搜索示例

```python
manager = LocalVideoManager("./video_library")

# 搜索视频
results = manager.search_videos("演讲")

# 删除视频（移到回收站）
video_hash = manager.videos[list(manager.videos.keys())[0]]
manager.delete_video(video_hash, move_to_trash=True)

# 获取统计信息
stats = manager.get_statistics()
print(f"总视频数: {stats['total_videos']}")
print(f"总大小: {stats['total_size_gb']:.2f}GB")
print(f"总时长: {stats['total_duration_hours']:.2f}小时")
```

---

## 📁 项目结构

```
sunny/
├── run.py                          # 启动脚本
├── app.py                          # Flask Web 后端
├── local_video_manager.py          # 视频管理系统
├── auto_cut_engine.py              # 自动剪辑引擎
├── video_editor.py                 # 视频编辑工具
├── requirements.txt                # Python 依赖
├── templates/
│   └── index.html                  # Web UI 前端
├── video_library/                  # 视频库目录
│   ├── raw_videos/                 # 原始视频
│   ├── processed_videos/           # 处理后的视频
│   ├── favorites/                  # 收藏夹
│   ├── trash/                      # 回收站
│   └── metadata.json               # 元数据
├── uploads/                        # 上传临时文件
└── output/                         # 导出文件
```

---

## 🔧 API 端点文档

### 获取视频列表
```http
GET /api/videos?category=raw_videos

Response:
{
  "success": true,
  "data": [
    {
      "hash": "abc123...",
      "name": "video.mp4",
      "size_mb": 512.5,
      "duration": 3600,
      "resolution": "1920x1080",
      "fps": 30,
      "audio": true,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### 上传视频
```http
POST /api/upload
Content-Type: multipart/form-data

file: <video_file>

Response:
{
  "success": true,
  "message": "上传成功",
  "data": {
    "name": "video.mp4",
    "size_mb": 512.5,
    "duration": 3600
  }
}
```

### 扫描目录
```http
POST /api/scan
Content-Type: application/json

{
  "directory": "/home/user/videos"
}

Response:
{
  "success": true,
  "message": "扫描完成，添加了 5 个视频",
  "count": 5
}
```

### 分析视频
```http
GET /api/analyze/<video_hash>

Response:
{
  "success": true,
  "data": {
    "video_name": "video.mp4",
    "duration": 3600,
    "silence_regions": 5,
    "black_regions": 2,
    "scene_changes": 15,
    "silence_details": [...],
    "black_details": [...]
  }
}
```

### 自动剪辑
```http
POST /api/auto-cut
Content-Type: application/json

{
  "video_hash": "abc123...",
  "target_duration": 600,
  "remove_silence": true,
  "remove_black": true
}

Response:
{
  "success": true,
  "data": {
    "original_duration": 3600,
    "kept_duration": 1200,
    "reduction": "66.7%",
    "segments": 8,
    "segments_detail": [...]
  }
}
```

### 导出视频
```http
POST /api/export
Content-Type: application/json

{
  "video_hash": "abc123...",
  "output_name": "edited_video",
  "codec": "libx264",
  "bitrate": "5000k"
}

Response:
{
  "success": true,
  "message": "导出成功",
  "data": {
    "output_path": "./output/edited_video.mp4",
    "file_size_mb": 250.5
  }
}
```

---

## ⚙️ 配置文件

### requirements.txt

```txt
Flask==2.3.0
moviepy==1.0.3
numpy==1.24.0
opencv-python==4.7.0
Werkzeug==2.3.0
```

### 环境变量

```bash
# 设置视频库路径
export VIDEO_LIBRARY_PATH=./video_library

# 设置输出路径
export OUTPUT_PATH=./output

# 设置日志级别
export LOG_LEVEL=INFO
```

---

## 🐛 故障排除

### 问题 1: FFmpeg 未找到
**错误信息**: `OSError: ffmpeg not found`

**解决方案**:
```bash
# 确保已安装 FFmpeg
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg

# 验证安装
ffmpeg -version
```

### 问题 2: 内存不足
**错误信息**: `MemoryError: cannot allocate ...`

**解决方案**:
- 处理小于 2GB 的视频文件
- 关闭其他应用程序释放内存
- 增加虚拟内存

### 问题 3: 视频无法上传
**错误信息**: `File not allowed`

**解决方案**:
- 检查文件格式是否支持（MP4, AVI, MOV, MKV 等）
- 确保文件大小小于 2GB
- 检查磁盘空间是否充足

### 问题 4: 导出很慢
**错误信息**: 导出花费过长时间

**解决方案**:
- 尝试降低比特率（2000k 而不是 8000k）
- 使用 H.265 编码器（压缩比更高但更慢）
- 缩小分辨率

---

## 📊 性能优化

### 视频处理时间参考

| 视频大小 | 分辨率 | 自动剪辑 | 导出 (5000k) |
|---------|--------|---------|------------|
| 100MB   | 720p   | 30秒    | 1分钟     |
| 500MB   | 1080p  | 2分钟   | 5分钟     |
| 1GB     | 1080p  | 4分钟   | 10分钟    |
| 2GB     | 4K     | 8分钟   | 20分钟    |

### 优化建议

1. **减少采样率** - 降低检测精度以加快处理
2. **使用 H.265** - 更好的压缩比，但处理时间更长
3. **限制比特率** - 降低输出质量可加快导出
4. **预处理视频** - 先缩小分辨率再处理

---

## 🔐 隐私与安全

- ✅ 完全离线处理，无需上传到云端
- ✅ 所有数据存储在本地磁盘
- ✅ 支持删除到回收站，可恢复
- ✅ 元数据保存为本地 JSON 文件

---

## 📝 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

- GitHub: [@sunnytan562-create](https://github.com/sunnytan562-create)
- Email: sunnytan562@gmail.com

---

**祝您使用愉快！🎉**
