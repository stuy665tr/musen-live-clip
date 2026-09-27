import subprocess
import os

# ffmpeg路径 - 请根据你的实际环境修改
ffmpeg = r"ffmpeg"

def extract_keyframes(input_file, output_dir, interval=30, count=30):
    """定期提取关键帧用于内容分析"""
    os.makedirs(output_dir, exist_ok=True)
    
    for i in range(count):
        timestamp = i * interval
        output_file = os.path.join(output_dir, f"frame_{i:02d}_{timestamp}s.jpg")
        cmd = [ffmpeg, "-ss", str(timestamp), "-i", input_file, "-vframes", "1", "-q:v", "2", "-y", output_file]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if os.path.exists(output_file):
            print(f"提取成功: {timestamp}s -> {output_file}")
        else:
            print(f"提取失败: {timestamp}s")
    
    print("关键帧提取完成")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        extract_keyframes(sys.argv[1], "keyframes_output")
    else:
        print("用法: python extract_frames.py <视频路径>")