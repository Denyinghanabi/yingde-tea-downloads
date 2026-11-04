"""Build the selected final deliverables, excluding the raw media library."""
from pathlib import Path
from datetime import datetime
import argparse
import copy
import hashlib
import json
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'public'
OUTPUT = ROOT / 'output/release'


def copy_file(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != destination.resolve():
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
    value = path.stat().st_size
    return f'{value / 1024 / 1024:.1f} MB' if value >= 1024 * 1024 else f'{value / 1024:.0f} KB'


def refresh_h5(source):
    destination = PUBLIC / 'h5'
    assert destination.resolve().parent == PUBLIC.resolve()
    assert source.resolve() != destination.resolve()
    entries = sorted(p for p in source.rglob('*') if p.is_file())
    assert (source / 'index.html').is_file() and entries
    backup = ROOT / 'output/backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f') / 'h5'
    if destination.is_dir():
        shutil.copytree(destination, backup)
    wanted = {p.relative_to(source) for p in entries}
    # Prune individual stale files only after preserving a backup and checking paths.
    for old in destination.rglob('*'):
        if old.is_file() and old.relative_to(destination) not in wanted:
            assert old.resolve().is_relative_to(destination.resolve())
            old.unlink()
    for file in entries:
        copy_file(file, destination / file.relative_to(source))
    for folder in sorted(destination.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
    return [(destination / p.relative_to(source), 'H5/' + p.relative_to(source).as_posix()) for p in entries]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', type=Path, default=ROOT / 'scripts/delivery_sources.json')
    config = json.loads(parser.parse_args().sources.read_text(encoding='utf-8-sig'))
    selected = {key: (ROOT / config[key]).resolve() for key in ['h5', 'pr', 'video', 'voice', 'subtitle', 'word']}
    support = [(ROOT / value).resolve() for value in config['support']]
    for key, file in selected.items():
        assert file.is_dir() if key == 'h5' else file.is_file(), str(file)
    assert all(file.is_file() for file in support)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    h5_entries = refresh_h5(selected['h5'])
    copy_file(selected['pr'], PUBLIC / 'files/yingde-premiere.prproj')
    copy_file(selected['word'], PUBLIC / 'files/yingde-news.docx')
    copy_file(selected['video'], OUTPUT / 'yingde-video.mp4')
    copy_file(selected['voice'], PUBLIC / 'files/普通话年轻男声旁白_48kHz.wav')
    subtitle_names = ['字幕.srt', '字幕_配音同步版.srt', '英德红茶_多轨字幕.srt']
    for name in subtitle_names:
        copy_file(selected['subtitle'], PUBLIC / 'files' / name)
    for file in support:
        copy_file(file, PUBLIC / 'files' / file.name)

    pr_name = selected['pr'].name
    pr_instructions = OUTPUT / 'PR使用说明.txt'
    pr_instructions.write_text(
        '英德红茶 60秒字幕配音同步版｜PR 工程使用说明\n\n'
        f'1. 完整解压后，进入 PR源文件，打开“{pr_name}”。\n'
        '2. 将 U 盘中原“素材文件夹”里的内容复制到本包的空“素材文件夹”中。'
        '保留视频子文件夹、音频素材等目录，不要再套一层素材文件夹，不要混放同名文件。\n'
        '3. 如提示媒体脱机，使用“链接媒体”定位对应的原始视频、音乐或音效。\n'
        '4. 本包已附确认使用的“普通话年轻男声旁白_48kHz.wav”和同步字幕，'
        '请与 PR 工程放在一起；若配音提示脱机，重新定位到这一份 WAV。\n'
        '5. 字幕.srt、字幕_配音同步版.srt、英德红茶_多轨字幕.srt 内容一致，'
        '均为已对齐旁白的15条字幕，后者用于兼容工程中遗留的文件名。\n'
        '6. 旁白稿、实际使用素材清单、字幕配音逐句核对表已附。\n\n'
        '本包保留原 PR 工程，未重新剪辑。媒体箱可能还列有未使用的历史配音或参考片，'
        '可根据实际需要定位或跳过。实际使用的青年普通话配音已经附在本包内。\n'
        '原始视频、音乐和音效不随包上传，继续使用 U 盘中的素材。配音为经确认的 AI 合成声音。\n',
        encoding='utf-8-sig')
    pr_entries = [
        (PUBLIC / 'files/yingde-premiere.prproj', 'PR源文件/' + pr_name),
        (None, 'PR源文件/素材文件夹/'),
        (pr_instructions, 'PR源文件/使用说明.txt'),
        (PUBLIC / 'files/普通话年轻男声旁白_48kHz.wav', 'PR源文件/普通话年轻男声旁白_48kHz.wav'),
    ] + [(PUBLIC / 'files' / name, 'PR源文件/' + name) for name in subtitle_names]
    pr_entries += [(PUBLIC / 'files' / file.name, 'PR源文件/' + file.name) for file in support]
    h5_instructions = OUTPUT / 'H5使用说明.txt'
    h5_instructions.write_text(
        '英德红茶 H5｜2026-11-04 排版修订版\n\n'
        '解压后打开 H5/index.html。index.html、style.css、script.js 均可编辑。'
        '请完整保留图片、声音、字体、透明 Logo 等运行资源。\n'
        '下载站在线预览：https://ydhc.denyinghanabi.cc.cd/h5/\n'
        f'木疙瘩正式体验：{config["h5_platform_url"]}\n'
        f'木疙瘩可编辑工程：{config["h5_editor_url"]}\n'
        '本包提供当前 HTML 源码和实际使用资源，未附全部原始素材库。\n', encoding='utf-8-sig')
    h5_entries.append((h5_instructions, 'H5/使用说明.txt'))
    archive(PUBLIC / 'downloads/yingde-h5.zip', h5_entries)
    archive(PUBLIC / 'downloads/yingde-premiere.zip', pr_entries)
    instructions = OUTPUT / '使用说明.txt'
    instructions.write_text(
        '英德红茶作品下载包｜' + config['release_tag'] + '\n\n'
        'H5：11月4日排版修订版，包含最新换图、交互、透明绿红 Logo 和字体。打开 H5/index.html。\n'
        'PR：60秒字幕配音同步版，包含原工程、空素材文件夹、确认配音 WAV、同步字幕及说明。'
        '原始视频、音乐、音效使用 U 盘中的素材，再按需链接媒体。\n'
        '视频：60秒字幕配音同步版，使用已确认的青年普通话配音。\n'
        '新闻稿：沿用下载站的 Word 文档。\n\n'
        '本包不含全部原始素材、缓存、自动保存和历史版本。配音为已确认的 AI 合成声音。\n', encoding='utf-8-sig')
    archive(OUTPUT / 'yingde-complete.zip', h5_entries + pr_entries + [
        (OUTPUT / 'yingde-video.mp4', '视频/' + selected['video'].name),
        (PUBLIC / 'files/yingde-news.docx', '新闻稿/英德红茶图文新闻稿.docx'),
        (instructions, '使用说明.txt'),
    ])
    files = [p for p in (PUBLIC / 'h5').rglob('*') if p.is_file()]
    files += [p for p in (PUBLIC / 'files').iterdir() if p.is_file()]
    files += [PUBLIC / 'downloads' / name for name in ['yingde-h5.zip', 'yingde-premiere.zip']]
    files += [OUTPUT / name for name in ['yingde-video.mp4', 'yingde-complete.zip']]
    manifest = [{'path': 'downloads/' + p.name if p.parent == OUTPUT else p.relative_to(PUBLIC).as_posix(),
                 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    (PUBLIC / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    replacements = {'{{H5_SIZE}}': size(PUBLIC / 'downloads/yingde-h5.zip'),
                    '{{PR_SIZE}}': size(PUBLIC / 'downloads/yingde-premiere.zip'),
                    '{{WORD_SIZE}}': size(PUBLIC / 'files/yingde-news.docx'),
                    '{{VIDEO_SIZE}}': size(OUTPUT / 'yingde-video.mp4'),
                    '{{ALL_SIZE}}': size(OUTPUT / 'yingde-complete.zip'),
                    '{{VERSION}}': config['release_tag'][1:]}
    template = (ROOT / 'scripts/index.template.html').read_text(encoding='utf-8')
    for key, value in replacements.items():
        template = template.replace(key, value)
    (PUBLIC / 'index.html').write_text(template, encoding='utf-8')
    ns = {'s': 'http://www.w3.org/2000/svg'}
    ET.register_namespace('', ns['s'])
    selected_logo = ET.parse(PUBLIC / 'h5/Logo源文件/yingde-logo-green.svg').getroot()
    favicon = ET.Element('{%s}svg' % ns['s'], {'viewBox': '305 114 638 600'})
    favicon.append(copy.deepcopy(selected_logo.find("s:g[@id='emblem']", ns)))
    ET.ElementTree(favicon).write(PUBLIC / 'favicon.svg', encoding='utf-8', xml_declaration=True)
    print(json.dumps({'release': config['release_tag'], 'h5_runtime_files': len(h5_entries)-1,
                      'h5_zip': replacements['{{H5_SIZE}}'], 'pr_zip': replacements['{{PR_SIZE}}'],
                      'video': replacements['{{VIDEO_SIZE}}'], 'complete_zip': replacements['{{ALL_SIZE}}']}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
