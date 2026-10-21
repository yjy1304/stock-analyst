"""从已归档PDF生成逐页文本和校验清单；不修改PDF。使用安装pypdf的Python运行。"""
from pathlib import Path
from pypdf import PdfReader
import hashlib, json

root = Path(__file__).resolve().parent.parent
manifest = []
for path in sorted((root / '原始财报').glob('*.pdf')):
    reader = PdfReader(path)
    pages = [p.extract_text() or '' for p in reader.pages]
    (root / '原始数据' / (path.stem + '.txt')).write_text(
        '\n\n'.join(f'=== PDF页 {i+1} ===\n{t}' for i, t in enumerate(pages)), encoding='utf-8')
    manifest.append({'file': path.name, 'pages': len(pages), 'bytes': path.stat().st_size,
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    print(path.name, len(pages), flush=True)
(root / '原始数据' / '文件校验.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
