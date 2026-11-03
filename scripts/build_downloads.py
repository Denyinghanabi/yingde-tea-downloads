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
            output.write(source, relative)


def size(path):
    return f'{path.stat().st_size / 1024 / 1024:.1f} MB'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True, help='Final deliverables folder')
    source = parser.parse_args().source
    required = [source / '01_H5/H5作品' / file for file in H5_FILES]
    required += [source / '02_视频/英德红茶_片头动效版.prproj', source / '英德红茶视频.mp4', source / '英德红茶图文新闻稿.docx']
    for file in required:
        if not file.is_file():
            raise FileNotFoundError(file)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for relative in H5_FILES:
        copy(source / '01_H5/H5作品' / relative, PUBLIC / 'h5' / relative)
    copy(source / '02_视频/英德红茶_片头动效版.prproj', PUBLIC / 'files/yingde-premiere.prproj')
    copy(source / '英德红茶图文新闻稿.docx', PUBLIC / 'files/yingde-news.docx')
    copy(source / '英德红茶视频.mp4', OUTPUT / 'yingde-video.mp4')
    instructions = OUTPUT / '使用说明.txt'
    instructions.write_text(
        '英德红茶作品下载包\n\n'
        'H5：打开 H5/index.html 可离线查看，须完整保留文件夹。\n'
        'PR 源文件：使用 Adobe Premiere Pro 打开。未附原始素材，需自行重新链接媒体。\n'
        '视频：MP4 成片，可直接播放。\n'
        '新闻稿：Word 可编辑文档。\n\n'
        '本包只包含上述四项。H5 内的图片、Logo 和环境音为运行必需资源。'
        '没有附带原始素材库、参考素材、缓存、历史版本或 PDF。\n', encoding='utf-8-sig')
    h5_entries = [(PUBLIC / 'h5' / file, 'H5/' + file) for file in H5_FILES]
    archive(PUBLIC / 'downloads/yingde-h5.zip', h5_entries)
    archive(OUTPUT / 'yingde-complete.zip', h5_entries + [
        (PUBLIC / 'files/yingde-premiere.prproj', 'PR源文件/英德红茶_片头动效版.prproj'),
        (OUTPUT / 'yingde-video.mp4', '视频/英德红茶视频.mp4'),
        (PUBLIC / 'files/yingde-news.docx', '新闻稿/英德红茶图文新闻稿.docx'),
        (instructions, '使用说明.txt'),
    ])
    files = [PUBLIC / 'h5' / file for file in H5_FILES]
    files += [PUBLIC / 'files/yingde-premiere.prproj', PUBLIC / 'files/yingde-news.docx', PUBLIC / 'downloads/yingde-h5.zip', OUTPUT / 'yingde-video.mp4', OUTPUT / 'yingde-complete.zip']
    manifest = [{'path': ('downloads/' + f.name) if f.parent == OUTPUT else f.relative_to(PUBLIC).as_posix(), 'bytes': f.stat().st_size, 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]
    (PUBLIC / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    replacements = {'{{H5_SIZE}}': size(PUBLIC / 'downloads/yingde-h5.zip'), '{{PR_SIZE}}': f"{(PUBLIC / 'files/yingde-premiere.prproj').stat().st_size / 1024:.0f} KB", '{{WORD_SIZE}}': size(PUBLIC / 'files/yingde-news.docx'), '{{VIDEO_SIZE}}': size(OUTPUT / 'yingde-video.mp4'), '{{ALL_SIZE}}': size(OUTPUT / 'yingde-complete.zip')}
    template = (ROOT / 'scripts/index.template.html').read_text(encoding='utf-8')
    for key, value in replacements.items():
        template = template.replace(key, value)
    (PUBLIC / 'index.html').write_text(template, encoding='utf-8')
    print(json.dumps({'source': str(source), 'complete_zip': replacements['{{ALL_SIZE}}'], 'h5_zip': replacements['{{H5_SIZE}}'], 'files': len(manifest)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
