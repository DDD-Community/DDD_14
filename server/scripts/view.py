#!/usr/bin/env python3
"""승인을 받기 전에 문서를 브라우저로 열어 사용자가 직접 눈으로 확인하게 한다.

사용: python3 scripts/view.py [문서...] [--base <ref>] [--no-open]
  문서를 주지 않으면 이 브랜치에서 바뀐 마크다운 문서를 연다(base와 비교한 변경, 작업 트리, 새 파일).

문서마다 탭이 셋이다. 원문(렌더링), 소스(마크다운 그대로), 변경(base와의 diff).
파일의 글자를 요약하거나 고치지 않는다. 화면에 파일 경로, 커밋, 파일의 SHA-256을 찍어 나중에 대조할 수 있다.
결과는 _workspace/view-<해시>.html이다. 해시는 보여 주는 내용에서 나오므로 같은 내용은 같은 파일이고
다른 내용은 다른 파일이라서 병렬 세션이 서로 덮어쓰지 않는다. 하루가 지난 view-*.html은 실행할 때 지운다.
외부 주소를 부르지 않는다. 문서를 고치지 않고 승인을 대신하지 않는다.
"""
import hashlib
import html
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "_workspace"
MAX_AGE_SECONDS = 24 * 60 * 60


def git(*args, ok=(0,)):
    """git을 실행하고 출력을 돌려준다. 종료 코드가 ok에 없으면 빈 문자열이다."""
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=20)
    return r.stdout if r.returncode in ok else ""


# ---------- 마크다운 -> HTML (표준 라이브러리만, 입력은 먼저 이스케이프한다) ----------

def split_row(line):
    """표의 한 줄을 칸으로 나눈다. 백틱 안의 |는 나누지 않는다."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cur, in_code = [], [], False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code:
            cells.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def is_separator(line):
    s = line.strip()
    return bool(s) and s.startswith("|") and re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?", s) is not None


def inline(text):
    codes = []

    def keep(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}" rel="noreferrer">{m.group(1)}</a>',
        text,
    )
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")


def render_markdown(src):
    lines = src.split("\n")
    out = []
    i = 0
    n = len(lines)
    para = []

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(p.strip() for p in para)) + "</p>")
            para.clear()

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_para()
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(code)) + "</code></pre>")
            continue

        if not stripped:
            flush_para()
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_para()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            flush_para()
            out.append("<hr>")
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < n and is_separator(lines[i + 1]):
            flush_para()
            head = split_row(line)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            t = ["<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"]
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        if stripped.startswith(">"):
            flush_para()
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + inline(" ".join(quote)) + "</blockquote>")
            continue

        m = LIST_RE.match(line)
        if m:
            flush_para()
            items = []  # (indent, ordered, text)
            while i < n:
                lm = LIST_RE.match(lines[i])
                if lm:
                    items.append([len(lm.group(1).replace("\t", "    ")), lm.group(2)[0].isdigit(), lm.group(3)])
                    i += 1
                elif lines[i].strip() and lines[i].startswith((" ", "\t")) and items:
                    items[-1][2] += " " + lines[i].strip()
                    i += 1
                else:
                    break
            out.append(render_list(items))
            continue

        para.append(line)
        i += 1

    flush_para()
    return "\n".join(out)


def render_list(items):
    html_parts = []
    stack = []  # (indent, tag)
    for indent, ordered, text in items:
        tag = "ol" if ordered else "ul"
        while stack and indent < stack[-1][0]:
            html_parts.append(f"</li></{stack.pop()[1]}>")
        if not stack or indent > stack[-1][0]:
            stack.append((indent, tag))
            html_parts.append(f"<{tag}><li>")
        else:
            html_parts.append("</li><li>")
        html_parts.append(inline(text))
    while stack:
        html_parts.append(f"</li></{stack.pop()[1]}>")
    return "".join(html_parts)


# ---------- 변경(diff) ----------

def merge_base(base):
    if base:
        if not git("rev-parse", "--verify", "-q", base).strip():
            raise SystemExit(f"view: base를 찾지 못했다: {base}")
        return base
    for ref in ("develop", "origin/develop"):
        mb = git("merge-base", "HEAD", ref).strip()
        if mb:
            return mb
    return "HEAD"


def diff_for(rel, base_ref):
    tracked = git("ls-files", "--error-unmatch", rel).strip()
    if tracked:
        text = git("diff", "-U3", base_ref, "--", rel)
    else:
        # --no-index는 차이가 있으면 종료 코드 1이다
        text = git("diff", "-U3", "--no-index", "--", "/dev/null", rel, ok=(0, 1))
    return text


def render_diff(text):
    if not text.strip():
        return '<p class="muted">base와 달라진 곳이 없다.</p>'
    rows = []
    for line in text.split("\n"):
        cls = ""
        if line.startswith("+++") or line.startswith("---") or line.startswith("diff ") or line.startswith("index "):
            cls = "meta"
        elif line.startswith("@@"):
            cls = "hunk"
        elif line.startswith("+"):
            cls = "add"
        elif line.startswith("-"):
            cls = "del"
        rows.append(f'<div class="ln {cls}">{html.escape(line) or "&nbsp;"}</div>')
    return '<div class="diff">' + "".join(rows) + "</div>"


# ---------- 문서 모으기와 페이지 ----------

def default_files(base_ref):
    names = set()
    for cmd in (["diff", "--name-only", base_ref], ["ls-files", "--others", "--exclude-standard"]):
        for line in git(*cmd).split("\n"):
            line = line.strip()
            if line.endswith(".md"):
                names.add(line)
    return sorted(names)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_page(files, base_ref):
    head = git("rev-parse", "--short", "HEAD").strip() or "(커밋 없음)"
    branch = git("branch", "--show-current").strip() or "(분리된 HEAD)"
    dirty = bool(git("status", "--porcelain", "--untracked-files=no").strip())
    entries = []
    seed = hashlib.sha256()
    for rel in files:
        path = ROOT / rel
        if not path.is_file():
            print(f"view: 파일이 없다: {rel}", file=sys.stderr)
            continue
        data = path.read_bytes()
        text = data.decode("utf-8")
        diff = diff_for(rel, base_ref)
        seed.update(rel.encode() + b"\0" + data + b"\0" + diff.encode())
        entries.append((rel, text, sha256(data), diff))
    if not entries:
        return None, None
    tabs, panels = [], []
    for idx, (rel, text, digest, diff) in enumerate(entries):
        did = f"d{idx}"
        tabs.append(f'<a href="#{did}" class="doc-link">{html.escape(rel)}</a>')
        panels.append(
            f'<section id="{did}" class="doc">'
            f'<h2 class="path">{html.escape(rel)}</h2>'
            f'<p class="meta">파일의 SHA-256 <code>{digest}</code></p>'
            f'<div class="tabbar">'
            f'<input type="radio" name="t{idx}" id="t{idx}a" checked><label for="t{idx}a">원문</label>'
            f'<input type="radio" name="t{idx}" id="t{idx}b"><label for="t{idx}b">소스</label>'
            f'<input type="radio" name="t{idx}" id="t{idx}c"><label for="t{idx}c">변경</label>'
            f'<div class="pane pa"><article>{render_markdown(text)}</article></div>'
            f'<div class="pane pb"><pre class="src">{html.escape(text)}</pre></div>'
            f'<div class="pane pc">{render_diff(diff)}</div>'
            f'</div></section>'
        )
    page = PAGE.format(
        branch=html.escape(branch),
        head=html.escape(head),
        dirty="작업 트리에 커밋하지 않은 변경이 있다" if dirty else "작업 트리가 깨끗하다",
        base=html.escape(base_ref[:12]),
        toc="".join(tabs),
        panels="".join(panels),
    )
    return page, seed.hexdigest()[:8]


PAGE = """<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><title>문서 확인</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{ --bg:#fff; --fg:#1f2328; --muted:#656d76; --line:#d0d7de; --code:#f6f8fa; --add:#e6ffec; --del:#ffebe9; --hunk:#ddf4ff; --accent:#0969da; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg:#0d1117; --fg:#e6edf3; --muted:#8b949e; --line:#30363d; --code:#161b22; --add:#12261e; --del:#2d1417; --hunk:#0c2d4a; --accent:#58a6ff; }} }}
body {{ margin:0; font:16px/1.65 -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif; background:var(--bg); color:var(--fg); }}
header {{ position:sticky; top:0; background:var(--bg); border-bottom:1px solid var(--line); padding:10px 24px; z-index:2; }}
header .info {{ color:var(--muted); font-size:13px; }}
nav {{ margin-top:6px; display:flex; flex-wrap:wrap; gap:8px; }}
.doc-link {{ font-size:13px; padding:2px 8px; border:1px solid var(--line); border-radius:12px; text-decoration:none; color:var(--accent); }}
main {{ max-width:1000px; margin:0 auto; padding:16px 24px 80px; }}
.doc {{ margin-top:28px; }}
.path {{ font-size:15px; font-family:ui-monospace, Menlo, monospace; border-bottom:1px solid var(--line); padding-bottom:6px; }}
.meta {{ color:var(--muted); font-size:12px; margin:4px 0 10px; word-break:break-all; }}
.tabbar input {{ position:absolute; opacity:0; }}
.tabbar label {{ display:inline-block; padding:4px 14px; border:1px solid var(--line); border-bottom:none; border-radius:6px 6px 0 0; cursor:pointer; color:var(--muted); font-size:14px; }}
.tabbar input:checked + label {{ color:var(--fg); background:var(--code); font-weight:600; }}
.pane {{ display:none; border:1px solid var(--line); padding:8px 20px 20px; }}
.tabbar input:nth-of-type(1):checked ~ .pa, .tabbar input:nth-of-type(2):checked ~ .pb, .tabbar input:nth-of-type(3):checked ~ .pc {{ display:block; }}
article h1 {{ font-size:1.7em; border-bottom:1px solid var(--line); padding-bottom:.3em; }}
article h2 {{ font-size:1.35em; border-bottom:1px solid var(--line); padding-bottom:.25em; margin-top:1.6em; }}
article h3 {{ font-size:1.12em; margin-top:1.4em; }}
table {{ border-collapse:collapse; margin:12px 0; display:block; overflow-x:auto; }}
th, td {{ border:1px solid var(--line); padding:6px 12px; text-align:left; vertical-align:top; }}
th {{ background:var(--code); }}
code {{ background:var(--code); border-radius:4px; padding:1px 5px; font:13px ui-monospace, Menlo, monospace; }}
pre {{ background:var(--code); padding:12px; border-radius:6px; overflow-x:auto; }}
pre.src {{ white-space:pre-wrap; word-break:break-word; font:13px/1.5 ui-monospace, Menlo, monospace; }}
pre code {{ background:none; padding:0; }}
blockquote {{ margin:8px 0; padding:0 14px; border-left:4px solid var(--line); color:var(--muted); }}
.diff {{ font:13px/1.5 ui-monospace, Menlo, monospace; white-space:pre-wrap; word-break:break-word; }}
.ln.add {{ background:var(--add); }} .ln.del {{ background:var(--del); }} .ln.hunk {{ background:var(--hunk); }} .ln.meta {{ color:var(--muted); }}
.muted {{ color:var(--muted); }}
footer {{ color:var(--muted); font-size:12px; margin-top:40px; }}
</style></head><body>
<header><div><strong>승인 전 문서 확인</strong></div>
<div class="info">브랜치 <code>{branch}</code> · 커밋 <code>{head}</code> · {dirty} · 변경 보기의 기준(base) <code>{base}</code></div>
<nav>{toc}</nav></header>
<main>{panels}
<footer>이 화면은 파일을 그대로 렌더링한 것이다. 렌더러가 단순해서 어긋나 보이면 소스 탭이 파일의 글자 그대로다. 이 화면을 본 것은 승인이 아니다. 승인은 대화에서 사용자가 한다.</footer>
</main></body></html>
"""


def clean_old():
    now = time.time()
    if not OUT_DIR.is_dir():
        return
    for f in OUT_DIR.glob("view-*.html"):
        try:
            if now - f.stat().st_mtime > MAX_AGE_SECONDS:
                f.unlink()
        except OSError:
            pass


def main(argv):
    base = None
    open_it = True
    files = []
    it = iter(argv)
    for a in it:
        if a == "--no-open":
            open_it = False
        elif a == "--base":
            base = next(it, None)
        else:
            files.append(a)
    base_ref = merge_base(base)
    if not files:
        files = default_files(base_ref)
    files = [str(Path(f).resolve().relative_to(ROOT)) if Path(f).is_absolute() else f for f in files]
    page, key = build_page(files, base_ref)
    if page is None:
        print("view: 열 문서가 없다")
        return 1
    OUT_DIR.mkdir(exist_ok=True)
    clean_old()
    out = OUT_DIR / f"view-{key}.html"
    out.write_text(page, encoding="utf-8")
    print(f"view: {out}")
    if open_it:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        try:
            subprocess.run([opener, str(out)], timeout=10)
        except Exception as e:
            print(f"view: 브라우저를 열지 못했다({e}). 위 경로를 직접 연다", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
