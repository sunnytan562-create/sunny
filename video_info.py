"""
视频信息查询工具
获取和分析视频文件的详细信息
"""

import os
import json
import logging
from pathlib import Path
import click
from moviepy.editor import VideoFileClip

logger = logging.getLogger(__name__)


class VideoAnalyzer:
    """视频分析器"""
    
    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """
        获取视频详细信息
        
        Args:
            video_path: 视频文件路径
        
        Returns:
            视频信息字典
        """
        try:
            clip = VideoFileClip(video_path)
            
            info = {
                'file': video_path,
                'file_size_mb': os.path.getsize(video_path) / (1024 * 1024),
                'duration_seconds': clip.duration,
                'duration_formatted': f"{int(clip.duration//3600):02d}:{int((clip.duration%3600)//60):02d}:{int(clip.duration%60):02d}",
                'fps': clip.fps,
                'width': clip.w,
                'height': clip.h,
                'resolution': f"{clip.w}x{clip.h}",
                'aspect_ratio': f"{clip.w}:{clip.h}",
                'total_frames': int(clip.duration * clip.fps),
                'audio': {
                    'has_audio': clip.audio is not None,
                    'fps': clip.audio.fps if clip.audio else None,
                    'channels': clip.audio.nchannels if clip.audio else None,
                } if clip.audio else {'has_audio': False}
            }
            
            clip.close()
            return info
        
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            raise
    
    @staticmethod
    def compare_videos(video_paths: list) -> dict:
        """
        比较多个视频
        
        Args:
            video_paths: 视频文件路径列表
        
        Returns:
            比较结果
        """
        videos = []
        for path in video_paths:
            try:
                info = VideoAnalyzer.get_video_info(path)
                videos.append(info)
            except Exception as e:
                logger.error(f"无法分析 {path}: {e}")
        
        return {'videos': videos, 'count': len(videos)}
    
    @staticmethod
    def analyze_directory(directory: str, extensions: tuple = ('mp4', 'avi', 'mov', 'mkv')) -> dict:
        """
        分析目录中的所有视频
        
        Args:
            directory: 目录路径
            extensions: 文件扩展名元组
        
        Returns:
            分析结果
        """
        videos = []
        
        for ext in extensions:
            for video_path in Path(directory).glob(f'*.{ext}'):
                try:
                    info = VideoAnalyzer.get_video_info(str(video_path))
                    videos.append(info)
                except Exception as e:
                    logger.warning(f"无法分析 {video_path}: {e}")
        
        total_size = sum(v.get('file_size_mb', 0) for v in videos)
        total_duration = sum(v.get('duration_seconds', 0) for v in videos)
        
        return {
            'directory': directory,
            'video_count': len(videos),
            'videos': videos,
            'total_size_mb': total_size,
            'total_duration_seconds': total_duration,
            'total_duration_formatted': f"{int(total_duration//3600):02d}:{int((total_duration%3600)//60):02d}:{int(total_duration%60):02d}"
        }


@click.group()
def cli():
    """视频信息工具"""
    pass


@cli.command()
@click.argument('video_path')
@click.option('--output', type=click.Path(), help='输出 JSON 文件路径')
@click.option('--format', type=click.Choice(['json', 'table']), default='table', help='输出格式')
def info(video_path, output, format):
    """获取视频信息"""
    try:
        info_data = VideoAnalyzer.get_video_info(video_path)
        
        if output:
            with open(output, 'w') as f:
                json.dump(info_data, f, indent=2)
            click.echo(f"信息已保存到: {output}")
        else:
            if format == 'json':
                click.echo(json.dumps(info_data, indent=2))
            else:
                click.echo(f"{'文件':<20}: {info_data['file']}")
                click.echo(f"{'文件大小':<20}: {info_data['file_size_mb']:.2f} MB")
                click.echo(f"{'时长':<20}: {info_data['duration_formatted']} ({info_data['duration_seconds']:.2f}s)")
                click.echo(f"{'帧率':<20}: {info_data['fps']} fps")
                click.echo(f"{'分辨率':<20}: {info_data['resolution']}")
                click.echo(f"{'宽高比':<20}: {info_data['aspect_ratio']}")
                click.echo(f"{'总帧数':<20}: {info_data['total_frames']}")
                click.echo(f"{'有音频':<20}: {'是' if info_data['audio']['has_audio'] else '否'}")
                if info_data['audio']['has_audio']:
                    click.echo(f"{'音频采样率':<20}: {info_data['audio']['fps']} Hz")
                    click.echo(f"{'音频通道数':<20}: {info_data['audio']['channels']}")
    
    except Exception as e:
        click.echo(f"错误: {e}", err=True)


@cli.command()
@click.argument('directory')
@click.option('--extensions', default='mp4,avi,mov,mkv', help='文件扩展名（逗号分隔）')
@click.option('--output', type=click.Path(), help='输出 JSON 文件路径')
def batch_analyze(directory, extensions, output):
    """批量分析目录中的视频"""
    try:
        ext_tuple = tuple(ext.strip() for ext in extensions.split(','))
        result = VideoAnalyzer.analyze_directory(directory, ext_tuple)
        
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            click.echo(f"分析结果已保存到: {output}")
        else:
            click.echo(f"{'='*60}")
            click.echo(f"目录分析: {result['directory']}")
            click.echo(f"{'='*60}")
            click.echo(f"视频数量: {result['video_count']}")
            click.echo(f"总大小: {result['total_size_mb']:.2f} MB")
            click.echo(f"总时长: {result['total_duration_formatted']}")
            click.echo(f"\n{'序号':<5} {'文件':<30} {'大小(MB)':<12} {'时长':<12} {'分辨率':<12}")
            click.echo(f"{'-'*71}")
            for idx, video in enumerate(result['videos'], 1):
                click.echo(f"{idx:<5} {Path(video['file']).name:<30} {video['file_size_mb']:<12.2f} "
                          f"{video['duration_formatted']:<12} {video['resolution']:<12}")
    
    except Exception as e:
        click.echo(f"错误: {e}", err=True)


@cli.command()
@click.argument('video_paths', nargs=-1, required=True)
@click.option('--output', type=click.Path(), help='输出 JSON 文件路径')
def compare(video_paths, output):
    """比较多个视频"""
    try:
        result = VideoAnalyzer.compare_videos(list(video_paths))
        
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            click.echo(f"比较结果已保存到: {output}")
        else:
            click.echo(f"{'='*80}")
            click.echo(f"视频比较 ({result['count']} 个视频)")
            click.echo(f"{'='*80}")
            click.echo(f"{'文件':<30} {'大小(MB)':<12} {'分辨率':<12} {'时长':<12} {'帧率':<8}")
            click.echo(f"{'-'*80}")
            for video in result['videos']:
                click.echo(f"{Path(video['file']).name:<30} {video['file_size_mb']:<12.2f} "
                          f"{video['resolution']:<12} {video['duration_formatted']:<12} {video['fps']:<8}")
    
    except Exception as e:
        click.echo(f"错误: {e}", err=True)


if __name__ == '__main__':
    cli()
