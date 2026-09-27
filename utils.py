#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用工具模块 - 视频信息获取
不依赖ffprobe，用ffmpeg获取视频信息
"""

import os
import subprocess
import re

# ffmpeg路径 - 请根据你的实际环境修改
FFMPEG = r"ffmpeg"

def get_video_info(video_path):
    """用ffmpeg获取视频信息（不依赖ffprobe）"""
    cmd = [FFMPEG, "-i", video_path]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    output = result.stderr  # ffmpeg把信息输出到stderr
    
    info = {
        "width": 1080,
        "height": 1920,
        "duration": 60.0,
        "has_audio": True,
        "fps": 30
    }
    
    # 解析时长 Duration: 00:00:20.00, start: 0.000000, bitrate: ...
    duration_match = re.search(r'Duration:\s+(\d+):(\d+):([\d.]+)', output)
    if duration_match:
        hours = int(duration_match.group(1))
        minutes = int(duration_match.group(2))
        seconds = float(duration_match.group(3))
        info["duration"] = hours * 3600 + minutes * 60 + seconds
    
    # 解析分辨率 Stream #0:0: Video: ..., 1080x1920 [SAR ...]
    res_match = re.search(r'(\d{2,5})x(\d{2,5})', output)
    if res_match:
        info["width"] = int(res_match.group(1))
        info["height"] = int(res_match.group(2))
    
    # 解析帧率 fps
    fps_match = re.search(r'(\d+(?:\.\d+)?)\s*fps', output)
    if fps_match:
        info["fps"] = float(fps_match.group(1))
    
    # 检查是否有音频流
    info["has_audio"] = "Audio:" in output
    
    return info

def get_video_duration(video_path):
    """获取视频时长（秒）"""
    info = get_video_info(video_path)
    return info["duration"]

def get_video_resolution(video_path):
    """获取视频分辨率"""
    info = get_video_info(video_path)
    return info["width"], info["height"]

def has_audio_stream(video_path):
    """检查视频是否有音频流"""
    info = get_video_info(video_path)
    return info["has_audio"]

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        info = get_video_info(sys.argv[1])
        print(f"视频: {sys.argv[1]}")
        print(f"分辨率: {info['width']}x{info['height']}")
        print(f"时长: {info['duration']:.1f}秒")
        print(f"帧率: {info['fps']}")
        print(f"有音频: {info['has_audio']}")
    else:
        print("用法: python utils.py <视频路径>")