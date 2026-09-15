"""图片素材下载脚本（把真实照片本地化到前端 public 目录）

用法：
    cd D:\\Ctrip\\backend
    D:\\Ctrip\\.venv\\Scripts\\python.exe scripts\\fetch_images.py --only S001,H001,B001   # 样品
    D:\\Ctrip\\.venv\\Scripts\\python.exe scripts\\fetch_images.py                        # 全量
    D:\\Ctrip\\.venv\\Scripts\\python.exe scripts\\fetch_images.py --force                # 覆盖重下

图源：Wikimedia Commons（自由授权），按 PHOTO_PLAN 中「品类/星级 → 关键词」的映射检索。
产物：
    frontend/public/images/{shops,hotels,banners}/*.jpg   本地图片（演示时完全离线可用）
    frontend/public/images/CREDITS.md                     来源与授权说明（必须保留）
    frontend/public/images/credits.json                   结构化来源信息
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.mock_data import PHOTO_PLAN  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PUBLIC = os.path.join(ROOT, "frontend", "public")
CREDITS_JSON = os.path.join(PUBLIC, "images", "credits.json")
CREDITS_MD = os.path.join(PUBLIC, "images", "CREDITS.md")

UA = {"User-Agent": "course-prototype-local-travel-hub/0.1 (educational demo)"}
API = "https://commons.wikimedia.org/w/api.php"

BAD_EXT = (".svg", ".pdf", ".tif", ".tiff", ".webm", ".ogv", ".gif", ".djvu", ".xcf")
BAD_WORDS = (
    "map", "logo", "diagram", "chart", "coat of arms", "flag", "seal", "sign",
    "poster", "screenshot", "icon", "drawing", "painting", "sketch", "banknote",
    "stamp", "graph", "plan of", "floor plan",
    # 艺术品/非照片类：Commons 上大量博物馆藏品是绘画、版画，会污染"真实照片"效果
    "oil on canvas", "watercolour", "watercolor", "lithograph", "engraving", "etching",
    "edward hopper", "woodcut", "aquatint", "mezzotint", "illustration", "caricature",
)

_cache: dict = {}


def api_get(params: dict) -> dict:
    params = dict(params)
    params.setdefault("format", "json")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_candidates(keyword: str, limit: int = 12) -> list:
    """按关键词检索 Commons 图片，返回候选列表（含授权信息）。"""
    if keyword in _cache:
        return _cache[keyword]
    try:
        payload = api_get(
            {
                "action": "query",
                "generator": "search",
                "gsrsearch": keyword,
                "gsrnamespace": "6",
                "gsrlimit": str(limit),
                "prop": "imageinfo",
                "iiprop": "url|size|extmetadata|mime",
                "iiurlwidth": "640",
            }
        )
    except Exception as exc:  # noqa: BLE001
        print(f"    [检索失败] {keyword}: {type(exc).__name__}: {exc}", flush=True)
        _cache[keyword] = {"strict": [], "raw": []}
        return _cache[keyword]

    pages = (payload.get("query") or {}).get("pages") or {}
    tokens = [t for t in re.split(r"[\s\-]+", keyword.lower()) if len(t) > 2]
    raw, strict = [], []
    for page in pages.values():
        title = page.get("title", "")
        low = title.lower().replace("_", " ")
        if low.endswith(BAD_EXT) or any(w in low for w in BAD_WORDS):
            continue
        info = (page.get("imageinfo") or [{}])[0]
        thumb = info.get("thumburl")
        if not thumb:
            continue
        width, height = info.get("thumbwidth") or 0, info.get("thumbheight") or 0
        if width < 500 or width < height * 0.9:  # 只要够宽、偏横构图的图
            continue
        meta = info.get("extmetadata") or {}

        def m(key):
            return re.sub(r"<[^>]+>", "", str((meta.get(key) or {}).get("value", ""))).strip()

        item = {
            "title": title,
            "thumb": thumb,
            "page": info.get("descriptionurl", ""),
            "license": m("LicenseShortName") or "见来源页",
            "artist": m("Artist") or "未署名",
            "width": width,
            "height": height,
        }
        raw.append(item)
        if not tokens or any(t in low for t in tokens):
            strict.append(item)  # 主题相关性过滤：标题命中至少一个关键词
    _cache[keyword] = {"strict": strict, "raw": raw}
    print(f"    [检索] {keyword:34} 严格 {len(strict):2} / 宽松 {len(raw):2}", flush=True)
    return _cache[keyword]


def download(url: str, dest: str) -> bool:
    """下载并做基本有效性校验（类型 / 体积 / 文件头）。

    图源 upload.wikimedia.org 存在间歇性 SSL 握手超时，因此每个候选最多尝试两个主机名
    （upload / thumb），每个主机只试一次、单次超时 12s，避免个别慢图拖垮整体。
    """
    variants = []
    if "upload.wikimedia.org" in url:
        variants.append(url.replace("upload.wikimedia.org", "thumb.wikimedia.org"))  # 实测该主机更稳
    variants.append(url)

    last_err = ""
    for variant in variants:
        try:
            req = urllib.request.Request(variant, headers=UA)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
        except Exception as exc:  # noqa: BLE001
            last_err = f"{type(exc).__name__}"
            continue
        if len(data) < 12000:
            last_err = f"体积过小 {len(data)}B"
            continue
        if not (data[:3] == b"\xff\xd8\xff" or data[:8] == b"\x89PNG\r\n\x1a\n"):
            last_err = "非 JPEG/PNG"
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(data)
        return True

    print(f"      [下载失败] {last_err}", flush=True)
    return False


def main():
    # 关键：行缓冲。此前脚本因 stdout 块缓冲导致长时间"零输出"，误判为卡死。
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:  # noqa: BLE001
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default="", help="只处理指定 ID，逗号分隔（如 S001,H001,B001）")
    parser.add_argument("--force", action="store_true", help="已存在也重新下载")
    parser.add_argument("--budget", type=int, default=240, help="本次运行的秒级时间预算，超时即停止（可重复运行续跑）")
    parser.add_argument("--covers-only", action="store_true", help="只下载封面/轮播等关键图，跳过详情页图库（默认全量）")
    parser.add_argument("--keywords", default="", help="临时覆盖取图关键词（逗号分隔），仅对 --only 指定的对象生效，用于替换不满意的图")
    args = parser.parse_args()

    only = {x.strip() for x in args.only.split(",") if x.strip()}
    plan_items = [(k, v) for k, v in PHOTO_PLAN.items() if not only or k in only]

    credits = {}
    if os.path.exists(CREDITS_JSON):
        with open(CREDITS_JSON, encoding="utf-8") as fh:
            credits = json.load(fh)

    used_titles = set(credits.keys())
    ok_count = fail_count = skip_count = 0
    started_all = time.time()
    stopped = False

    for item_id, plan in sorted(plan_items):
        if stopped:
            break
        keywords, paths, kind = plan["keywords"], plan["paths"], plan["kind"]
        if args.keywords.strip():
            override = [k.strip() for k in args.keywords.split(",") if k.strip()]
            if override:
                keywords = override  # 仅对本次 --only 的对象生效
        if args.covers_only:
            paths = paths[:1]  # 只取封面（门店/酒店第 1 张、轮播唯一一张）
        print(f"\n== {item_id}（{kind}）共 {len(paths)} 张", flush=True)
        for idx, rel_path in enumerate(paths):
            # 时间预算：到点就优雅退出，已下载的文件保留，下次运行自动续跑
            if time.time() - started_all > args.budget:
                stopped = True
                print(f"\n[预算用尽 {args.budget}s] 已停止，可重复运行本命令继续下载剩余图片", flush=True)
                break
            dest = os.path.join(PUBLIC, rel_path.lstrip("/").replace("/", os.sep))
            # 覆盖重下时：旧授权记录要等新图下载成功后再清理，
            # 否则一旦本次下载失败，会出现「文件还在、授权记录已丢」的不一致
            stale_titles = [t for t, v in credits.items() if v["path"] == rel_path]
            if os.path.exists(dest) and not args.force:
                skip_count += 1
                print(f"  [{idx + 1}/{len(paths)}] 已存在，跳过 {rel_path}", flush=True)
                continue
            # 主关键词优先，其余关键词依次兜底；严格候选优先，不足时放宽
            order = [idx % len(keywords)] + [i for i in range(len(keywords)) if i != idx % len(keywords)]
            cands, seen = [], set()
            for ki in order:
                pools = search_candidates(keywords[ki])
                for pool in (pools["strict"], pools["raw"]):
                    for cand in pool:
                        if cand["title"] not in used_titles and cand["title"] not in seen:
                            seen.add(cand["title"])
                            cands.append(cand)
            if not cands:
                fail_count += 1
                print(f"  [{idx + 1}/{len(paths)}] 无可用候选 -> {rel_path}", flush=True)
                continue

            picked, download_fails = None, 0
            for cand in cands:
                started = time.time()
                if download(cand["thumb"], dest):
                    picked = cand
                    print(
                        f"  [{idx + 1}/{len(paths)}] OK {int((time.time() - started) * 1000):>5}ms  "
                        f"{cand['title'][5:52]}  ({cand['license']})",
                        flush=True,
                    )
                    break
                download_fails += 1
                if download_fails >= 3:  # 连续 3 个候选下载失败就不再纠缠，避免整体卡死
                    break

            if picked:
                for stale in stale_titles:  # 新图已成功写入，此时才清理该路径的旧记录
                    credits.pop(stale, None)
                used_titles.add(picked["title"])
                credits[picked["title"]] = {
                    "item": item_id,
                    "path": rel_path,
                    "title": picked["title"],
                    "license": picked["license"],
                    "artist": picked["artist"],
                    "page": picked["page"],
                }
                ok_count += 1
            else:
                fail_count += 1
                print(f"  [{idx + 1}/{len(paths)}] 放弃 -> {rel_path}", flush=True)
            time.sleep(0.2)  # 对图源友好，避免触发限流

    os.makedirs(os.path.dirname(CREDITS_JSON), exist_ok=True)

    # 清理失效记录：授权表里存在、但文件已被删除的条目要一并去掉，避免 CREDITS.md 与磁盘不一致
    dropped = [k for k, v in credits.items()
               if not os.path.exists(os.path.join(PUBLIC, v["path"].lstrip("/").replace("/", os.sep)))]
    for k in dropped:
        credits.pop(k, None)
    if dropped:
        print(f"\n[清理] 移除 {len(dropped)} 条失效授权记录（对应文件已不存在）", flush=True)

    with open(CREDITS_JSON, "w", encoding="utf-8") as fh:
        json.dump(credits, fh, ensure_ascii=False, indent=2)

    write_credits_md(credits)

    print("\n" + "=" * 68)
    total_bytes = sum(
        os.path.getsize(os.path.join(PUBLIC, c["path"].lstrip("/").replace("/", os.sep)))
        for c in credits.values()
        if os.path.exists(os.path.join(PUBLIC, c["path"].lstrip("/").replace("/", os.sep)))
    )
    print(f"下载完成：成功 {ok_count} / 失败 {fail_count} / 跳过 {skip_count}")
    print(f"图片累计体积：{total_bytes / 1024 / 1024:.1f} MB（{len(credits)} 张）")
    print(f"来源说明：frontend/public/images/CREDITS.md")
    return 1 if fail_count else 0


def write_credits_md(credits: dict):
    lines = [
        "# 图片素材来源与授权说明",
        "",
        "本目录下的照片均从 **Wikimedia Commons** 检索下载并本地化存储，用于课程实训演示原型，",
        "遵循各自原始授权协议（下表逐张列出）。演示时读取本地文件，不依赖外网。",
        "",
        "| 用途对象 | 文件 | 原始文件 | 授权 | 作者 | 来源页 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for info in sorted(credits.values(), key=lambda x: x["path"]):
        lines.append(
            f"| {info['item']} | `{info['path']}` | {info['title'].replace('|', '/')} "
            f"| {info['license'].replace('|', '/')} | {info['artist'][:40].replace('|', '/')} | [Commons]({info['page']}) |"
        )
    lines += [
        "",
        "> 说明：若报告的图片使用要求更严格，可只保留本文件与 `credits.json`，或将图片替换为自摄/自制素材；",
        "> 代码中所有图片均带加载失败回退（渐变色块占位），因此删除本目录任何图片都不会导致页面异常。",
        "",
    ]
    with open(CREDITS_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
