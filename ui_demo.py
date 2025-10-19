import whisper
import srt
import datetime
import os
import subprocess
import tempfile
import gradio as gr

# === 1. 初始化模型 (全局加载一次，启动时加载) ===
# 将模型加载放在全局作用域，这样Gradio界面启动时模型就已加载好，
# 避免每次点击按钮都重新加载模型，大大提高响应速度。
print("="*50)
print("正在初始化，请稍候...")
print("🎧 正在加载 Whisper 模型 (small)...")
try:
    # 默认加载 small 模型，可以在界面上更改，但预加载一个可以加快首次处理速度
    model = whisper.load_model("small")
    print("✅ Whisper 'small' 模型加载成功。")
    # 创建一个字典来缓存已加载的模型
    loaded_models = {"small": model}
except Exception as e:
    print(f"❌ 加载默认 Whisper 模型失败: {e}")
    print("请确保已安装 PyTorch 且支持 CUDA (如果使用GPU)。")
    loaded_models = {}
print("="*50)


# === 2. 核心处理函数 ===
# 这是脚本的核心逻辑，被Gradio界面调用。
# 使用 yield 来逐步返回日志信息，实现流式输出。
def process_videos(video_folder, language, model_size):
    """
    处理指定文件夹中的所有视频，生成SRT字幕。
    
    Args:
        video_folder (str): 包含视频文件的文件夹路径。
        language (str): 视频的语言。
        model_size (str): 要使用的Whisper模型大小。
        
    Yields:
        str: 处理过程中的日志信息。
    """
    log_messages = []
    
    # --- 输入验证 ---
    if not video_folder or not os.path.isdir(video_folder):
        yield "❌ 错误：请输入一个有效的文件夹路径。"
        return

    log_messages.append(f"📂 目标文件夹: {video_folder}")
    log_messages.append(f"🌐 识别语言: {language}")
    log_messages.append(f"🧠 使用模型: {model_size}")
    yield "\n".join(log_messages)

    # --- 模型加载/切换 ---
    # 检查当前选择的模型是否已经加载，如果没有，则加载它
    if model_size not in loaded_models:
        try:
            log_messages.append(f"\n modeli 正在加载 Whisper 模型 '{model_size}'...")
            yield "\n".join(log_messages)
            
            new_model = whisper.load_model(model_size)
            loaded_models[model_size] = new_model
            
            log_messages.append(f"✅ 模型 '{model_size}' 加载成功。")
            yield "\n".join(log_messages)
        except Exception as e:
            log_messages.append(f"❌ 加载 Whisper 模型 '{model_size}' 失败: {e}")
            yield "\n".join(log_messages)
            return
            
    # 获取当前要使用的模型
    current_model = loaded_models[model_size]

    # --- 查找视频文件 ---
    supported_extensions = ['.mp4', '.mkv', '.ts', '.avi', '.mov', '.flv', '.webm']
    video_files = [f for f in os.listdir(video_folder)
                   if os.path.isfile(os.path.join(video_folder, f)) and os.path.splitext(f)[1].lower() in supported_extensions]

    if not video_files:
        log_messages.append("\n❌ 在指定文件夹中未找到任何支持的视频文件。")
        yield "\n".join(log_messages)
        return

    log_messages.append(f"\n▶️ 发现 {len(video_files)} 个视频文件，准备开始处理...")
    yield "\n".join(log_messages)

    # --- 循环处理 ---
    for index, video_name in enumerate(video_files):
        video_path = os.path.join(video_folder, video_name)
        output_srt = os.path.splitext(video_path)[0] + ".srt"

        log_messages.append("\n" + "-"*40)
        log_messages.append(f"🎬 ({index + 1}/{len(video_files)}) 开始处理: {video_name}")
        yield "\n".join(log_messages)

        if os.path.exists(output_srt):
            log_messages.append(f"🟡 字幕文件已存在，自动跳过。")
            yield "\n".join(log_messages)
            continue

        # Step A: 提取音频
        audio_path = None
        try:
            log_messages.append("  - 正在提取音频...")
            yield "\n".join(log_messages)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
                audio_path = tmp_audio.name

            subprocess.run([
                "ffmpeg", "-y", "-i", video_path,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", audio_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            log_messages.append(f"  - ❌ 提取音频失败: {e}。请确保 ffmpeg 已正确安装。")
            yield "\n".join(log_messages)
            if audio_path and os.path.exists(audio_path): os.remove(audio_path)
            continue
        
        # Step B: 语音识别
        try:
            log_messages.append("  - 正在进行语音识别 (这可能需要一些时间)...")
            yield "\n".join(log_messages)
            
            result = current_model.transcribe(audio_path, language=language, task="transcribe", fp16=False)
            segments = result["segments"]
        except Exception as e:
            log_messages.append(f"  - ❌ Whisper 语音识别失败: {e}")
            yield "\n".join(log_messages)
            if audio_path and os.path.exists(audio_path): os.remove(audio_path)
            continue

        # Step C: 生成并保存字幕
        log_messages.append("  - 正在生成 SRT 字幕文件...")
        yield "\n".join(log_messages)
        
        subs = []
        for seg in segments:
            if text := seg["text"].strip():
                start_time = datetime.timedelta(seconds=seg["start"])
                end_time = datetime.timedelta(seconds=seg["end"])
                subs.append(srt.Subtitle(index=len(subs) + 1, start=start_time, end=end_time, content=text))
        
        try:
            with open(output_srt, "w", encoding="utf-8") as f:
                f.write(srt.compose(subs))
            log_messages.append(f"  - ✅ 字幕已保存到: {os.path.basename(output_srt)}")
            yield "\n".join(log_messages)
        except Exception as e:
            log_messages.append(f"  - ❌ 保存字幕文件失败: {e}")
            yield "\n".join(log_messages)
        
        finally:
             if audio_path and os.path.exists(audio_path): os.remove(audio_path)

    log_messages.append("\n" + "="*40)
    log_messages.append("🎉 所有视频文件处理完毕！")
    yield "\n".join(log_messages)


# === 3. Gradio 界面定义 ===
# Whisper支持的语言列表 (部分常用)
# 格式为 [显示名称, Whisper参数值]
supported_languages = [
    ("Japanese", "Japanese"),
    ("English", "English"),
    ("Chinese", "Chinese"),
    ("Korean", "Korean"),
    ("French", "French"),
    ("German", "German"),
    ("Spanish", "Spanish"),
    ("Russian", "Russian"),
    ("Auto Detect", None) # None 会让 Whisper 自动检测
]

# Whisper 模型尺寸
model_sizes = ["tiny", "base", "small", "medium", "large"]

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 视频批量字幕生成工具 (Whisper)
        输入一个包含视频文件的文件夹路径，选择视频的语言和识别模型，点击“开始处理”即可为文件夹内所有视频生成 SRT 字幕文件。
        """
    )
    
    with gr.Row():
        folder_input = gr.Textbox(
            label="视频文件夹路径", 
            placeholder="例如: D:\\Videos\\MySeries"
        )
    
    with gr.Row():
        lang_input = gr.Dropdown(
            choices=[lang[0] for lang in supported_languages],
            value="Japanese",
            label="视频语言"
        )
        model_input = gr.Dropdown(
            choices=model_sizes,
            value="small",
            label="Whisper 模型大小"
        )
    
    start_button = gr.Button("开始处理", variant="primary")
    
    log_output = gr.Textbox(
        label="处理日志", 
        lines=15, 
        interactive=False,
        autoscroll=True
    )
    
    # 按钮点击事件
    def on_submit(folder, lang_display_name, model):
        # 将显示名称转换为Whisper需要的参数值
        lang_value = next((val for name, val in supported_languages if name == lang_display_name), None)
        
        # 【【【 这是关键修改 】】】
        # 使用 yield from 将 process_videos 生成器产出的内容直接转交给 Gradio
        yield from process_videos(folder, lang_value, model)

    start_button.click(
        fn=on_submit,
        inputs=[folder_input, lang_input, model_input],
        outputs=[log_output]
    )

# === 4. 启动界面 ===
if __name__ == "__main__":
    # 使用 share=True 会生成一个公网链接，方便分享给别人使用
    demo.launch()