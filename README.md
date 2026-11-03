# 英德红茶作品下载

下载网站：<https://ydhc.denyinghanabi.cc.cd/>

包含用户选定的四项：H5 交互作品、视频 PR 源文件、MP4 视频成品、新闻稿 Word。支持单独下载和全部下载，H5 也可以在线打开。

PR 下载提供 ZIP：解压后 `PR源文件/` 内有一个原始 `.prproj` 工程、空的 `素材文件夹/`、两个字幕文件及使用说明。将 U 盘中原素材文件夹的内容复制进去并保持目录结构，打开工程后按需重新链接媒体。完整作品 ZIP 也包含相同的 PR 目录。

未附原始素材库、参考素材、缓存、历史版本或 PDF。H5 只保留运行必需的图片、标志和环境音。PR 工程换电脑后需要自行重新链接媒体。

下载页和 H5 部署在 Cloudflare Workers。超过静态文件大小限制的视频和完整 ZIP 存放在本仓库的公开 Release 中，由 Worker 流式提供下载，无需登录。每个文件的 SHA-256 见 `public/manifest.json`。

重新打包：`python scripts/build_downloads.py --source "最终成品文件夹路径"`。脚本只读原始作品，生成 `public/` 及忽略上传的 `output/release/`。更新 Release 的两个大文件后，运行 `wrangler deploy` 更新网站。

作品的著作权和使用权限归原权利人所有。
