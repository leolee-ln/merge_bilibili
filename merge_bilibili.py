#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_bilibili.py
将 B 站缓存的 video.m4s + audio.m4s 合并成 mp4
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

FFMPEG_EXE = r"C:\Users\huawei\Downloads\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"
DOWNLOAD_DIR = Path("download")
OUTPUT_DIR   = Path("output")

# ---------- 工具函数 ----------
def sanitize_filename(name: str) -> str:
    """去掉 Windows 不允许出现在文件名里的字符"""
    for ch in r'\/:*?"<>|':
        name = name.replace(ch, "_")
    return name.strip()

def is_encrypted(m4s: Path) -> bool:
    """判断 m4s 是否被 B 站加密：文件头 16 字节 == 后续 16 字节的异或值"""
    if m4s.stat().st_size < 32:
        return False
    with m4s.open("rb") as f:
        head = f.read(16)
        tail = f.read(16)
    # 新版缓存特征：head 与 tail 做异或后得到连续 16 字节的 0x47
    return bytes(a ^ b for a, b in zip(head, tail)) == b'\x47' * 16

def decrypt_inplace(src: Path, dst: Path):
    """去掉前 16 字节，写临时文件"""
    with src.open("rb") as f_in, dst.open("wb") as f_out:
        f_in.seek(16)
        while True:
            chunk = f_in.read(1024 * 1024)
            if not chunk:
                break
            f_out.write(chunk)

def find_entry_json(start: Path):
    """从 start 目录开始递归查找所有 entry.json"""
    for root, _, files in os.walk(start):
        if "entry.json" in files:
            yield Path(root) / "entry.json"

def get_title(entry_path: Path) -> str:
    """读取 entry.json 中的 title 字段"""
    # entry.json 里可能有 \x00，先按二进制读再解码
    raw = entry_path.read_bytes().split(b'\x00', 1)[0]
    data = json.loads(raw.decode('utf-8-sig'))
    return data["title"]

def find_m4s_pair(parent: Path):
    """
    parent 是 entry.json 所在目录。
    进入 parent 下的 **唯一子目录** 寻找 video.m4s 和 audio.m4s。
    返回 (video_path, audio_path)
    """
    sub_dirs = [d for d in parent.iterdir() if d.is_dir()]
    if len(sub_dirs) != 1:
        return None, None
    target = sub_dirs[0]
    video = target / "video.m4s"
    audio = target / "audio.m4s"
    return (video, audio) if video.is_file() and audio.is_file() else (None, None)

def merge(video: Path, audio: Path, out: Path):
    """调用 ffmpeg 合成"""
    cmd = [
        FFMPEG_EXE,
        "-i", str(video),
        "-i", str(audio),
        "-c", "copy",
        "-loglevel", "error",
        str(out)
    ]
    print(f"Merging -> {out.name}")
    subprocess.run(cmd, check=True)

# ---------- 主流程 ----------
def main():
    if not DOWNLOAD_DIR.is_dir():
        print("download 目录不存在")
        sys.exit(1)
    OUTPUT_DIR.mkdir(exist_ok=True)

    for entry_json in find_entry_json(DOWNLOAD_DIR):
        try:
            title = get_title(entry_json)
            safe_title = sanitize_filename(title) + ".mp4"
            out_file = OUTPUT_DIR / safe_title

            counter = 1
            while out_file.exists():
                out_file = OUTPUT_DIR / f"{safe_title[:-4]}_{counter}.mp4"
                counter += 1

            video_raw, audio_raw = find_m4s_pair(entry_json.parent)
            if not video_raw:
                continue

            # 判断是否需要解密
            need_decrypt = is_encrypted(video_raw) or is_encrypted(audio_raw)
            if not need_decrypt:
                merge(video_raw, audio_raw, out_file)
                continue

            # 需要解密，写临时文件
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_video = Path(tmpdir) / "video.m4s"
                tmp_audio = Path(tmpdir) / "audio.m4s"
                decrypt_inplace(video_raw, tmp_video)
                decrypt_inplace(audio_raw, tmp_audio)
                merge(tmp_video, tmp_audio, out_file)

        except Exception as e:
            print(f"处理 {entry_json} 时出错：{e}", file=sys.stderr)

    print("全部完成！")

if __name__ == "__main__":
    main()
    sys.exit(0)
