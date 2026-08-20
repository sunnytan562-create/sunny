"""
本地视频文件管理系统
用于扫描、管理和组织本地视频素材
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

from moviepy.editor import VideoFileClip

logger = logging.getLogger(__name__)


@dataclass
class VideoFile:
    """视频文件数据类"""
    path: str
    name: str
    size_mb: float
    duration: float
    resolution: str
    fps: float
    bitrate: str
    codec: str
    audio: bool
    created_at: str
    file_hash: str
    
    def to_dict(self):
        return asdict(self)


class LocalVideoManager:
    """本地视频管理器"""
    
    def __init__(self, library_dir: str = "./video_library"):
        """
        初始化视频管理器
        
        Args:
            library_dir: 视频库目录
        """
        self.library_dir = Path(library_dir)
        self.library_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.library_dir / "metadata.json"
        self.videos: Dict[str, VideoFile] = {}
        
        # 创建子目录
        self.raw_videos_dir = self.library_dir / "raw_videos"
        self.processed_videos_dir = self.library_dir / "processed_videos"
        self.favorites_dir = self.library_dir / "favorites"
        self.trash_dir = self.library_dir / "trash"
        
        for dir_path in [self.raw_videos_dir, self.processed_videos_dir, 
                         self.favorites_dir, self.trash_dir]:
            dir_path.mkdir(exist_ok=True)
        
        self.load_metadata()
        logger.info(f"视频库已初始化: {self.library_dir}")
    
    def _calculate_file_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """计算文件哈希值"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def add_video(self, video_path: str, category: str = "raw_videos") -> Optional[VideoFile]:
        """
        添加视频到库
        
        Args:
            video_path: 视频文件路径
            category: 类别 (raw_videos, processed_videos, favorites)
        
        Returns:
            VideoFile 对象或 None
        """
        try:
            video_path = Path(video_path)
            
            if not video_path.exists():
                logger.error(f"视频文件不存在: {video_path}")
                return None
            
            # 计算文件哈希，避免重复
            file_hash = self._calculate_file_hash(str(video_path))
            if file_hash in self.videos:
                logger.warning(f"视频已存在: {video_path.name}")
                return self.videos[file_hash]
            
            # 打开视频获取信息
            clip = VideoFileClip(str(video_path))
            
            # 计算比特率
            size_bits = os.path.getsize(video_path) * 8
            bitrate = f"{int(size_bits / clip.duration / 1000)}k"
            
            # 获取编码信息（简化版）
            codec = "unknown"
            if str(video_path).endswith('.mp4'):
                codec = "h264"
            elif str(video_path).endswith('.avi'):
                codec = "mpeg4"
            elif str(video_path).endswith('.mkv'):
                codec = "h264/h265"
            
            video_file = VideoFile(
                path=str(video_path),
                name=video_path.name,
                size_mb=os.path.getsize(video_path) / (1024 * 1024),
                duration=clip.duration,
                resolution=f"{clip.w}x{clip.h}",
                fps=clip.fps,
                bitrate=bitrate,
                codec=codec,
                audio=clip.audio is not None,
                created_at=datetime.now().isoformat(),
                file_hash=file_hash
            )
            
            clip.close()
            
            # 复制到库目录
            category_dir = getattr(self, f"{category}_dir")
            dest_path = category_dir / video_path.name
            
            if not dest_path.exists():
                import shutil
                shutil.copy2(video_path, dest_path)
                logger.info(f"视频已复制: {dest_path}")
            
            video_file.path = str(dest_path)
            self.videos[file_hash] = video_file
            self.save_metadata()
            
            logger.info(f"视频已添加: {video_file.name}")
            return video_file
        
        except Exception as e:
            logger.error(f"添加视频失败: {e}")
            return None
    
    def scan_directory(self, directory: str, recursive: bool = True, 
                      category: str = "raw_videos") -> List[VideoFile]:
        """
        扫描目录中的视频文件
        
        Args:
            directory: 目录路径
            recursive: 是否递归扫描
            category: 视频类别
        
        Returns:
            视频文件列表
        """
        added_videos = []
        dir_path = Path(directory)
        
        if not dir_path.exists():
            logger.error(f"目录不存在: {directory}")
            return added_videos
        
        # 支持的视频格式
        video_extensions = ('*.mp4', '*.avi', '*.mov', '*.mkv', '*.flv', '*.wmv', '*.webm')
        
        # 扫描视频文件
        if recursive:
            pattern = f"**/*"
            files = dir_path.rglob("*")
        else:
            pattern = "*"
            files = dir_path.glob("*")
        
        for file_path in files:
            if file_path.is_file() and file_path.suffix.lower() in [f.replace("*", "") for f in video_extensions]:
                video_file = self.add_video(str(file_path), category)
                if video_file:
                    added_videos.append(video_file)
        
        logger.info(f"扫描完成: 添加了 {len(added_videos)} 个视频")
        return added_videos
    
    def get_video(self, video_hash: str) -> Optional[VideoFile]:
        """获取视频信息"""
        return self.videos.get(video_hash)
    
    def list_videos(self, category: Optional[str] = None) -> List[VideoFile]:
        """
        列出视频
        
        Args:
            category: 类别过滤
        
        Returns:
            视频列表
        """
        videos = list(self.videos.values())
        
        if category:
            category_dir = getattr(self, f"{category}_dir", None)
            if category_dir:
                videos = [v for v in videos if str(category_dir) in v.path]
        
        return videos
    
    def delete_video(self, video_hash: str, move_to_trash: bool = True) -> bool:
        """
        删除视频
        
        Args:
            video_hash: 视频哈希
            move_to_trash: 是否移动到回收站
        
        Returns:
            是否成功
        """
        try:
            if video_hash not in self.videos:
                return False
            
            video = self.videos[video_hash]
            video_path = Path(video.path)
            
            if move_to_trash and video_path.exists():
                import shutil
                shutil.move(str(video_path), str(self.trash_dir / video_path.name))
            elif video_path.exists():
                video_path.unlink()
            
            del self.videos[video_hash]
            self.save_metadata()
            
            logger.info(f"视频已删除: {video.name}")
            return True
        
        except Exception as e:
            logger.error(f"删除视频失败: {e}")
            return False
    
    def search_videos(self, keyword: str) -> List[VideoFile]:
        """搜索视频"""
        keyword = keyword.lower()
        return [v for v in self.videos.values() 
                if keyword in v.name.lower()]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        videos = list(self.videos.values())
        
        return {
            'total_videos': len(videos),
            'total_size_gb': sum(v.size_mb for v in videos) / 1024,
            'total_duration_hours': sum(v.duration for v in videos) / 3600,
            'videos_with_audio': sum(1 for v in videos if v.audio),
            'average_duration': sum(v.duration for v in videos) / len(videos) if videos else 0,
            'resolutions': list(set(v.resolution for v in videos)),
            'codecs': list(set(v.codec for v in videos))
        }
    
    def save_metadata(self):
        """保存元数据到文件"""
        try:
            metadata = {
                'videos': {k: v.to_dict() for k, v in self.videos.items()},
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info("元数据已保存")
        except Exception as e:
            logger.error(f"保存元数据失败: {e}")
    
    def load_metadata(self):
        """从文件加载元数据"""
        try:
            if not self.metadata_file.exists():
                logger.info("元数据文件不存在，创建新的")
                return
            
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            self.videos = {}
            for file_hash, video_data in metadata.get('videos', {}).items():
                # 验证文件是否仍然存在
                if Path(video_data['path']).exists():
                    self.videos[file_hash] = VideoFile(**video_data)
            
            logger.info(f"元数据已加载: {len(self.videos)} 个视频")
        except Exception as e:
            logger.error(f"加载元数据失败: {e}")
    
    def export_video(self, video_hash: str, output_path: str) -> bool:
        """导出视频到指定位置"""
        try:
            if video_hash not in self.videos:
                return False
            
            import shutil
            video = self.videos[video_hash]
            shutil.copy2(video.path, output_path)
            
            logger.info(f"视频已导出: {output_path}")
            return True
        except Exception as e:
            logger.error(f"导出视频失败: {e}")
            return False
