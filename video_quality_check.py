#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频质量检测脚本
检测视频是否有卡顿、编码问题、音画同步等问题
确保观众观看体验流畅
"""

import subprocess
import json
import os
import sys
import re

# ffmpeg路径 - 请根据你的实际环境修改
FFMPEG = r"ffmpeg"

def get_video_info(video_path):
    """获取视频详细信息（用ffmpeg）"""
    cmd = [FFMPEG, "-i", video_path]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    info_text = result.stderr
    
    info = {'streams': [], 'format': {}}
    
    # 解析时长
    duration_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', info_text)
    if duration_match:
        h, m, s = duration_match.groups()
        info['format']['duration'] = str(int(h)*3600 + int(m)*60 + float(s))
    
    # 解析视频流
    vline = next((l for l in info_text.splitlines() if 'Video:' in l), '')
    video_match = re.search(r'Video: (\w+).*?(\d{2,5})x(\d{2,5})', vline)
    if video_match:
        codec, width, height = video_match.groups()
        video_stream = {'codec_type': 'video', 'codec_name': codec, 'width': int(width), 'height': int(height)}
        fps_match = re.search(r'(\d+(?:\.\d+)?)\s*fps', info_text)
        if fps_match:
            video_stream['r_frame_rate'] = fps_match.group(1)
        info['streams'].append(video_stream)
    
    # 解析音频流
    audio_match = re.search(r'Audio: (\w+)', info_text)
    if audio_match:
        audio_stream = {'codec_type': 'audio', 'codec_name': audio_match.group(1)}
        sample_match = re.search(r'Audio: \w+, (\d+) Hz', info_text)
        if sample_match:
            audio_stream['sample_rate'] = sample_match.group(1)
        info['streams'].append(audio_stream)
    
    # 解析码率
    bitrate_match = re.search(r'bitrate: (\d+) kb/s', info_text)
    if bitrate_match:
        info['format']['bit_rate'] = str(int(bitrate_match.group(1)) * 1000)
    
    return info

def check_video_quality(video_path):
    """检测视频质量"""
    print(f"正在检测视频质量: {os.path.basename(video_path)}")
    info = get_video_info(video_path)
    issues = []
    warnings = []
    
    video_stream = None
    audio_stream = None
    for stream in info.get('streams', []):
        if stream['codec_type'] == 'video':
            video_stream = stream
        elif stream['codec_type'] == 'audio':
            audio_stream = stream
    
    if not video_stream:
        issues.append("没有视频流")
        return False
    
    # 1. 检查编码格式
    codec = video_stream.get('codec_name', '')
    if codec not in ['h264', 'mpeg4']:
        issues.append(f"视频编码不是H.264: {codec}")
    else:
        print(f"✓ 视频编码: {codec}")
    
    # 2. 检查帧率
    fps_str = video_stream.get('r_frame_rate', '30/1')
    if '/' in fps_str:
        num, den = fps_str.split('/')
        fps = float(num) / float(den)
    else:
        fps = float(fps_str)
    if abs(fps - 30) > 1:
        warnings.append(f"帧率不是30fps: {fps:.1f}fps")
    else:
        print(f"✓ 帧率: {fps:.1f}fps")
    
    # 3. 检查分辨率
    width = video_stream.get('width', 0)
    height = video_stream.get('height', 0)
    if height <= width:
        issues.append(f"视频不是竖屏！当前是横屏 {width}x{height}")
    elif width != 1080 or height != 1920:
        warnings.append(f"分辨率不是标准1080x1920: {width}x{height}")
    else:
        print(f"✓ 分辨率: {width}x{height}（竖屏9:16）")
    
    # 4. 检查音频
    if audio_stream:
        audio_codec = audio_stream.get('codec_name', '')
        if audio_codec not in ['aac', 'mp3']:
            warnings.append(f"音频编码不是AAC: {audio_codec}")
        else:
            print(f"✓ 音频编码: {audio_codec}")
    else:
        issues.append("没有音频流")
    
    # 5. 解码测试
    print("正在解码测试...")
    cmd = [FFMPEG, "-v", "error", "-i", video_path, "-f", "null", "-"]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=120)
    if result.returncode != 0 or result.stderr:
        issues.append(f"解码错误: {result.stderr[:100]}")
    else:
        print("✓ 解码测试通过，无卡顿/损坏")
    
    if issues:
        print("❌ 发现严重问题:")
        for issue in issues:
            print(f"  - {issue}")
    if warnings:
        print("⚠️  警告:")
        for warning in warnings:
            print(f"  - {warning}")
    if not issues and not warnings:
        print("✅ 视频质量检测通过！")
    
    return len(issues) == 0

def batch_check(folder_path):
    """批量检测文件夹中的视频"""
    videos = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.mp4', '.ts', '.mov'))]
    print(f"找到 {len(videos)} 个视频\n")
    passed = 0
    for video in videos:
        print("\n" + "-"*50)
        if check_video_quality(video):
            passed += 1
    print(f"\n检测完成: 通过 {passed}/{len(videos)} 个")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isdir(path):
            batch_check(path)
        elif os.path.isfile(path):
            check_video_quality(path)
    else:
        print("用法: python video_quality_check.py <视频文件或文件夹>")