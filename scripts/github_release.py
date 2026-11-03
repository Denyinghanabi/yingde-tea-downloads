"""Publish public artifacts using Git Credential Manager, without persisting tokens."""
from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = 'Denyinghanabi/yingde-tea-downloads'
TAG = 'v1.0.0'


def credential_config():
    result = subprocess.run(['git', '-c', 'credential.interactive=never', 'credential', 'fill'], input='protocol=https\nhost=github.com\nusername=Denyinghanabi\n\n', capture_output=True, text=True, encoding='utf-8', check=True)
    values = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
    return 'header = ' + json.dumps('Authorization: Bearer ' + values['password']) + '\n'


def api(config, method, path, payload=None, upload=None, allow_missing=False):
    url = path if path.startswith('https://') else 'https://api.github.com' + path
    args = ['curl.exe', '--ssl-revoke-best-effort', '-sS', '--connect-timeout', '20', '--max-time', '300', '--config', '-', '-X', method, '-H', 'Accept: application/vnd.github+json', '-H', 'X-GitHub-Api-Version: 2022-11-28']
    if upload:
        args += ['-H', 'Content-Type: application/octet-stream', '--data-binary', '@' + str(upload)]
    elif payload is not None:
        args += ['-H', 'Content-Type: application/json', '--data-binary', json.dumps(payload, ensure_ascii=True)]
    args += ['-w', '\n%{http_code}', url]
    response = subprocess.run(args, input=config, capture_output=True, text=True, encoding='utf-8', check=True)
    body, status = response.stdout.rsplit('\n', 1)
    data = json.loads(body) if body.strip() else {}
    if status == '404' and allow_missing:
        return None
    if not 200 <= int(status) < 300:
        raise RuntimeError(f'GitHub API {method} {path}: HTTP {status}: {data.get("message", "request failed")}')
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['repo', 'release', 'status'])
    action = parser.parse_args().action
    config = credential_config()
    if action == 'repo':
        user = api(config, 'GET', '/user')
        if user['login'].lower() != 'denyinghanabi':
            raise RuntimeError('Unexpected authenticated GitHub account')
        repo = api(config, 'GET', '/repos/' + REPO, allow_missing=True)
        if repo is None:
            repo = api(config, 'POST', '/user/repos', {'name': 'yingde-tea-downloads', 'description': '英德红茶 H5、PR 源文件、视频成品和新闻稿 Word 下载', 'homepage': 'https://ydhc.denyinghanabi.cc.cd', 'private': False, 'auto_init': False})
        if repo['private']:
            raise RuntimeError('The repository is private; refusing to change existing visibility')
        subprocess.run(['git', 'config', 'user.name', user['login']], cwd=ROOT, check=True)
        subprocess.run(['git', 'config', 'user.email', f'{user["id"]}+{user["login"]}@users.noreply.github.com'], cwd=ROOT, check=True)
        print(json.dumps({'repo': repo['html_url'], 'login': user['login']}, ensure_ascii=False))
        return
    release = api(config, 'GET', '/repos/' + REPO + '/releases/tags/' + TAG, allow_missing=True)
    if action == 'status':
        print(json.dumps({'release': release['html_url'] if release else None, 'draft': release.get('draft') if release else None, 'assets': [{'name': a['name'], 'size': a['size'], 'url': a['browser_download_url']} for a in release.get('assets', [])] if release else []}, ensure_ascii=False))
        return
    if release is None:
        releases = api(config, 'GET', '/repos/' + REPO + '/releases')
        release = next((r for r in releases if r['tag_name'] == TAG), None)
    if release is None:
        release = api(config, 'POST', '/repos/' + REPO + '/releases', {'tag_name': TAG, 'target_commitish': 'main', 'name': '英德红茶作品下载 v1.0.0', 'body': '包含 H5、PR 源文件、MP4 成片和新闻稿 Word。原始素材库不包含在内；H5 仅保留运行所需资源，PR 工程需要自行重新链接原始素材。\n\n网站：https://ydhc.denyinghanabi.cc.cd/', 'draft': True})
    existing = {a['name']: a for a in release['assets']}
    for name in ['yingde-video.mp4', 'yingde-complete.zip']:
        file = ROOT / 'output/release' / name
        if name in existing:
            if existing[name]['size'] != file.stat().st_size:
                raise RuntimeError('An existing release asset differs: ' + name)
            print('Already uploaded: ' + name, flush=True)
            continue
        print('Uploading: ' + name, flush=True)
        asset = api(config, 'POST', release['upload_url'].split('{')[0] + '?name=' + name, upload=file)
        if asset['size'] != file.stat().st_size:
            raise RuntimeError('Upload size mismatch: ' + name)
        print(json.dumps({'uploaded': asset['name'], 'bytes': asset['size']}), flush=True)
    if release['draft']:
        release = api(config, 'PATCH', '/repos/' + REPO + '/releases/' + str(release['id']), {'draft': False})
    print(json.dumps({'release': release['html_url'], 'draft': release['draft']}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
