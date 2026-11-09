#!/usr/bin/env python3
"""정적 문서 검사: HTML 태그 짝, 상대 링크·#앵커, README 링크.

외부(http/https/mailto) 링크는 검사하지 않는다 — 남의 사이트 상태로 PR 이 깨지지 않게.
저장소 루트에서 실행한다: python3 .github/scripts/check_docs.py
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path.cwd()
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
# 닫는 태그를 생략해도 되는 요소는 짝 검사에서 뺀다.
OPTIONAL_END = {"li", "p", "td", "th", "tr", "thead", "tbody", "tfoot", "dt", "dd", "option", "html", "head", "body"}


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.errors, self.stack = set(), [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        for key in ("href", "src"):
            if a.get(key):
                self.links.append((self.getpos()[0], a[key]))
        if tag not in VOID and tag not in OPTIONAL_END:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag in VOID or tag in OPTIONAL_END:
            return
        if not self.stack or self.stack[-1][0] != tag:
            where = f"(열린 태그: <{self.stack[-1][0]}> {self.stack[-1][1]}줄)" if self.stack else "(열린 태그 없음)"
            self.errors.append(f"{self.getpos()[0]}줄: </{tag}> 짝이 맞지 않음 {where}")
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break
            return
        self.stack.pop()


def parse(path):
    d = Doc()
    d.feed(path.read_text(encoding="utf-8"))
    d.close()
    for tag, line in d.stack:
        d.errors.append(f"{line}줄: <{tag}> 닫히지 않음")
    return d


def target_of(src, link):
    """링크가 가리키는 (파일, 앵커). 외부 링크면 None."""
    parts = urlsplit(link)
    if parts.scheme or link.startswith("//"):
        return None
    path = unquote(parts.path)
    if not path:
        dest = src
    else:
        dest = (ROOT / path.lstrip("/")) if path.startswith("/") else (src.parent / path)
        if path.endswith("/") or dest.is_dir():
            dest = dest / "index.html"
    return dest.resolve(), unquote(parts.fragment)


def main():
    html_files = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts)
    docs = {p.resolve(): parse(p) for p in html_files}
    problems = []

    def check(src, line, link):
        t = target_of(src, link)
        if t is None:
            return
        dest, frag = t
        if not dest.exists():
            problems.append(f"{src.relative_to(ROOT)}:{line}: 없는 파일로 가는 링크 {link}")
        elif frag and dest in docs and frag not in docs[dest].ids:
            problems.append(f"{src.relative_to(ROOT)}:{line}: 없는 앵커 {link}")

    for path, d in docs.items():
        rel = path.relative_to(ROOT)
        problems += [f"{rel}:{e}" for e in d.errors]
        for line, link in d.links:
            check(path, line, link)

    for md in sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts):
        for n, text in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for link in re.findall(r"\]\(([^)\s]+)\)", text):
                check(md.resolve(), n, link)

    print(f"HTML {len(docs)}개 검사")
    for p in problems:
        print("::error::" + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
