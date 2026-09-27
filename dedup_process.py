#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四层去重处理脚本
对切片视频执行结构层+画面层+音频层+原创增量层去重
永久禁用：镜像翻转、音频变速（铁律）
"""

import os
import sys
import random
import subprocess

# ffmpeg路径 - 请根据你的实际环境修改
FFMPEG = r"ffmpeg"
FONT = r"C:\Windows\Fonts\msyhbd.ttc"  # 微软雅黑粗体

# 30种装饰元素（需自行准备PNG文件）
decorations = [
    'heart.png', 'star.png', 'pk_badge.png', 'explosion.png', 'crown.png',
    'fire.png', 'lightning.png', 'music_note.png', 'thumbs_up.png', 'arrow_right.png',
    'speech_bubble.png', 'confetti.png', 'spotlight.png', 'gold_frame.png', 'follow_button.png',
    'rose.png', 'diamond.png', 'trophy.png', 'balloons.png', 'bow.png',
    'star_rain.png', 'heart_wings.png', 'microphone.png', 'neon.png', 'gift.png',
    'music_notes.png', 'water_splash.png', 'fire_heart.png', 'stage_light.png', 'bubbles.png'
]

# 四个角落位置
positions = {
    'top_left': '10:10',
    'top_right': 'W-w-10:10',
    'bottom_left': '10:H-h-10',
    'bottom_right': 'W-w-10:H-h-10'
}

def dedup_video(input_path, output_path, decor_dir="decorations"):
    """对单个视频执行四层去重"""
    # 随机选择2-3个装饰元素
    num_decors = random.randint(2, 3)
    selected_decors = random.sample(decorations, num_decors)
    selected_positions = random.sample(list(positions.keys()), num_decors)
    
    # 随机参数（镜像/变速已按铁律永久禁用）
    brightness = random.uniform(0.95, 1.05)
    contrast = random.uniform(0.95, 1.05)
    
    # 构建滤镜
    vf_parts = [f'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920']
    vf_parts.append(f'eq=brightness={brightness-1}:contrast={contrast}')
    vf_parts.append('unsharp=5:5:0.5')  # 锐化
    
    # 输入参数
    inputs = ['-i', input_path]
    overlays = []
    decor_filters = []
    
    for i, (decor, pos) in enumerate(zip(selected_decors, selected_positions)):
        decor_path = os.path.join(decor_dir, decor)
        if os.path.exists(decor_path):
            inputs.extend(['-i', decor_path])
            scale_filter = f"[{i+1}:v]scale=60:60,colorkey=white:0.3:0.5,format=rgba,colorchannelmixer=aa=0.75[dv{i}]"
            decor_filters.append(scale_filter)
            pos_val = positions[pos]
            if i == 0:
                overlays.append(f"[0:v][dv{i}]overlay={pos_val}[v{i}]")
            else:
                overlays.append(f"[v{i-1}][dv{i}]overlay={pos_val}[v{i}]")
    
    vf = ','.join(vf_parts)
    filter_complex = f'[0:v]{vf}[vbase];'
    if decor_filters:
        filter_complex += ';'.join(decor_filters) + ';'
    if overlays:
        filter_complex += ';'.join(overlays)
        final_v = f'[v{len(overlays)-1}]'
    else:
        final_v = '[vbase]'
    
    # 音频滤镜（禁用变速，仅提升音量）
    af = 'volume=1.1'
    
    cmd = [FFMPEG, '-y'] + inputs + [
        '-filter_complex', filter_complex,
        '-map', final_v,
        '-map', '0:a',
        '-af', af,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-movflags', '+faststart',
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return result.returncode == 0 and os.path.exists(output_path)

def batch_dedup(input_dir, output_dir):
    """批量去重"""
    os.makedirs(output_dir, exist_ok=True)
    files = sorted([f for f in os.listdir(input_dir) if f.endswith('.mp4')])
    print(f'处理 {len(files)} 个视频...')
    
    for i, filename in enumerate(files):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        if os.path.exists(output_path):
            print(f'[{i+1}/{len(files)}] ✓ 已存在: {filename}')
            continue
        print(f'[{i+1}/{len(files)}] 处理: {filename}')
        if dedup_video(input_path, output_path):
            size = os.path.getsize(output_path) / 1024 / 1024
            print(f'  ✓ 完成: {size:.1f} MB')
        else:
            print(f'  ✗ 失败')

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        batch_dedup(sys.argv[1], sys.argv[2])
    else:
        print("用法: python dedup_process.py <输入目录> <输出目录>")