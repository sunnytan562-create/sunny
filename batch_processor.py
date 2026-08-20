"""
批量视频处理器
支持从配置文件批量处理多个视频任务
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import click

from video_editor import VideoEditor, VideoProcessor

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, max_workers: int = 2):
        """
        初始化批量处理器
        
        Args:
            max_workers: 最大并行处理数
        """
        self.max_workers = max_workers
        self.results = []
    
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单个任务
        
        Args:
            task: 任务配置
        
        Returns:
            处理结果
        """
        task_name = task.get('name', 'unknown')
        input_path = task.get('input')
        output_path = task.get('output')
        actions = task.get('actions', [])
        
        logger.info(f"开始处理任务: {task_name}")
        
        try:
            editor = VideoEditor(input_path)
            
            # 执行所有操作
            for action in actions:
                action_type = action.get('type')
                
                if action_type == 'trim':
                    start = action.get('start', 0)
                    end = action.get('end')
                    editor.trim(start, end)
                
                elif action_type == 'resize':
                    width = action.get('width')
                    height = action.get('height')
                    maintain_ratio = action.get('maintain_ratio', True)
                    editor.resize(width, height, maintain_ratio)
                
                elif action_type == 'rotate':
                    angle = action.get('angle', 0)
                    editor.rotate(angle)
                
                elif action_type == 'speed':
                    speed = action.get('speed', 1.0)
                    editor.change_speed(speed)
                
                elif action_type == 'watermark':
                    watermark_path = action.get('watermark_path')
                    position = action.get('position', 'bottom_right')
                    opacity = action.get('opacity', 0.7)
                    editor.add_watermark(watermark_path, position, opacity)
                
                elif action_type == 'fps':
                    fps = action.get('fps', 30)
                    editor.set_fps(fps)
                
                else:
                    logger.warning(f"未知的操作类型: {action_type}")
            
            # 导出
            codec = task.get('codec', 'libx264')
            audio_codec = task.get('audio_codec', 'aac')
            bitrate = task.get('bitrate', '5000k')
            
            editor.export(output_path, codec, audio_codec, bitrate)
            editor.close()
            
            result = {
                'task_name': task_name,
                'status': 'success',
                'input': input_path,
                'output': output_path,
                'message': '处理成功'
            }
            logger.info(f"任务完成: {task_name}")
            
        except Exception as e:
            logger.error(f"任务失败: {task_name} - {e}")
            result = {
                'task_name': task_name,
                'status': 'failed',
                'input': input_path,
                'output': output_path,
                'message': str(e)
            }
        
        return result
    
    def process_batch(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量处理多个任务
        
        Args:
            tasks: 任务列表
        
        Returns:
            处理结果列表
        """
        logger.info(f"开始批量处理: {len(tasks)} 个任务")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.process_task, task): task 
                for task in tasks
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    logger.error(f"处理错误: {e}")
        
        logger.info(f"批量处理完成: {len(self.results)} 个任务")
        return self.results
    
    def load_config(self, config_path: str) -> List[Dict[str, Any]]:
        """
        从配置文件加载任务
        
        Args:
            config_path: 配置文件路径
        
        Returns:
            任务列表
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            tasks = config.get('tasks', [])
            logger.info(f"加载配置文件: {config_path} ({len(tasks)} 个任务)")
            return tasks
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def save_results(self, output_path: str):
        """
        保存处理结果
        
        Args:
            output_path: 输出文件路径
        """
        try:
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"结果已保存: {output_path}")
        except Exception as e:
            logger.error(f"保存结果失败: {e}")


@click.group()
def cli():
    """视频批量处理工具"""
    pass


@cli.command()
@click.option('--config', required=True, help='配置文件路径 (JSON)')
@click.option('--workers', default=2, help='并行处理数')
@click.option('--output-report', default='results.json', help='结果报告输出路径')
def batch(config, workers, output_report):
    """执行批量处理任务"""
    try:
        processor = BatchProcessor(max_workers=workers)
        tasks = processor.load_config(config)
        processor.process_batch(tasks)
        processor.save_results(output_report)
        
        # 显示摘要
        success_count = sum(1 for r in processor.results if r['status'] == 'success')
        failed_count = len(processor.results) - success_count
        
        click.echo(f"\n{'='*50}")
        click.echo(f"处理摘要")
        click.echo(f"{'='*50}")
        click.echo(f"总数: {len(processor.results)}")
        click.echo(f"成功: {success_count}")
        click.echo(f"失败: {failed_count}")
        click.echo(f"结果已保存: {output_report}")
        
    except Exception as e:
        click.echo(f"错误: {e}", err=True)


@cli.command()
@click.option('--template', default='examples/tasks.json', help='输出模板路径')
def generate_template(template):
    """生成配置文件模板"""
    template_config = {
        "tasks": [
            {
                "name": "clip_example",
                "input": "input_video.mp4",
                "output": "output/clip_example.mp4",
                "codec": "libx264",
                "audio_codec": "aac",
                "bitrate": "5000k",
                "actions": [
                    {
                        "type": "trim",
                        "start": 10,
                        "end": 60
                    },
                    {
                        "type": "resize",
                        "width": 1920,
                        "height": 1080,
                        "maintain_ratio": True
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
    
    output_dir = os.path.dirname(template)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(template, 'w', encoding='utf-8') as f:
        json.dump(template_config, f, indent=2, ensure_ascii=False)
    
    click.echo(f"模板已生成: {template}")


if __name__ == '__main__':
    cli()
