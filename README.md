# 拾词 Wordleaf
浏览器本地英文照片识别、离线英汉词库、收藏与 A4 双列打印。

## 使用
上传或拍照 → 点击原图上的单词色块 → 星标收藏 → 打印预览 → 系统打印窗口保存 PDF。
首次联网点击「准备离线使用」下载全部资源。照片不会发送服务器。浏览器清理站点数据将删除离线缓存和单词薄。

支持多照片、自动倾斜校正、90度旋转、词形还原、拼写建议与手动查词、设备本地语音、历史单词薄、移动端收起收藏栏。
例句来自文章上下文。音标以词库提供的英式为主；完整展示词库收录的释义，不保证穷尽语言中的所有义项。含 ECDICT 的 5,040 条 IELTS 标签；构建会逐词校验 kajweb/dict 专八参考表 12,197 词、雅思参考表 3,575 词全部可查。参考词表不代表官方穷尽词表，释义仍来自 ECDICT；补充了 barometre、façade 两个拼写映射和一条短语释义。严重透视、模糊、手写及部分 HEIC 图片可能无法识别。暂不包含扫码跨设备传图。

## 构建
需要 Node.js 22 与 Python 3。
```
npm ci
python3 build.py
python3 -m http.server 8765 --directory dist
```
GitHub Settings → Pages → Source 选择 GitHub Actions，main 分支推送自动发布。也支持 Netlify（附 netlify.toml）。
运行时所有 OCR、模型、词典均由本站提供，不依赖第三方 API，不需要 API key。

## 数据和许可
ECDICT: https://github.com/skywind3000/ECDICT (MIT)。Tesseract.js / core 与 tessdata_fast 为 Apache-2.0。构建生成 LICENSES.txt 并保留许可。
