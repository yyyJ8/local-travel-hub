"""图片素材审计（一次性检查工具）

检查项：
1. credits.json 是否为合法 UTF-8 JSON；
2. 授权记录与磁盘文件是否一一对应；
3. 是否有重复图片（同一张图被多个对象复用）；
4. 是否缺图、是否缺署名（授权合规提醒）。
"""
import hashlib
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PUBLIC = os.path.join(ROOT, "frontend", "public")
CREDITS = os.path.join(PUBLIC, "images", "credits.json")


def main():
    with open(CREDITS, encoding="utf-8") as fh:
        credits = json.load(fh)
    print(f"[OK] credits.json 合法 UTF-8 JSON，共 {len(credits)} 条记录")

    # 路径 -> 记录
    by_path = {}
    for c in credits.values():
        by_path[c["path"]] = c

    # 磁盘文件
    disk = []
    for base, _dirs, files in os.walk(os.path.join(PUBLIC, "images")):
        for f in files:
            if f.lower().endswith((".jpg", ".png")):
                rel = "/" + os.path.relpath(os.path.join(base, f), PUBLIC).replace(os.sep, "/")
                disk.append(rel)
    disk.sort()
    print(f"[OK] 磁盘图片 {len(disk)} 张")

    missing_credit = [p for p in disk if p not in by_path]
    missing_file = [p for p in by_path if p not in disk]
    print(f"{'[!!]' if missing_credit else '[OK]'} 有文件但无授权记录：{missing_credit or '无'}")
    print(f"{'[!!]' if missing_file else '[OK]'} 有授权记录但无文件：{missing_file or '无'}")

    # 重复图片检测（按内容 md5）
    hashes = defaultdict(list)
    for rel in disk:
        path = os.path.join(PUBLIC, rel.lstrip("/").replace("/", os.sep))
        with open(path, "rb") as fh:
            hashes[hashlib.md5(fh.read()).hexdigest()].append(rel)
    dups = {h: v for h, v in hashes.items() if len(v) > 1}
    print(f"{'[!!]' if dups else '[OK]'} 内容完全相同的重复图：{len(dups)} 组")
    for h, files in dups.items():
        print(f"      重复：{'、'.join(files)}")

    # 署名缺失提醒
    no_artist = [c["path"] for c in credits.values() if c["artist"] in ("未署名", "", "见来源页")]
    print(f"{'[注意]' if no_artist else '[OK]'} 未署名的图片 {len(no_artist)} 张：{no_artist or '无'}")

    print("\n逐张清单（对象 -> 文件 <- 原始文件 / 授权）：")
    for c in sorted(credits.values(), key=lambda x: x["path"]):
        print(f"  {c['item']:5} {c['path']:28} {c['license']:14} {c['title'][5:70]}")

    total = sum(
        os.path.getsize(os.path.join(PUBLIC, p.lstrip("/").replace("/", os.sep))) for p in disk
    )
    print(f"\n合计体积：{total / 1024 / 1024:.2f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
