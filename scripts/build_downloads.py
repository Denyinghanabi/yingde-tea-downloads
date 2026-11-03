"""Build the selected H5, Premiere project, video and Word deliverables."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
OUTPUT = ROOT / 'output/release'
H5_FILES = [
    'index.html', 'style.css', 'script.js', 'Logo源文件/tea-logo.svg',
    '素材精选/tea_garden_main.jpg', '素材精选/mountain_garden.jpg',
    '素材精选/tea_picker.jpg', '素材精选/tea_pour.jpg',
    '素材精选/tea_set.jpg', '素材精选/鸟声.mp3',
]


def copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def archive(destination, entries):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as output:
        for source, relative in entries:
            if source is None:
                output.writestr(relative.rstrip('/') + '/', b'')
            else:
                output.write(source, relative)


def size(path):
    return f'{path.stat().st_size / 1024 / 1024:.1f} MB'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True, help='Final deliverables folder')
    source = parser.parse_args().source
    required = [source / '01_H5/H5作品' / file for file in H5_FILES]
    required += [source / '02_视频/英德红茶_片头动效版.prproj', source / '英德红茶视频.mp4', source / '英德红茶图文新闻稿.docx']
    subtitle_names = ['字幕.srt', '英德红茶_多轨字幕.srt']
    required += [source / '02_视频' / name for name in subtitle_names]
    for file in required:
        if not file.is_file():
            raise FileNotFoundError(file)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for relative in H5_FILES:
        copy(source / '01_H5/H5作品' / relative, PUBLIC / 'h5' / relative)
    copy(source / '02_视频/英德红茶_片头动效版.prproj', PUBLIC / 'files/yingde-premiere.prproj')
    for name in subtitle_names:
        copy(source / '02_视频' / name, PUBLIC / 'files' / name)
    copy(source / '英德红茶图文新闻稿.docx', PUBLIC / 'files/yingde-news.docx')
    copy(source / '英德红茶视频.mp4', OUTPUT / 'yingde-video.mp4')
    pr_instructions = OUTPUT / 'PR使用说明.txt'
    pr_instructions.write_text(
        'PR 工程使用说明\n\n'
        '1. 先完整解压压缩包，再打开 PR源文件 文件夹。\n'
        '2. 将 U 盘中原“素材文件夹”里的内容复制到本包的“素材文件夹”中。'
        '保留“视频子文件夹”“音频素材”等原有目录，不要再套一层“素材文件夹”，'
        '也不要把不同目录的同名文件混放。\n'
        '3. 使用 Adobe Premiere Pro 打开“英德红茶_片头动效版.prproj”。\n'
        '4. 如提示“媒体脱机”，选择“链接媒体”，定位到本包素材文件夹中的对应文件。'
        'Premiere 通常可以继续找到同目录的其他素材；仍未找到的文件需逐项定位。\n'
        '5. 字幕.srt 和 英德红茶_多轨字幕.srt 已附，请与 PR 工程放在同一目录。\n\n'
        '本包的“素材文件夹”有意留空，不包含原始视频、音乐和音效。'
        'PR 工程保留原始文件内容，因此换电脑后仍可能需要重新链接媒体。'
        '若提示缺少参考视频“短视频.mp4”，可从 U 盘另行定位对应文件。\n',
        encoding='utf-8-sig')
    pr_entries = [
        (PUBLIC / 'files/yingde-premiere.prproj', 'PR源文件/英德红茶_片头动效版.prproj'),
        (None, 'PR源文件/素材文件夹/'),
        (pr_instructions, 'PR源文件/使用说明.txt'),
    ] + [(PUBLIC / 'files' / name, 'PR源文件/' + name) for name in subtitle_names]
    archive(PUBLIC / 'downloads/yingde-premiere.zip', pr_entries)
    instructions = OUTPUT / '使用说明.txt'
    instructions.write_text(
        '英德红茶作品下载包\n\n'
        'H5：打开 H5/index.html 可离线查看，须完整保留文件夹。\n'
        'PR 源文件：PR源文件 目录内有 PR 工程、空的“素材文件夹”、字幕和使用说明。'
        '将 U 盘中原素材文件夹的内容拷入，保留目录结构，再打开工程重新链接媒体。\n'
        '视频：MP4 成片，可直接播放。\n'
        '新闻稿：Word 可编辑文档。\n\n'
        '本包只包含上述四项。H5 内的图片、Logo 和环境音为运行必需资源。'
        '没有附带原始素材库、参考素材、缓存、历史版本或 PDF。\n', encoding='utf-8-sig')
    h5_entries = [(PUBLIC / 'h5' / file, 'H5/' + file) for file in H5_FILES]
    archive(PUBLIC / 'downloads/yingde-h5.zip', h5_entries)
    archive(OUTPUT / 'yingde-complete.zip', h5_entries + pr_entries + [
        (OUTPUT / 'yingde-video.mp4', '视频/英德红茶视频.mp4'),
        (PUBLIC / 'files/yingde-news.docx', '新闻稿/英德红茶图文新闻稿.docx'),
        (instructions, '使用说明.txt'),
    ])
    files = [PUBLIC / 'h5' / file for file in H5_FILES]
    files += [PUBLIC / 'files/yingde-premiere.prproj', PUBLIC / 'files/yingde-news.docx', PUBLIC / 'downloads/yingde-h5.zip', OUTPUT / 'yingde-video.mp4', OUTPUT / 'yingde-complete.zip']
    files += [PUBLIC / 'downloads/yingde-premiere.zip'] + [PUBLIC / 'files' / name for name in subtitle_names]
    manifest = [{'path': ('downloads/' + f.name) if f.parent == OUTPUT else f.relative_to(PUBLIC).as_posix(), 'bytes': f.stat().st_size, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]
    (PUBLIC / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    replacements = {'{{H5_SIZE}}': size(PUBLIC / 'downloads/yingde-h5.zip'), '{{PR_SIZE}}': f"{(PUBLIC / 'downloads/yingde-premiere.zip').stat().st_size / 1024:.0f} KB", '{{WORD_SIZE}}': size(PUBLIC / 'files/yingde-news.docx'), '{{VIDEO_SIZE}}': size(OUTPUT / 'yingde-video.mp4'), '{{ALL_SIZE}}': size(OUTPUT / 'yingde-complete.zip')}
    template = (ROOT / 'scripts/index.template.html').read_text(encoding='utf-8')
    for key, value in replacements.items():
        template = template.replace(key, value)
    (PUBLIC / 'index.html').write_text(template, encoding='utf-8')
    print(json.dumps({'source': str(source), 'complete_zip': replacements['{{ALL_SIZE}}'], 'h5_zip': replacements['{{H5_SIZE}}'], 'files': len(manifest)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
