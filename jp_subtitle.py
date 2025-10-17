import whisper
import srt
import datetime
import os
import subprocess
import tempfile
from tqdm import tqdm

# === 1. 配置区域 ===
# *********************************************************************************
VIDEO_FOLDER = "D:\\BaiduNetdiskDownload\\S01"  # 【请修改】输入视频所在的文件夹
MODEL_SIZE = "small"                         # Whisper模型大小: tiny, base, small, medium, large
LANGUAGE = "Japanese"                        # 视频中的原始语言
# *********************************************************************************

# === 2. 初始化 Whisper 模型 (全局加载一次，提高效率) ===
print("🎧 正在加载 Whisper 模型中...")
try:
    model = whisper.load_model(MODEL_SIZE)
    print(f"✅ Whisper 模型 '{MODEL_SIZE}' 加载成功。")
except Exception as e:
    print(f"❌ 加载 Whisper 模型失败: {e}")
    exit()

# === 3. 查找并处理文件夹中的所有视频文件 ===
# 支持的视频文件扩展名
supported_extensions = ['.mp4', '.mkv', '.ts', '.avi', '.mov', '.flv', '.webm']

# 筛选出文件夹中所有支持的视频文件
video_files = [f for f in os.listdir(VIDEO_FOLDER)
               if os.path.isfile(os.path.join(VIDEO_FOLDER, f)) and os.path.splitext(f)[1].lower() in supported_extensions]

if not video_files:
    print(f"❌ 在文件夹 '{VIDEO_FOLDER}' 中未找到任何支持的视频文件。")
    exit()

print(f"📂 发现 {len(video_files)} 个视频文件，准备开始处理...")

# 循环处理每个视频文件
for index, video_name in enumerate(video_files):
    video_path = os.path.join(VIDEO_FOLDER, video_name)
    # 生成与视频文件同名的 .srt 字幕文件路径
    output_srt = os.path.splitext(video_path)[0] + ".srt"

    print("-" * 80)
    print(f"🎬 开始处理第 {index + 1}/{len(video_files)} 个文件: {video_name}")

    # 如果字幕文件已存在，则跳过
    if os.path.exists(output_srt):
        print(f"🟡 字幕文件 '{os.path.basename(output_srt)}' 已存在，自动跳过。")
        continue

    # === Step A：提取音频 ===
    print(" extracting audio...")
    audio_path = None # 初始化变量
    try:
        # 创建临时音频文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
            audio_path = tmp_audio.name

        # 使用 ffmpeg 提取音频（静默输出）
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 提取音频失败。请确保 ffmpeg 已正确安装并配置在系统 PATH 中。")
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path) # 清理失败时产生的临时文件
        continue # 继续处理下一个视频

    # === Step B：语音识别 (Whisper) ===
    print(f" transcribing audio to {LANGUAGE}...")
    try:
        # 实际识别，Whisper 会在控制台显示自己的进度条
        result = model.transcribe(audio_path, language=LANGUAGE, task="transcribe", fp16=False)
        segments = result["segments"]
    except Exception as e:
        print(f"❌ Whisper 语音识别失败: {e}")
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        continue

    # === Step C：生成并保存字幕文件 ===
    print(" generating SRT file...")
    subs = []
    for seg in segments:
        start_time = datetime.timedelta(seconds=seg["start"])
        end_time = datetime.timedelta(seconds=seg["end"])
        text = seg["text"].strip()

        # 如果识别出的文本为空，则跳过
        if not text:
            continue
        
        # 【修改点】直接使用 Whisper 识别出的原文
        subs.append(srt.Subtitle(index=len(subs) + 1, start=start_time, end=end_time, content=text))

    try:
        with open(output_srt, "w", encoding="utf-8") as f:
            f.write(srt.compose(subs))
    except Exception as e:
        print(f"❌ 保存字幕文件失败: {e}")

    # 删除临时音频文件
    if audio_path and os.path.exists(audio_path):
        os.remove(audio_path)

    print(f"✅ 处理完成！字幕已保存到: {output_srt}")

print("-" * 80)
print("🎉 所有视频文件处理完毕！")