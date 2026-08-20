"""
配置管理模块
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()

# 输出目录
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 日志目录
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 示例目录
EXAMPLES_DIR = PROJECT_ROOT / "examples"
EXAMPLES_DIR.mkdir(exist_ok=True)

# 日志配置
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = LOG_DIR / "video_processing.log"

# FFmpeg 配置
FFMPEG_CODEC_VIDEO = "libx264"
FFMPEG_CODEC_AUDIO = "aac"
FFMPEG_PRESET = "medium"  # ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow

# 视频处理默认参数
DEFAULT_BITRATE = "5000k"
DEFAULT_FPS = 30
DEFAULT_AUDIO_CHANNELS = 2
DEFAULT_SAMPLE_RATE = 44100

# 批量处理配置
MAX_WORKERS = 2
TASK_TIMEOUT = 3600  # 秒

# 支持的视频格式
SUPPORTED_VIDEO_FORMATS = (
    'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'm4v', 'mpg', 'mpeg'
)

# 支持的音频格式
SUPPORTED_AUDIO_FORMATS = (
    'mp3', 'aac', 'wav', 'flac', 'm4a', 'wma', 'ogg'
)

# 支持的图像格式
SUPPORTED_IMAGE_FORMATS = (
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'
)


def get_output_path(task_name: str, extension: str = 'mp4') -> str:
    """获取输出文件路径"""
    filename = f"{task_name}.{extension}"
    return str(OUTPUT_DIR / filename)


def get_log_file_path() -> str:
    """获取日志文件路径"""
    return str(LOG_FILE)


def is_supported_video_format(filename: str) -> bool:
    """检查是否为支持的视频格式"""
    ext = Path(filename).suffix.lower().lstrip('.')
    return ext in SUPPORTED_VIDEO_FORMATS


def is_supported_audio_format(filename: str) -> bool:
    """检查是否为支持的音频格式"""
    ext = Path(filename).suffix.lower().lstrip('.')
    return ext in SUPPORTED_AUDIO_FORMATS


def is_supported_image_format(filename: str) -> bool:
    """检查是否为支持的图像格式"""
    ext = Path(filename).suffix.lower().lstrip('.')
    return ext in SUPPORTED_IMAGE_FORMATS
