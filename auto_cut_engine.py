"""
智能自动剪辑引擎
支持关键帧检测、场景识别、自动剪辑
"""

import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from pathlib import Path

from video_editor import VideoEditor
from moviepy.editor import VideoFileClip

logger = logging.getLogger(__name__)


@dataclass
class CutPoint:
    """剪辑点数据类"""
    start_time: float
    end_time: float
    duration: float
    confidence: float  # 置信度 0-1
    reason: str  # 剪辑原因


class AutoCutEngine:
    """智能自动剪辑引擎"""
    
    def __init__(self):
        """初始化剪辑引擎"""
        self.cut_points: List[CutPoint] = []
        logger.info("自动剪辑引擎已初始化")
    
    def detect_silence(self, video_path: str, threshold: float = 0.01, 
                       min_duration: float = 0.5) -> List[Tuple[float, float]]:
        """
        检测静音区间
        
        Args:
            video_path: 视频路径
            threshold: 音量阈值
            min_duration: 最小静音持续时间（秒）
        
        Returns:
            静音区间列表 [(start, end), ...]
        """
        try:
            clip = VideoFileClip(video_path)
            if clip.audio is None:
                logger.warning("视频没有音频")
                clip.close()
                return []
            
            # 获取音频数组
            audio_array = clip.audio.to_soundarray(fps=clip.audio.fps)
            
            # 计算每帧的音量
            if len(audio_array.shape) > 1:
                volume = np.sqrt(np.mean(audio_array ** 2, axis=1))
            else:
                volume = np.abs(audio_array)
            
            # 规范化到 0-1
            if volume.max() > 0:
                volume = volume / volume.max()
            
            # 找静音点
            silent_frames = volume < threshold
            fps = clip.audio.fps
            
            # 合并连续的静音帧
            silence_regions = []
            start = None
            
            for i, is_silent in enumerate(silent_frames):
                if is_silent and start is None:
                    start = i / fps
                elif not is_silent and start is not None:
                    end = i / fps
                    duration = end - start
                    if duration >= min_duration:
                        silence_regions.append((start, end))
                    start = None
            
            clip.close()
            logger.info(f"检测到 {len(silence_regions)} 个静音区间")
            return silence_regions
        
        except Exception as e:
            logger.error(f"检测静音失败: {e}")
            return []
    
    def detect_black_frames(self, video_path: str, threshold: float = 30,
                            sample_rate: int = 30) -> List[Tuple[float, float]]:
        """
        检测黑屏区间
        
        Args:
            video_path: 视频路径
            threshold: 亮度阈值（0-255）
            sample_rate: 采样率（每秒检查的帧数）
        
        Returns:
            黑屏区间列表
        """
        try:
            clip = VideoFileClip(video_path)
            fps = clip.fps
            sample_interval = fps / sample_rate
            
            black_regions = []
            start = None
            
            for t in np.arange(0, clip.duration, sample_interval):
                frame = clip.get_frame(t)
                
                # 计算帧的平均亮度
                gray = np.mean(frame, axis=2)
                brightness = np.mean(gray)
                
                if brightness < threshold:
                    if start is None:
                        start = t
                else:
                    if start is not None:
                        black_regions.append((start, t))
                        start = None
            
            if start is not None:
                black_regions.append((start, clip.duration))
            
            clip.close()
            logger.info(f"检测到 {len(black_regions)} 个黑屏区间")
            return black_regions
        
        except Exception as e:
            logger.error(f"检测黑屏失败: {e}")
            return []
    
    def detect_scene_changes(self, video_path: str, threshold: float = 27.0,
                            sample_rate: int = 10) -> List[float]:
        """
        检测场景切换点
        
        Args:
            video_path: 视频路径
            threshold: 场景变化阈值
            sample_rate: 采样率
        
        Returns:
            场景切换时间点列表
        """
        try:
            clip = VideoFileClip(video_path)
            fps = clip.fps
            sample_interval = fps / sample_rate
            
            scene_changes = []
            prev_frame = None
            
            for t in np.arange(0, clip.duration, sample_interval):
                frame = clip.get_frame(t)
                
                if prev_frame is not None:
                    # 计算帧差（简化版）
                    diff = np.mean(np.abs(frame.astype(float) - prev_frame.astype(float)))
                    
                    if diff > threshold:
                        scene_changes.append(t)
                
                prev_frame = frame.copy()
            
            clip.close()
            logger.info(f"检测到 {len(scene_changes)} 个场景切换点")
            return scene_changes
        
        except Exception as e:
            logger.error(f"检测场景切换失败: {e}")
            return []
    
    def smart_cut(self, video_path: str, target_duration: Optional[float] = None,
                  remove_silence: bool = True, remove_black: bool = True,
                  min_segment_duration: float = 2.0) -> List[CutPoint]:
        """
        智能自动剪辑
        
        Args:
            video_path: 视频路径
            target_duration: 目标时长（秒）
            remove_silence: 是否移除静音
            remove_black: 是否移除黑屏
            min_segment_duration: 最小保留片段时长
        
        Returns:
            剪辑点列表
        """
        clip = VideoFileClip(video_path)
        total_duration = clip.duration
        clip.close()
        
        self.cut_points = []
        
        # 检测需要移除的区间
        remove_intervals = []
        
        if remove_silence:
            remove_intervals.extend([
                (start, end, "静音") for start, end in self.detect_silence(video_path)
            ])
        
        if remove_black:
            remove_intervals.extend([
                (start, end, "黑屏") for start, end in self.detect_black_frames(video_path)
            ])
        
        # 合并重叠区间
        remove_intervals = self._merge_intervals(remove_intervals)
        
        # 生成保留片段
        current_time = 0
        for start, end, reason in remove_intervals:
            if start > current_time and start - current_time >= min_segment_duration:
                self.cut_points.append(CutPoint(
                    start_time=current_time,
                    end_time=start,
                    duration=start - current_time,
                    confidence=1.0,
                    reason="保留片段"
                ))
            current_time = end
        
        # 添加最后的片段
        if current_time < total_duration and total_duration - current_time >= min_segment_duration:
            self.cut_points.append(CutPoint(
                start_time=current_time,
                end_time=total_duration,
                duration=total_duration - current_time,
                confidence=1.0,
                reason="保留片段"
            ))
        
        # 如果指定了目标时长，进行压缩
        if target_duration and sum(cp.duration for cp in self.cut_points) > target_duration:
            self.cut_points = self._compress_to_target(target_duration)
        
        logger.info(f"生成了 {len(self.cut_points)} 个剪辑点")
        return self.cut_points
    
    def _merge_intervals(self, intervals: List[Tuple[float, float, str]], 
                        gap: float = 0.5) -> List[Tuple[float, float, str]]:
        """合并接近的时间间隔"""
        if not intervals:
            return []
        
        # 按开始时间排序
        intervals.sort(key=lambda x: x[0])
        
        merged = [intervals[0]]
        
        for current in intervals[1:]:
            last = merged[-1]
            if current[0] - last[1] <= gap:
                # 合并
                merged[-1] = (last[0], max(last[1], current[1]), f"{last[2]},{current[2]}")
            else:
                merged.append(current)
        
        return merged
    
    def _compress_to_target(self, target_duration: float) -> List[CutPoint]:
        """压缩片段到目标时长"""
        if not self.cut_points:
            return []
        
        total_duration = sum(cp.duration for cp in self.cut_points)
        
        if total_duration <= target_duration:
            return self.cut_points
        
        compress_ratio = target_duration / total_duration
        compressed = []
        
        for cp in self.cut_points:
            new_duration = cp.duration * compress_ratio
            compressed.append(CutPoint(
                start_time=cp.start_time,
                end_time=cp.start_time + new_duration,
                duration=new_duration,
                confidence=cp.confidence * compress_ratio,
                reason=f"{cp.reason}(压缩)"
            ))
        
        return compressed
    
    def get_cut_segments(self) -> List[Dict]:
        """获取剪辑片段信息"""
        return [
            {
                'start': cp.start_time,
                'end': cp.end_time,
                'duration': cp.duration,
                'confidence': cp.confidence,
                'reason': cp.reason
            }
            for cp in self.cut_points
        ]
    
    def apply_cuts(self, video_path: str, output_path: str, 
                   codec: str = 'libx264', bitrate: str = '5000k') -> bool:
        """
        应用剪辑并导出
        
        Args:
            video_path: 源视频路径
            output_path: 输出路径
            codec: 编码器
            bitrate: 比特率
        
        Returns:
            是否成功
        """
        try:
            if not self.cut_points:
                logger.error("没有剪辑点，请先执行 smart_cut()")
                return False
            
            from moviepy.editor import concatenate_videoclips, VideoFileClip
            
            clip = VideoFileClip(video_path)
            segments = []
            
            for cp in self.cut_points:
                segment = clip.subclipped(cp.start_time, cp.end_time)
                segments.append(segment)
            
            # 合并所有片段
            final_clip = concatenate_videoclips(segments)
            
            # 导出
            final_clip.write_videofile(
                output_path,
                codec=codec,
                bitrate=bitrate,
                verbose=False,
                logger=None
            )
            
            clip.close()
            final_clip.close()
            
            logger.info(f"已导出到: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"应用剪辑失败: {e}")
            return False
    
    def clear(self):
        """清空剪辑点"""
        self.cut_points = []
        logger.info("剪辑点已清空")
