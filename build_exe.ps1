# ================================
# build_exe.ps1
# 打包 app.py 为独立 exe
# ================================

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

Write-Host "🧹 Cleaning old build files..."
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force *.spec -ErrorAction SilentlyContinue

# 检查 ffmpeg.exe 是否存在
if (-not (Test-Path "ffmpeg.exe")) {
    Write-Host "❌ 找不到 ffmpeg.exe，请将 ffmpeg.exe 放到当前目录后再试。" -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Building EXE with PyInstaller..."

# 注意：这里使用反引号 ` 仅用于分行
# 如果你的 PowerShell 解析不正确，可以改成一行（我在下方提供单行版本）

pyinstaller --noconfirm --onefile --windowed `
  --add-data "ffmpeg.exe;." `
  --collect-all whisper `
  --collect-all torch `
  --collect-all numpy `
  --collect-all gradio `
  --collect-all gradio_client `
  --collect-all safehttpx `
  --collect-all groovy `
  --hidden-import gradio `
  --hidden-import gradio_client `
  --name "gen_subtitle_tool" app.py

Write-Host "`n✅ Build completed!"
Write-Host "Output file: dist\gen_subtitle_tool.exe"

# 验证 ffmpeg 是否真的被打包成功
if (Test-Path "dist\ffmpeg.exe") {
    Write-Host "✅ ffmpeg.exe successfully included."
} else {
    Write-Host "⚠️ Warning: ffmpeg.exe not found in dist folder. Copying manually..."
    Copy-Item "ffmpeg.exe" "dist\ffmpeg.exe" -Force
}
