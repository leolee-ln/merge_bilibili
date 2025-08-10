# Merge bilibili

merge bilibili video and audio to mp4

合并 B 站视频和音频为 mp4

## 准备工作

1. 下载并安装 [ffmpeg](https://ffmpeg.org/download.html)。

    可以使用 [Windows builds by BtbN](https://github.com/BtbN/FFmpeg-Builds/releases) 提供的静态编译版本。

    解压后目录中的 `\bin\ffmpeg.exe` 即为可执行文件。

2. python 环境

    安装 [Python](https://www.python.org/downloads/) 3.6 及以上版本。

3. 下载本仓库代码。

    将代码放置在 B 站缓存目录 `download` 外。

    编辑代码中的 `FFMPEG_EXE` 变量，指定 `ffmpeg.exe` 的路径。

    （也可以将代码置于任意目录，指定 `FFMPEG_EXE` `DOWNLOAD_DIR` `OUTPUT_DIR`）

## 使用方法

1. 运行 `merge_bilibili.py`。

    `python merge_bilibili.py`

2. 等待程序完成。

    默认输出到 `output` 目录。

## 注意事项

- 该脚本仅在 Windows 上测试通过。
- 该脚本不会删除原始缓存文件。
- 该脚本不会覆盖已存在的输出文件。
