"""
核心视频编辑模块
支持剪辑、调整、格式转换等基础操作
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple
import subprocess
import json

from moviepy.editor import VideoFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoEditor:
    """视频编辑器类 - 提供基础视频操作"""
    
    def __init__(self, input_path: str):
        """
        初始化视频编辑器
        
        Args:
            input_path: 输入视频文件路径
        """
        self.input_path = input_path
        self.clip = None
        self.output_path = None
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"视频文件不存在: {input_path}")
        
        try:
            self.clip = VideoFileClip(input_path)
            logger.info(f"加载视频成功: {input_path}")
            logger.info(f"时长: {self.clip.duration}s, 分辨率: {self.clip.size}")
        except Exception as e:
            logger.error(f"加载视频失败: {e}")
            raise
    
    def trim(self, start: float, end: float) -> 'VideoEditor':
        """
        剪辑视频片段
        
        Args:
            start: 开始时间（秒）
            end: 结束时间（秒）
        
        Returns:
            self: 支持链式调用
        """
        if start < 0 or end > self.clip.duration or start >= end:
            logger.error(f"无效的时间范围: {start}-{end}")
            raise ValueError("时间范围无效")
        
        self.clip = self.clip.subclipped(start, end)
        logger.info(f"剪辑片段: {start}s - {end}s")
        return self
    
    def resize(self, width: int, height: int, maintain_ratio: bool = True) -> 'VideoEditor':
        """
        调整视频分辨率
        
        Args:
            width: 目标宽度
            height: 目标高度
            maintain_ratio: 是否保持宽高比
        
        Returns:
            self: 支持链式调用
        """
        if maintain_ratio:
            # 计算缩放比例以保持宽高比
            ratio = min(width / self.clip.w, height / self.clip.h)
            new_width = int(self.clip.w * ratio)
            new_height = int(self.clip.h * ratio)
            self.clip = self.clip.resize((new_width, new_height))
        else:
            self.clip = self.clip.resize((width, height))
        
        logger.info(f"调整分辨率: {width}x{height}")
        return self
    
    def set_fps(self, fps: int) -> 'VideoEditor':
        """
        设置帧率
        
        Args:
            fps: 目标帧率
        
        Returns:
            self: 支持链式调用
        """
        self.clip = self.clip.speedx(self.clip.fps / fps) if fps != self.clip.fps else self.clip
        logger.info(f"设置帧率: {fps} fps")
        return self
    
    def rotate(self, angle: float) -> 'VideoEditor':
        """
        旋转视频
        
        Args:
            angle: 旋转角度（度）
        
        Returns:
            self: 支持链式调用
        """
        self.clip = self.clip.rotate(angle)
        logger.info(f"旋转视频: {angle}°")
        return self
    
    def add_watermark(self, watermark_path: str, position: str = 'bottom_right', 
                     opacity: float = 0.7) -> 'VideoEditor':
        """
        添加水印
        
        Args:
            watermark_path: 水印图片路径
            position: 位置 (top_left, top_right, bottom_left, bottom_right, center)
            opacity: 透明度 (0-1)
        
        Returns:
            self: 支持链式调用
        """
        if not os.path.exists(watermark_path):
            logger.error(f"水印文件不存在: {watermark_path}")
            raise FileNotFoundError(f"水印文件不存在: {watermark_path}")
        
        try:
            from moviepy.editor import ImageClip, CompositeVideoClip
            
            watermark = ImageClip(watermark_path).set_duration(self.clip.duration)
            watermark = watermark.set_opacity(opacity)
            
            # 根据位置调整水印坐标
            positions = {
                'top_left': (10, 10),
                'top_right': (self.clip.w - watermark.w - 10, 10),
                'bottom_left': (10, self.clip.h - watermark.h - 10),
                'bottom_right': (self.clip.w - watermark.w - 10, self.clip.h - watermark.h - 10),
                'center': ((self.clip.w - watermark.w) // 2, (self.clip.h - watermark.h) // 2)
            }
            
            watermark = watermark.set_position(positions.get(position, positions['bottom_right']))
            self.clip = CompositeVideoClip([self.clip, watermark])
            
            logger.info(f"添加水印: {watermark_path} ({position})")
        except Exception as e:
            logger.error(f"添加水印失败: {e}")
            raise
        
        return self
    
    def change_speed(self, speed: float) -> 'VideoEditor':
        """
        改变播放速度
        
        Args:
            speed: 速度倍数 (0.5 = 减速50%, 2 = 加速100%)
        
        Returns:
            self: 支持链式调用
        """
        if speed <= 0:
            logger.error("速度必须大于0")
            raise ValueError("速度必须大于0")
        
        self.clip = self.clip.speedx(speed)
        logger.info(f"改变速度: {speed}x")
        return self
    
    def export(self, output_path: str, codec: str = 'libx264', audio_codec: str = 'aac',
               bitrate: str = "5000k", verbose: bool = False) -> str:
        """
        导出视频
        
        Args:
            output_path: 输出文件路径
            codec: 视频编码器
            audio_codec: 音频编码器
            bitrate: 比特率
            verbose: 是否显示详细日志
        
        Returns:
            输出文件路径
        """
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        try:
            logger.info(f"开始导出: {output_path}")
            self.clip.write_videofile(
                output_path,
                codec=codec,
                audio_codec=audio_codec,
                bitrate=bitrate,
                verbose=verbose,
                logger=None if not verbose else logger
            )
            logger.info(f"导出成功: {output_path}")
            self.output_path = output_path
            return output_path
        except Exception as e:
            logger.error(f"导出失败: {e}")
            raise
    
    def get_info(self) -> dict:
        """
        获取视频信息
        
        Returns:
            视频信息字典
        """
        return {
            'duration': self.clip.duration,
            'fps': self.clip.fps,
            'width': self.clip.w,
            'height': self.clip.h,
            'size': self.clip.size,
            'audio': {
                'fps': self.clip.audio.fps if self.clip.audio else None,
                'nchannels': self.clip.audio.nchannels if self.clip.audio else None
            }
        }
    
    def close(self):
        """关闭视频文件"""
        if self.clip:
            self.clip.close()
            logger.info("视频文件已关闭")


class VideoProcessor:
    """视频处理器 - 处理复杂的视频处理任务"""
    
    @staticmethod
    def concatenate(video_paths: list, output_path: str) -> str:
        """
        合并多个视频
        
        Args:
            video_paths: 视频文件路径列表
            output_path: 输出文件路径
        
        Returns:
            输出文件路径
        """
        try:
            clips = [VideoFileClip(path) for path in video_paths]
            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile(output_path, verbose=False, logger=None)
            
            for clip in clips:
                clip.close()
            
            logger.info(f"合并成功: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"合并失败: {e}")
            raise
    
    @staticmethod
    def extract_frames(video_path: str, output_dir: str, interval: int = 1) -> list:
        """
        提取视频帧
        
        Args:
            video_path: 视频路径
            output_dir: 输出目录
            interval: 提取间隔（秒）
        
        Returns:
            提取的帧列表
        """
        try:
            clip = VideoFileClip(video_path)
            
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            frames = []
            for t in np.arange(0, clip.duration, interval):
                frame = clip.get_frame(t)
                frame_path = os.path.join(output_dir, f"frame_{int(t*1000):06d}.png")
                Image.fromarray(frame).save(frame_path)
                frames.append(frame_path)
            
            clip.close()
            logger.info(f"提取帧成功: {len(frames)} 帧")
            return frames
        except Exception as e:
            logger.error(f"提取帧失败: {e}")
            raise


if __name__ == '__main__':
    # 使用示例
    try:
        editor = VideoEditor('sample_video.mp4')
        editor.trim(10, 60).resize(1920, 1080).export('output.mp4')
        print(editor.get_info())
    except Exception as e:
        print(f"错误: {e}")
