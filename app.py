"""
Flask Web UI - 本地视频自动剪辑系统的网页界面
提供直观的操作界面进行视频管理和自动剪辑
"""

import os
import json
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

from local_video_manager import LocalVideoManager
from auto_cut_engine import AutoCutEngine
from video_editor import VideoEditor

# 配置
UPLOAD_FOLDER = Path("./uploads")
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'}
MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2GB

# 初始化
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

UPLOAD_FOLDER.mkdir(exist_ok=True)

# 初始化管理器
video_manager = LocalVideoManager("./video_library")
auto_cut = AutoCutEngine()

logger = logging.getLogger(__name__)


def allowed_file(filename):
    """检查文件是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== API 路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/videos', methods=['GET'])
def get_videos():
    """获取视频列表"""
    try:
        category = request.args.get('category', None)
        videos = video_manager.list_videos(category)
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'hash': hash_val,
                    'name': v.name,
                    'size_mb': round(v.size_mb, 2),
                    'duration': round(v.duration, 2),
                    'resolution': v.resolution,
                    'fps': v.fps,
                    'audio': v.audio,
                    'created_at': v.created_at
                }
                for hash_val, v in [(k, video_manager.get_video(k)) for k in video_manager.videos.keys()]
                if v
            ]
        })
    except Exception as e:
        logger.error(f"获取视频列表失败: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    try:
        stats = video_manager.get_statistics()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """上传视频"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有文件'})
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件格式'})
        
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))
        
        # 添加到库
        video = video_manager.add_video(str(filepath), category='raw_videos')
        
        if video:
            return jsonify({
                'success': True,
                'message': '上传成功',
                'data': {
                    'name': video.name,
                    'size_mb': round(video.size_mb, 2),
                    'duration': round(video.duration, 2)
                }
            })
        else:
            return jsonify({'success': False, 'error': '添加视频失败'})
    
    except Exception as e:
        logger.error(f"上传视频失败: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/scan', methods=['POST'])
def scan_directory():
    """扫描目录"""
    try:
        data = request.json
        directory = data.get('directory', '')
        
        if not directory or not os.path.exists(directory):
            return jsonify({'success': False, 'error': '目录不存在'})
        
        videos = video_manager.scan_directory(directory, recursive=True)
        
        return jsonify({
            'success': True,
            'message': f'扫描完成，添加了 {len(videos)} 个视频',
            'count': len(videos)
        })
    except Exception as e:
        logger.error(f"扫描目录失败: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/analyze/<video_hash>', methods=['GET'])
def analyze_video(video_hash):
    """分析视频"""
    try:
        video = video_manager.get_video(video_hash)
        
        if not video:
            return jsonify({'success': False, 'error': '视频不存在'})
        
        # 检测各种问题
        silence_regions = auto_cut.detect_silence(video.path)
        black_regions = auto_cut.detect_black_frames(video.path)
        scene_changes = auto_cut.detect_scene_changes(video.path)
        
        return jsonify({
            'success': True,
            'data': {
                'video_name': video.name,
                'duration': video.duration,
                'silence_regions': len(silence_regions),
                'black_regions': len(black_regions),
                'scene_changes': len(scene_changes),
                'silence_details': [
                    {'start': round(s, 2), 'end': round(e, 2)}
                    for s, e in silence_regions[:10]
                ],
                'black_details': [
                    {'start': round(s, 2), 'end': round(e, 2)}
                    for s, e in black_regions[:10]
                ]
            }
        })
    except Exception as e:
        logger.error(f"分析视频失败: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/auto-cut', methods=['POST'])
def auto_cut_video():
    """自动剪辑视频"""
    try:
        data = request.json
        video_hash = data.get('video_hash')
        target_duration = data.get('target_duration')
        remove_silence = data.get('remove_silence', True)
        remove_black = data.get('remove_black', True)
        
        video = video_manager.get_video(video_hash)
        
        if not video:
            return jsonify({'success': False, 'error': '视频不存在'})
        
        # 执行自动剪辑
        cuts = auto_cut.smart_cut(
            video.path,
            target_duration=target_duration,
            remove_silence=remove_silence,
            remove_black=remove_black
        )
        
        segments = auto_cut.get_cut_segments()
        total_kept_duration = sum(s['duration'] for s in segments)
        
        return jsonify({
            'success': True,
            'data': {
                'original_duration': video.duration,
                'kept_duration': round(total_kept_duration, 2),
                'reduction': f"{(1 - total_kept_duration/video.duration)*100:.1f}%",
                'segments': len(segments),
                'segments_detail': segments[:20]  # 只返回前20个
            }
        })
    except Exception as e:
        logger.error(f"自动剪辑失败: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/export', methods=['POST'])
def export_video():
    """导出剪辑后的视频"""
    try:
        data = request.json
        video_hash = data.get('video_hash')
        output_name = data.get('output_name', 'output')
        codec = data.get('codec', 'libx264')
        bitrate = data.get('bitrate', '5000k')
        
        video = video_manager.get_video(video_hash)
        
        if not video:
            return jsonify({'success': False, 'error': '视频不存在'})
        
        # 设置输出路径
        output_path = str(Path("./output") / f"{output_name}.mp4")
        Path("./output").mkdir(exist_ok=True)
        
        # 应用剪辑
        success = auto_cut.apply_cuts(video.path, output_path, codec, bitrate)
        
        if success:
            output_size = os.path.getsize(output_path) / (1024 * 1024)
            return jsonify({
                'success': True,
                'message': '导出成功',
                'data': {
                    'output_path': output_path,
                    'file_size_mb': round(output_size, 2)
                }
            })
        else:
            return jsonify({'success': False, 'error': '导出失败'})
    
    except Exception as e:
        logger.error(f"导出视频失败: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/delete/<video_hash>', methods=['DELETE'])
def delete_video(video_hash):
    """删除视频"""
    try:
        success = video_manager.delete_video(video_hash, move_to_trash=True)
        
        if success:
            return jsonify({'success': True, 'message': '视频已删除'})
        else:
            return jsonify({'success': False, 'error': '删除失败'})
    except Exception as e:
        logger.error(f"删除视频失败: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/search', methods=['GET'])
def search_videos():
    """搜索视频"""
    try:
        keyword = request.args.get('q', '')
        
        if not keyword:
            return jsonify({'success': False, 'error': '搜索关键词为空'})
        
        results = video_manager.search_videos(keyword)
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'name': v.name,
                    'size_mb': round(v.size_mb, 2),
                    'duration': round(v.duration, 2),
                    'resolution': v.resolution
                }
                for v in results
            ]
        })
    except Exception as e:
        logger.error(f"搜索视频失败: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/edit', methods=['POST'])
def edit_video():
    """编辑视频（手动调整）"""
    try:
        data = request.json
        video_hash = data.get('video_hash')
        start = data.get('start', 0)
        end = data.get('end')
        width = data.get('width')
        height = data.get('height')
        
        video = video_manager.get_video(video_hash)
        
        if not video:
            return jsonify({'success': False, 'error': '视频不存在'})
        
        editor = VideoEditor(video.path)
        
        if end:
            editor.trim(start, end)
        
        if width and height:
            editor.resize(width, height)
        
        output_path = f"./output/edited_{Path(video.path).stem}.mp4"
        Path("./output").mkdir(exist_ok=True)
        
        editor.export(output_path)
        editor.close()
        
        return jsonify({
            'success': True,
            'message': '编辑完成',
            'data': {'output_path': output_path}
        })
    except Exception as e:
        logger.error(f"编辑视频失败: {e}")
        return jsonify({'success': False, 'error': str(e)})


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': '页面未找到'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': '服务器错误'}), 500


if __name__ == '__main__':
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 70)
    print("🎬 本地视频自动剪辑系统 - Web 服务启动")
    print("=" * 70)
    print("🌐 访问地址: http://localhost:5000")
    print("=" * 70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
