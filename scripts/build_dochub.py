#!/usr/bin/env python3
"""
Build the DevOps Mastery dochub — a beautiful static HTML reader for every
Markdown file in the course.

Adapted from the Java 0-to-Hero `build_dochub.py`: one generator script + a
separate CSS/JS asset bundle, producing a self-contained `dochub/` tree that
opens directly in a browser. No node_modules, no build step beyond
`python3 scripts/build_dochub.py`.

Reads (READ-ONLY — never modifies), relative to the content/ root:
    README.md, COURSE_OUTLINE.md, LEARNING_PATHS.md, INTERVIEW_PREP.md,
    PROGRESS.md, AUDIT-*.md
    L*/README.md            (lecture overviews)
    L*/C*/README.md         (chapter overviews)
    L*/C*/T*.md             (topic files)
    scripts/dochub_assets/style.css
    scripts/dochub_assets/app.js

Writes:
    dochub/index.html               (hero + lecture cards + search)
    dochub/{lecture}/index.html     (lecture page — its chapters)
    dochub/{lecture}/{slug}.html    (per-doc reader page)
    dochub/assets/style.css         (copied)
    dochub/assets/app.js            (copied)
    dochub/assets/search-index.json

Top-level nav groups:
    reference  — root MDs (README, COURSE_OUTLINE, …)
    l01 … l30  — the 30 lectures (discovered dynamically from the L## dirs)

Vocabulary mapping vs. the Java reference build:
    nav group  = Lecture (L01–L30)        [Java: Level L0–L6]
    module     = Chapter (C01–C…)         [Java: Chapter C##]
    doc        = Topic   (T01–T…)         [Java: Topic T##]

Optional env:
    DOCHUB_ONLY_COMPLETE=1   Hide topics whose frontmatter status != 'complete'
                             (the DevOps topics carry no frontmatter, so this is
                             a no-op here — kept for parity with the reference.)

Requires:
    pip3 install markdown
"""

from __future__ import annotations
import os
import re
import sys
import json
import html
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

try:
    import markdown as md_lib
    from markdown.extensions.toc import TocExtension
except ImportError:
    sys.stderr.write(
        "ERROR: Python 'markdown' package not installed.\n"
        "Install with:  pip3 install markdown\n"
    )
    sys.exit(1)


# =============================================================================
# Paths
# =============================================================================

SCRIPT_DIR = Path(__file__).resolve().parent  # scripts/
REPO_ROOT = SCRIPT_DIR.parent                 # repo root
ROOT = REPO_ROOT / "content"                  # all course Markdown lives here
OUT_DIR = REPO_ROOT / "dochub"                # generated static site
ASSETS_SRC = SCRIPT_DIR / "dochub_assets"

ONLY_COMPLETE = os.environ.get("DOCHUB_ONLY_COMPLETE") == "1"

EXCLUDE_DIRS = {
    ".git", "node_modules", "build", ".docusaurus", ".cache-loader",
    "dochub", "web", ".idea", ".vscode", "scripts",
}

BRAND = "DevOps Mastery"
BRAND_LOGO = "D"
BRAND_SUB = "Documentation hub"

# Root reference docs, in the order they should appear under the Reference group.
ROOT_FILE_ORDER = [
    "README.md",
    "COURSE_OUTLINE.md",
    "LEARNING_PATHS.md",
    "INTERVIEW_PREP.md",
    "PROGRESS.md",
    "AUDIT-2026-06-15.md",
]

# Per-lecture accent colours (the reserved `indigo` goes to Reference). The
# eight cycle colours repeat across the 30 lectures.
TONE_CYCLE = ["teal", "violet", "pink", "amber", "emerald", "sky", "rose", "lime"]

# Per-lecture icons, by lecture number. Falls back to a cycle for any extras.
LECTURE_ICONS = {
    1: "🚀", 2: "🐧", 3: "🌐", 4: "🐚", 5: "🌿", 6: "💻", 7: "☁️", 8: "📦",
    9: "🌩️", 10: "🏗️", 11: "🔧", 12: "🐳", 13: "☸️", 14: "🕸️", 15: "🔁",
    16: "🛠️", 17: "📊", 18: "🔎", 19: "🧯", 20: "🔒", 21: "🗄️", 22: "📨",
    23: "⚡", 24: "🛰️", 25: "🐒", 26: "💰", 27: "🌍", 28: "🧩", 29: "🎯",
    30: "🏆",
}
_ICON_FALLBACK = ["📘", "📗", "📙", "📕", "📓", "📔"]

NUM_WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
             6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"}


# =============================================================================
# Data models
# =============================================================================

@dataclass
class Doc:
    src: Path
    rel: str                 # path relative to course root
    chapter: str             # nav-group slug (e.g. 'l01', 'reference')
    module: str              # module key (unique per nav group)
    module_label: str
    module_order: List[Any]
    kind: str                # 'overview' | 'page'
    title: str
    out_rel: str             # path relative to OUT_DIR, e.g. 'l01/c01-foo.html'
    raw: str
    frontmatter: Dict[str, Any] = field(default_factory=dict)
    body_html: str = ""

    @property
    def url(self) -> str:
        return self.out_rel


@dataclass
class Module:
    key: str
    label: str
    chapter: str
    order: List[Any]
    docs: List[Doc] = field(default_factory=list)

    @property
    def primary(self) -> Doc:
        for d in self.docs:
            if d.kind == "overview":
                return d
        return self.docs[0]


@dataclass
class Chapter:
    slug: str
    number: int
    title: str
    path_label: str
    subtitle: str
    icon: str
    color: str
    nav_label: str = ""
    modules: List[Module] = field(default_factory=list)
    docs: List[Doc] = field(default_factory=list)


# =============================================================================
# Frontmatter — tolerant flat-YAML parser (DevOps topics carry none; harmless)
# =============================================================================

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_scalar(val: str) -> Any:
    val = val.strip()
    if not val or val.lower() in ("null", "~"):
        return None
    if (val[0] == val[-1]) and val[0] in ("'", '"'):
        return val[1:-1]
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    if re.match(r"^\d{4}-\d{2}-\d{2}$", val):
        return val
    if re.match(r"^-?\d+$", val):
        try:
            return int(val)
        except ValueError:
            return val
    if re.match(r"^-?\d+\.\d+$", val):
        try:
            return float(val)
        except ValueError:
            return val
    return val


def _parse_inline_list(val: str) -> List[Any]:
    inner = val.strip()[1:-1].strip()
    if not inner:
        return []
    out: List[Any] = []
    for raw in inner.split(","):
        x = _parse_scalar(raw)
        if x is None or (isinstance(x, str) and not x.strip()):
            continue
        out.append(x)
    return out


def parse_frontmatter(raw: str) -> Tuple[Dict[str, Any], str]:
    m = _FM_RE.match(raw)
    if not m:
        return {}, raw
    fm_text = m.group(1)
    body = raw[m.end():]
    fm: Dict[str, Any] = {}
    for line in fm_text.split("\n"):
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if not key:
            continue
        if not val:
            fm[key] = ""
            continue
        if val.startswith("[") and val.endswith("]"):
            fm[key] = _parse_inline_list(val)
        else:
            fm[key] = _parse_scalar(val)
    return fm, body


# =============================================================================
# Discovery & classification
# =============================================================================

def slugify(s: str) -> str:
    r = s.lower()
    r = re.sub(r"[^a-z0-9]+", "-", r)
    r = re.sub(r"^-+|-+$", "", r)
    return r or "doc"


# Domain acronyms — humanize() upper-cases these in derived labels.
ACRONYMS = {
    "devops", "sre", "ci", "cd", "cicd", "iac", "k8s", "aws", "gcp", "vpc",
    "iam", "dns", "tcp", "udp", "http", "https", "tls", "ssl", "mtls", "api",
    "rest", "grpc", "sql", "nosql", "acid", "cap", "cdc", "cdn", "ssh", "os",
    "cli", "yaml", "json", "xml", "csv", "jwt", "oidc", "oauth", "saml",
    "rbac", "abac", "slo", "sli", "sla", "mttr", "mtbf", "rpo", "rto", "ha",
    "dr", "finops", "dora", "otel", "apm", "waf", "ddos", "bgp", "nat", "lb",
    "alb", "nlb", "gwlb", "efs", "ebs", "s3", "rds", "sqs", "sns", "ecs",
    "eks", "gke", "aks", "vm", "gc", "jvm", "id", "ip", "ui", "ux", "qps",
    "tco", "scp", "sbom", "slsa", "spiffe", "spire", "pdb", "hpa", "cni",
    "csi", "crd", "gitops", "tdd", "faangm",
}


def humanize(s: str) -> str:
    r = s.replace("_", " ").replace("-", " ").strip()
    out: List[str] = []
    for w in r.split(" "):
        if not w:
            continue
        lw = w.lower()
        if lw in ACRONYMS:
            out.append(w.upper())
        elif lw.endswith("s") and lw[:-1] in ACRONYMS:
            out.append(lw[:-1].upper() + "s")
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)


def filename_label(rel: str) -> str:
    stem = Path(rel).stem
    parent = Path(rel).parent.name
    if stem.upper() == "README" and parent and parent != ".":
        return f"{parent}/{stem}"
    return stem


# Strip a leading "L01" / "L01/C01" / "L01/C01/T01" code prefix from a title.
_CODE_PREFIX_RE = re.compile(
    r"^\s*L\d{2}(?:/C\d{2}(?:/T\d{2})?)?\s*[—–:-]\s*(.+)$"
)


def clean_title(t: str) -> str:
    m = _CODE_PREFIX_RE.match(t)
    return m.group(1).strip() if m else t.strip()


def first_h1(raw: str) -> Optional[str]:
    m = re.search(r"^#\s+(.+?)\s*$", raw, re.MULTILINE)
    if not m:
        return None
    return re.sub(r"`([^`]+)`", r"\1", m.group(1)).strip()


def title_for(rel: str, raw: str, fm: Dict[str, Any]) -> str:
    if isinstance(fm.get("title"), str) and fm["title"].strip():
        return clean_title(fm["title"].strip())
    h1 = first_h1(raw)
    if h1:
        return clean_title(h1)
    if rel == "README.md":
        return "Course README"
    parts = Path(rel).parts
    if len(parts) >= 2 and parts[-1].lower() == "readme.md":
        return humanize(parts[-2])
    return humanize(Path(rel).stem)


def first_paragraph(raw: str, cap: int = 300) -> str:
    """The first real prose paragraph after the H1 — used for lecture subtitles."""
    lines = raw.split("\n")
    started = False
    buf: List[str] = []
    for ln in lines:
        s = ln.strip()
        if not started:
            if s.startswith("#"):
                started = True
            continue
        if not s:
            if buf:
                break
            continue
        if s.startswith(("#", ">", "|", "```", "-", "*", "<")):
            if buf:
                break
            continue
        buf.append(s)
        if len(" ".join(buf)) > cap:
            break
    text = " ".join(buf).strip()
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    if len(text) > cap:
        text = text[: cap - 1].rstrip() + "…"
    return text


def find_md_files() -> List[Path]:
    """Root reference docs, then every .md under the L## lecture dirs."""
    out: List[Path] = []
    for name in ROOT_FILE_ORDER:
        p = ROOT / name
        if p.is_file():
            out.append(p)
    for lec in sorted(ROOT.glob("L[0-9][0-9]")):
        if not lec.is_dir():
            continue
        for p in sorted(lec.rglob("*.md")):
            parts = p.relative_to(ROOT).parts
            if any(part in EXCLUDE_DIRS for part in parts):
                continue
            out.append(p)
    return out


_LECTURE_DIR_RE = re.compile(r"^L(\d{2})$")
_CHAPTER_DIR_RE = re.compile(r"^C(\d{2})$")
_TOPIC_FILE_RE = re.compile(r"^T(\d{2})-")


def discover_chapters() -> "Dict[str, Dict[str, Any]]":
    """Build the nav-group definitions: a Reference group plus one per L## dir,
    reading each lecture README for its title and subtitle."""
    chapters: Dict[str, Dict[str, Any]] = {}
    chapters["reference"] = {
        "slug": "reference", "number": 1, "nav_label": "Ref",
        "title": "Reference", "path_label": "/",
        "subtitle": (
            "The map and the rulebook. The course overview, the master "
            "outline, the role/seniority learning paths, FAANGM interview "
            "guidance, the living progress tracker, and the content audit."
        ),
        "icon": "📚", "color": "indigo",
    }
    n = 2
    for lec in sorted(ROOT.glob("L[0-9][0-9]")):
        if not lec.is_dir():
            continue
        m = _LECTURE_DIR_RE.match(lec.name)
        if not m:
            continue
        num = int(m.group(1))
        slug = f"l{num:02d}"
        readme = lec / "README.md"
        title = f"Lecture {num}"
        subtitle = f"Lecture {num} of the {BRAND} curriculum."
        if readme.is_file():
            rtext = readme.read_text(encoding="utf-8", errors="replace")
            h1 = first_h1(rtext)
            if h1:
                title = clean_title(h1)
            para = first_paragraph(rtext)
            if para:
                subtitle = para
        icon = LECTURE_ICONS.get(num, _ICON_FALLBACK[num % len(_ICON_FALLBACK)])
        color = TONE_CYCLE[(num - 1) % len(TONE_CYCLE)]
        chapters[slug] = {
            "slug": slug, "number": n, "nav_label": lec.name,
            "title": title, "path_label": f"{lec.name}/",
            "subtitle": subtitle, "icon": icon, "color": color,
        }
        n += 1
    return chapters


CHAPTERS: Dict[str, Dict[str, Any]] = {}   # populated in main()


def classify(rel: str) -> Optional[Dict[str, Any]]:
    """Map a course-relative .md path to (chapter, module, kind, out_rel, …)."""
    parts = rel.split("/")

    # 1) Root markdown — Reference group
    if len(parts) == 1:
        fname = parts[0]
        if fname not in ROOT_FILE_ORDER:
            return None
        order = ROOT_FILE_ORDER.index(fname)
        stem = fname[:-3]
        return {
            "chapter": "reference",
            "module": f"reference:{slugify(stem)}",
            "module_label": stem,
            "module_order": [order],
            "kind": "page",
            "out_rel": f"reference/{slugify(stem)}.html",
        }

    # 2) L##/...
    lm = _LECTURE_DIR_RE.match(parts[0])
    if not lm:
        return None
    lec_num = int(lm.group(1))
    chapter_slug = f"l{lec_num:02d}"
    if chapter_slug not in CHAPTERS:
        return None

    # 2a) Lecture README → Overview module
    if len(parts) == 2 and parts[1].lower() == "readme.md":
        return {
            "chapter": chapter_slug,
            "module": f"{chapter_slug}:overview",
            "module_label": "Overview",
            "module_order": [0],
            "kind": "overview",
            "out_rel": f"{chapter_slug}/overview.html",
        }

    if len(parts) != 3:
        return None
    cm = _CHAPTER_DIR_RE.match(parts[1])
    if not cm:
        return None
    chap_num = int(cm.group(1))
    module_key = f"{chapter_slug}:c{chap_num:02d}"
    module_label = f"C{chap_num:02d}"   # refined from the chapter README later

    # 2b) Chapter README → module overview
    if parts[2].lower() == "readme.md":
        return {
            "chapter": chapter_slug,
            "module": module_key,
            "module_label": module_label,
            "module_order": [chap_num],
            "kind": "overview",
            "out_rel": f"{chapter_slug}/c{chap_num:02d}-readme.html",
        }

    # 2c) Topic file
    tm = _TOPIC_FILE_RE.match(parts[2])
    if not tm:
        return None
    topic_stem = parts[2][:-3]
    return {
        "chapter": chapter_slug,
        "module": module_key,
        "module_label": module_label,
        "module_order": [chap_num],
        "kind": "page",
        "out_rel": f"{chapter_slug}/c{chap_num:02d}-{slugify(topic_stem)}.html",
    }


# =============================================================================
# Markdown rendering (verbatim from the reference build)
# =============================================================================

HTML_ELEMENTS = {
    "a","abbr","address","area","article","aside","audio","b","base","bdi",
    "bdo","blockquote","body","br","button","canvas","caption","cite","code",
    "col","colgroup","data","datalist","dd","del","details","dfn","dialog",
    "div","dl","dt","em","embed","fieldset","figcaption","figure","footer",
    "form","h1","h2","h3","h4","h5","h6","head","header","hgroup","hr","html",
    "i","iframe","img","input","ins","kbd","label","legend","li","link","main",
    "map","mark","menu","meta","meter","nav","noscript","object","ol","optgroup",
    "option","output","p","param","picture","pre","progress","q","rb","rp","rt",
    "rtc","ruby","s","samp","script","section","select","slot","small","source",
    "span","strong","style","sub","summary","sup","table","tbody","td","template",
    "textarea","tfoot","th","thead","time","title","tr","track","u","ul","var",
    "video","wbr",
    "svg","path","circle","rect","line","polyline","polygon","g","defs","use",
    "symbol","text","mask","clippath","lineargradient","radialgradient","stop",
    "filter",
}

_PLACEHOLDER_RE = re.compile(r"<([^<>\n]+?)>")
_AUTOLINK_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*://", re.IGNORECASE)
_AUTOLINK_EMAIL = re.compile(r"^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$")
_TAG_NAME_RE = re.compile(r"^([a-zA-Z][a-zA-Z0-9-]*)")
BOOLEAN_ATTRS = {
    "allowfullscreen","async","autofocus","autoplay","checked","controls",
    "default","defer","disabled","formnovalidate","hidden","inert","ismap",
    "itemscope","loop","multiple","muted","nomodule","novalidate","open",
    "playsinline","readonly","required","reversed","selected",
}


def _escape_segment(s: str) -> str:
    def repl(m: re.Match) -> str:
        content = m.group(1)
        if not content:
            return m.group(0)
        if _AUTOLINK_SCHEME.search(content):
            return m.group(0)
        if content.startswith("mailto:") or _AUTOLINK_EMAIL.match(content):
            return m.group(0)
        if content.startswith("!--") or content.startswith("!DOCTYPE"):
            return m.group(0)
        c = content
        if c.startswith("/"):
            c = c[1:]
        c = c.lstrip()
        if c.endswith("/"):
            c = c[:-1].rstrip()
        tag_m = _TAG_NAME_RE.match(c)

        def esc() -> str:
            return "&lt;" + content.replace("&", "&amp;") + "&gt;"
        if not tag_m:
            return esc()
        tag = tag_m.group(1)
        if tag != tag.lower():
            return esc()
        if tag not in HTML_ELEMENTS:
            return esc()
        rest = c[len(tag):].strip()
        if not rest:
            return m.group(0)
        if "=" in rest or '"' in rest or "'" in rest:
            return m.group(0)
        words = rest.split()
        if all(w in BOOLEAN_ATTRS for w in words):
            return m.group(0)
        return esc()
    return _PLACEHOLDER_RE.sub(repl, s)


def escape_placeholder_tags(src: str) -> str:
    out: List[str] = []
    in_fence = False
    fence_marker: Optional[str] = None
    for ln in src.split("\n"):
        t = ln.lstrip()
        if not in_fence and (t.startswith("```") or t.startswith("~~~")):
            in_fence = True
            fence_marker = "```" if t.startswith("```") else "~~~"
            out.append(ln)
            continue
        if in_fence:
            out.append(ln)
            assert fence_marker is not None
            if t.startswith(fence_marker):
                in_fence = False
                fence_marker = None
            continue
        if ln.startswith("    ") or ln.startswith("\t"):
            out.append(ln)
            continue
        buf: List[str] = []
        i = 0
        while i < len(ln):
            c = ln[i]
            if c == "`":
                end = ln.find("`", i + 1)
                if end == -1:
                    buf.append(ln[i:])
                    i = len(ln)
                else:
                    buf.append(ln[i:end + 1])
                    i = end + 1
            else:
                nxt = ln.find("`", i)
                end = len(ln) if nxt == -1 else nxt
                buf.append(_escape_segment(ln[i:end]))
                i = end
        out.append("".join(buf))
    return "\n".join(out)


def make_md_engine() -> md_lib.Markdown:
    return md_lib.Markdown(extensions=[
        "fenced_code",
        "tables",
        "sane_lists",
        "attr_list",
        "def_list",
        "footnotes",
        TocExtension(permalink=False, baselevel=1, toc_depth="2-4"),
    ], output_format="html5")


_ALERT_RE = re.compile(
    r"<blockquote>\s*<p>\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION|INTERVIEW)\]\s*"
    r"(?:<br\s*/?>)?\s*(.*?)</p>(.*?)</blockquote>",
    re.DOTALL | re.IGNORECASE,
)

_ALERT_ICONS = {
    "NOTE": "ⓘ", "TIP": "💡", "WARNING": "⚠", "IMPORTANT": "‼",
    "CAUTION": "⚠", "INTERVIEW": "🎤",
}


def _h_unescape(s: str) -> str:
    return html.unescape(s)


def _h_escape(s: str) -> str:
    return html.escape(s, quote=True)


def post_process_html(body: str) -> str:
    body = re.sub(
        r'<pre(?:\s+class="codehilite")?>\s*<code class="language-mermaid">(.*?)</code>\s*</pre>',
        lambda m: f'<div class="mermaid">{_h_unescape(m.group(1))}</div>',
        body, flags=re.DOTALL,
    )

    def alert_repl(m: re.Match) -> str:
        kind = m.group(1).upper()
        first = m.group(2).strip()
        rest = m.group(3).strip()
        cls = kind.lower()
        body_html = f"<p>{first}</p>{rest}" if rest else f"<p>{first}</p>"
        ic = _ALERT_ICONS.get(kind, "ⓘ")
        kind_label = kind[0] + kind[1:].lower()
        return (
            f'<div class="callout callout-{cls}">'
            f'<div class="callout-head"><span class="callout-ic">{ic}</span>'
            f'<span class="callout-kind">{kind_label}</span></div>'
            f'<div class="callout-body">{body_html}</div>'
            f'</div>'
        )
    body = _ALERT_RE.sub(alert_repl, body)

    def code_lang_repl(m: re.Match) -> str:
        lang = m.group(1)
        inner = m.group(2)
        return (
            f'<div class="code-block">'
            f'<div class="code-head">'
            f'<span class="code-lang">{_h_escape(lang)}</span>'
            f'<button class="code-copy" type="button" title="Copy">Copy</button>'
            f'</div>'
            f'<pre class="codehilite"><code class="language-{_h_escape(lang)}">{inner}</code></pre>'
            f'</div>'
        )
    body = re.sub(
        r'<pre(?:\s+class="codehilite")?>\s*<code class="language-([^"]+)">(.*?)</code>\s*</pre>',
        code_lang_repl, body, flags=re.DOTALL,
    )

    def code_plain_repl(m: re.Match) -> str:
        inner = m.group(1)
        return (
            f'<div class="code-block">'
            f'<div class="code-head">'
            f'<button class="code-copy" type="button" title="Copy">Copy</button>'
            f'</div>'
            f'<pre class="codehilite"><code>{inner}</code></pre>'
            f'</div>'
        )
    body = re.sub(
        r'<pre(?:\s+class="codehilite")?>\s*<code>(.*?)</code>\s*</pre>',
        code_plain_repl, body, flags=re.DOTALL,
    )

    def anchor_repl(m: re.Match) -> str:
        tag = m.group(1)
        attrs = m.group(2)
        inner = m.group(3)
        id_m = re.search(r'\sid="([^"]+)"', attrs)
        if not id_m:
            return m.group(0)
        hid = id_m.group(1)
        return f'<{tag}{attrs}>{inner}<a class="anchor" href="#{hid}" aria-hidden="true">#</a></{tag}>'
    body = re.sub(
        r'<(h[234])((?:\s+[^>]*)?)>(.*?)</\1>',
        anchor_repl, body, flags=re.DOTALL | re.IGNORECASE,
    )

    body = re.sub(r'^\s*<h1(?:\s+[^>]*)?>.*?</h1>\s*', "", body, count=1, flags=re.DOTALL)

    def task_repl(m: re.Match) -> str:
        marker = m.group(1).lower()
        rest = m.group(2)
        checked = " checked" if marker == "x" else ""
        done = " task-done" if marker == "x" else ""
        return (
            f'<li class="task-item{done}">'
            f'<input type="checkbox" disabled{checked} />'
            f'<span>{rest}</span></li>'
        )
    body = re.sub(r'<li>\[([ xX])\]\s*(.*?)</li>', task_repl, body, flags=re.DOTALL)

    body = re.sub(r'(<table[\s>])', r'<div class="table-wrap">\1', body)
    body = body.replace("</table>", "</table></div>")

    return body


def render_markdown(raw: str) -> str:
    escaped = escape_placeholder_tags(raw)
    engine = make_md_engine()
    return engine.convert(escaped)


def rewrite_links(html_text: str, src_file: Path, doc_map: Dict[str, Doc], current: Doc) -> str:
    src_dir = src_file.parent
    cur_dir = (OUT_DIR / current.out_rel).parent

    def repl(m: re.Match) -> str:
        href = m.group(1)
        if href.startswith(("http://", "https://", "mailto:", "#")):
            return m.group(0)
        anchor = ""
        if "#" in href:
            href, _, anchor = href.partition("#")
            anchor = "#" + anchor
        try:
            target_path = (src_dir / href).resolve()
        except (OSError, RuntimeError):
            return m.group(0)
        key = str(target_path)
        target = doc_map.get(key)
        if not target:
            return m.group(0)
        try:
            rel = os.path.relpath(OUT_DIR / target.out_rel, cur_dir).replace(os.sep, "/")
        except ValueError:
            return m.group(0)
        return f'href="{_h_escape(rel + anchor)}"'

    return re.sub(r'href="([^"#][^"]*)"', repl, html_text)


# =============================================================================
# Helpers — search index + lede + TOC rail
# =============================================================================

def compare_orders(a: List[Any], b: List[Any]) -> int:
    def norm(x: Any) -> str:
        if isinstance(x, int):
            return str(x).rjust(12, "0")
        return str(x)
    for i in range(min(len(a), len(b))):
        ca = norm(a[i])
        cb = norm(b[i])
        if ca < cb:
            return -1
        if ca > cb:
            return 1
    return (len(a) > len(b)) - (len(a) < len(b))


def strip_to_text(raw_md: str, max_chars: int = 5000) -> str:
    s = raw_md
    s = re.sub(r"```[\s\S]*?```", " ", s)
    s = re.sub(r"`[^`]+`", " ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"^[#>|=\-+*]+\s*", " ", s, flags=re.MULTILINE)
    s = re.sub(r"[*_~]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > max_chars:
        s = s[:max_chars]
    return s


def extract_lede(raw: str) -> str:
    return first_paragraph(raw, cap=240)


def build_toc_rail(body_html: str) -> str:
    matches = list(re.finditer(
        r'<h([23])(?:[^>]*)\sid="([^"]+)"[^>]*>(.*?)</h\1>',
        body_html, flags=re.DOTALL | re.IGNORECASE,
    ))
    if not matches:
        return ""
    lis: List[str] = []
    for m in matches:
        level = m.group(1)
        anchor = m.group(2)
        text = m.group(3)
        text = re.sub(r'<a class="anchor"[^>]*>.*?</a>', "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", "", text).strip()
        lis.append(
            f'<li class="lvl-{level}"><a href="#{_h_escape(anchor)}" '
            f'data-toc-link>{_h_escape(text)}</a></li>'
        )
    return (
        '<aside class="toc-rail" aria-label="On this page">'
        '<h4>On this page</h4>'
        f'<ul>{"".join(lis)}</ul>'
        '</aside>'
    )


# =============================================================================
# Page templates
# =============================================================================

CHAPTER_LIST: List[Chapter] = []   # populated in main()


def theme_toggle_html() -> str:
    return (
        '<button id="theme-toggle" class="theme-toggle" type="button" '
        'aria-label="Toggle light/dark theme" title="Theme: auto (click to cycle)">'
        '<span class="tt-icon" aria-hidden="true">◐</span>'
        '<span class="tt-label">Auto</span>'
        '</button>'
    )


def nav_html(up: str, current_chapter: Optional[str]) -> str:
    parts: List[str] = []
    for ch in CHAPTER_LIST:
        active = " active" if current_chapter == ch.slug else ""
        parts.append(
            f'<a class="nav-link{active}" href="{up}{ch.slug}/index.html" '
            f'title="{_h_escape(ch.title)}">'
            f'<span class="name">{_h_escape(ch.nav_label)}</span>'
            f'<span class="count">{len(ch.docs)}</span>'
            f'</a>'
        )
    return "".join(parts)


def page_shell(title: str, body: str, *, base_depth: int,
               current_chapter: Optional[str] = None,
               with_progress: bool = False) -> str:
    up = "../" * base_depth
    progress = '<div class="progress-bar"><div class="fill"></div></div>' if with_progress else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{_h_escape(title)} — {BRAND}</title>
<link rel="stylesheet" href="{up}assets/style.css" />
<script>
  try {{
    var t = localStorage.getItem('dochub-theme');
    if (t && t !== 'auto') document.documentElement.dataset.theme = t;
  }} catch (e) {{}}
</script>
</head>
<body>
{progress}
<header class="topnav">
  <div class="topnav-inner">
    <a href="{up}index.html" class="brand">
      <div class="brand-logo">{BRAND_LOGO}</div>
      <div>
        <div class="brand-name">{BRAND}</div>
        <div class="brand-sub">{BRAND_SUB}</div>
      </div>
    </a>
    <nav>{nav_html(up, current_chapter)}</nav>
    <div class="spacer"></div>
    {theme_toggle_html()}
  </div>
</header>
{body}
<footer>
  <div class="container">
    <div>&copy; {BRAND} · Static site generated from the course Markdown</div>
    <div>Read-only mirror of the <code>content/</code> lecture tree</div>
  </div>
</footer>
<script src="{up}assets/app.js"></script>
</body>
</html>
"""


_KIND_ORDER = {"overview": 0, "page": 1}


def _sort_docs(docs: List[Doc]) -> List[Doc]:
    def key(d: Doc) -> Tuple[int, str]:
        return (_KIND_ORDER.get(d.kind, 9), d.rel)
    return sorted(docs, key=key)


def sidebar_html(chapter: Chapter, current: Doc, base_depth: int) -> str:
    up = "../" * base_depth
    parts: List[str] = [
        f'<div class="chapter-pill">'
        f'<span class="ic">{chapter.icon}</span>'
        f'<span>{_h_escape(chapter.nav_label)} · {_h_escape(chapter.title)}</span>'
        f'</div>',
        f'<div class="chapter-path">{_h_escape(chapter.path_label)}</div>',
        '<div class="side-search">'
        '<input id="side-search" type="search" placeholder="Filter this lecture…" />'
        '</div>',
        '<div class="nav-section">',
    ]

    for mod in chapter.modules:
        if len(mod.docs) == 1:
            d = mod.docs[0]
            active = " mod-flat-active" if d is current else ""
            href = up + d.url
            hay = f"{d.title} {d.rel} {mod.label}".lower()
            parts.append(
                f'<a class="mod-flat{active}" href="{_h_escape(href)}" '
                f'data-q="{_h_escape(hay)}">'
                f'<span>{_h_escape(mod.label)}</span></a>'
            )
            continue

        current_in_mod = any(d is current for d in mod.docs)
        attr_open = " open" if current_in_mod else ""
        hay_mod = (mod.label + " " + " ".join(d.rel for d in mod.docs)).lower()
        parts.append(
            f'<details class="mod"{attr_open} data-q="{_h_escape(hay_mod)}">'
            f'<summary><span class="caret">▶</span>'
            f'<span>{_h_escape(mod.label)}</span></summary>'
            f'<ul class="pages">'
        )
        for d in _sort_docs(mod.docs):
            active = " active" if d is current else ""
            href = up + d.url
            hay = f"{d.title} {d.rel}".lower()
            if d.kind == "overview":
                kind_label, kind_cls, pill = "Overview", "overview", "intro"
            else:
                kind_label, kind_cls, pill = d.title, "", ""
            parts.append(
                f'<li data-q="{_h_escape(hay)}">'
                f'<a class="{active.strip()}" href="{_h_escape(href)}">'
                f'<span>{_h_escape(kind_label)}</span>'
                f'<span class="kind-pill {kind_cls}">{_h_escape(pill)}</span>'
                f'</a></li>'
            )
        parts.append("</ul></details>")

    parts.append("</div>")
    return f'<aside class="sidebar">{"".join(parts)}</aside>'


def build_doc_page(doc: Doc, chapter: Chapter) -> str:
    base_depth = len(Path(doc.out_rel).parts) - 1
    up = "../" * base_depth

    flat: List[Doc] = []
    for mod in chapter.modules:
        flat.extend(_sort_docs(mod.docs))
    idx = flat.index(doc) if doc in flat else -1
    prev_doc = flat[idx - 1] if idx > 0 else None
    next_doc = flat[idx + 1] if 0 <= idx < len(flat) - 1 else None

    toc = build_toc_rail(doc.body_html)

    breadcrumb = (
        '<div class="breadcrumb">'
        f'<a href="{up}index.html">Docs hub</a><span class="sep">/</span>'
        f'<a href="{up}{chapter.slug}/index.html">{_h_escape(chapter.nav_label)} · {_h_escape(chapter.title)}</a>'
        f'<span class="sep">/</span><span>{_h_escape(doc.title)}</span>'
        '</div>'
    )

    pager_parts: List[str] = ['<div class="pager">']
    if prev_doc:
        pager_parts.append(
            f'<a class="prev" href="{up}{prev_doc.url}">'
            f'<div class="lbl">← Previous</div>'
            f'<div class="ttl">{_h_escape(filename_label(prev_doc.rel))}</div>'
            f'<div class="sub">{_h_escape(prev_doc.title)}</div></a>'
        )
    else:
        pager_parts.append("<span></span>")
    if next_doc:
        pager_parts.append(
            f'<a class="next" href="{up}{next_doc.url}">'
            f'<div class="lbl">Next →</div>'
            f'<div class="ttl">{_h_escape(filename_label(next_doc.rel))}</div>'
            f'<div class="sub">{_h_escape(next_doc.title)}</div></a>'
        )
    else:
        pager_parts.append("<span></span>")
    pager_parts.append("</div>")
    pager = "".join(pager_parts)

    raw_pane = f'<div class="raw-pane"><pre><code>{_h_escape(doc.raw)}</code></pre></div>'

    body = f"""
<div class="container">
  <div class="layout">
    {sidebar_html(chapter, doc, base_depth)}
    <main>
      <div class="article-head">
        {breadcrumb}
        <h1>{_h_escape(doc.title)}</h1>
        <div><span class="source-path">{_h_escape(doc.rel)}</span></div>
        <div class="view-toggle" role="tablist">
          <button data-view="rendered" class="active">Rendered</button>
          <button data-view="raw">Raw Markdown</button>
        </div>
      </div>
      <article class="markdown">{doc.body_html}</article>
      {raw_pane}
      {pager}
    </main>
    {toc}
  </div>
</div>
"""
    return page_shell(doc.title, body, base_depth=base_depth,
                      current_chapter=chapter.slug, with_progress=True)


def build_category_index(chapter: Chapter) -> str:
    up = "../"

    cards: List[str] = []
    for mod in chapter.modules:
        primary = mod.primary
        lede = _h_escape(extract_lede(primary.raw))
        initial = (mod.label[0] if mod.label else "·").upper()
        chip_parts: List[str] = []
        for d in _sort_docs(mod.docs):
            if d.kind == "overview":
                pill_text, cls = "Overview", "page-chip overview"
            else:
                pill_text, cls = d.title, "page-chip"
            chip_parts.append(
                f'<a class="{cls}" href="{up}{d.url}">{_h_escape(pill_text)}</a>'
            )
        chips = "".join(chip_parts)
        parent_path = str(Path(primary.rel).parent)
        path_display = parent_path if parent_path != "." else primary.rel
        cards.append(f"""
<div class="module-card">
  <div class="top">
    <div class="icon-mod">{_h_escape(initial)}</div>
    <div>
      <a href="{up}{primary.url}" class="module-title">
        <div class="ttl">{_h_escape(mod.label)}</div>
      </a>
      <div class="pth">{_h_escape(path_display)}</div>
    </div>
  </div>
  <div class="lede">{lede}</div>
  <div class="pages-row">{chips}</div>
</div>""")

    grid = "".join(cards)

    body = f"""
<section class="category-hero">
  <div class="container">
    <span class="eyebrow"><span>{chapter.icon}</span>
      <span>{_h_escape(chapter.nav_label)} · {_h_escape(chapter.title)}</span>
    </span>
    <h1>{_h_escape(chapter.title)}
      <span class="path-chip">{_h_escape(chapter.path_label)}</span>
    </h1>
    <p>{_h_escape(chapter.subtitle)}</p>
  </div>
</section>
<section>
  <div class="container">
    <div class="module-grid">{grid}</div>
  </div>
</section>
"""
    return page_shell(f"{chapter.nav_label} · {chapter.title}", body, base_depth=1,
                      current_chapter=chapter.slug)


def build_landing(total_docs: int, total_modules: int, total_lectures: int) -> str:
    cards: List[str] = []
    for ch in CHAPTER_LIST:
        mod_word = "chapter" if len(ch.modules) == 1 else "chapters"
        doc_word = "topic" if len(ch.docs) == 1 else "topics"
        cards.append(f"""
<a class="chapter-card tone-{ch.color}" href="{ch.slug}/index.html">
  <div class="top">
    <div class="icon">{ch.icon}</div>
    <div>
      <div class="num">{_h_escape(ch.nav_label)}</div>
      <h2>{_h_escape(ch.title)}</h2>
      <div class="path-chip">{_h_escape(ch.path_label)}</div>
    </div>
  </div>
  <p>{_h_escape(ch.subtitle)}</p>
  <div class="count">
    <span>{len(ch.modules)} {mod_word} · {len(ch.docs)} {doc_word}</span>
    <span class="arrow">→</span>
  </div>
</a>""")
    cards_html = "".join(cards)

    body = f"""
<section class="hero">
  <div class="hero-inner">
    <span class="hero-eyebrow">Documentation hub</span>
    <h1>Welcome to <span class="grad">{BRAND}</span>.<br/>
        From first commit to staff engineer.</h1>
    <p>
      A storybook tour of the complete DevOps / SRE / Platform Engineering
      curriculum — Linux and networking foundations through Kubernetes, cloud,
      reliability, security, and FAANGM interview prep. {total_lectures} lectures,
      {total_modules} chapters, {total_docs} documents. Start at
      <strong>L01</strong> if it's your first day, or jump to your tier.
    </p>

    <div class="hero-search" id="hero-search">
      <div class="hero-search-box">
        <span class="hero-search-icon">⌕</span>
        <input id="docs-search" type="search" autocomplete="off" spellcheck="false"
               placeholder="Search every doc — try &ldquo;kubernetes&rdquo;, &ldquo;terraform state&rdquo;, &ldquo;SLO&rdquo;&hellip;"
               aria-label="Search documentation" />
        <kbd class="hero-search-kbd">/</kbd>
      </div>
      <div class="hero-search-panel" id="docs-search-panel" hidden>
        <div class="hero-search-status" id="docs-search-status">Loading index…</div>
        <ul class="hero-search-results" id="docs-search-results" role="listbox"></ul>
        <div class="hero-search-foot">
          <span><kbd>↑</kbd><kbd>↓</kbd> navigate</span>
          <span><kbd>↵</kbd> open</span>
          <span><kbd>esc</kbd> close</span>
        </div>
      </div>
    </div>

    <div class="hero-meta">
      <span><span class="dot"></span>{total_docs} documents</span>
      <span><span class="dot" style="background:var(--violet)"></span>{total_modules} chapters</span>
      <span><span class="dot" style="background:var(--pink)"></span>{total_lectures} lectures</span>
    </div>
  </div>
</section>
<section class="chapters">
  <div class="container">
    <div class="chapter-grid">{cards_html}</div>
  </div>
</section>
"""
    return page_shell("Welcome", body, base_depth=0)


def build_search_index(docs: List[Doc]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for d in docs:
        ch = CHAPTERS[d.chapter]
        out.append({
            "t": d.title,
            "l": filename_label(d.rel),
            "p": d.rel,
            "u": d.url,
            "c": f'{ch["nav_label"]} · {ch["title"]}',
            "cs": ch["slug"],
            "ci": ch["icon"],
            "co": ch["color"],
            "k": d.kind,
            "b": strip_to_text(d.raw),
        })
    return out


# =============================================================================
# Main
# =============================================================================

def main() -> int:
    style_src = ASSETS_SRC / "style.css"
    app_src = ASSETS_SRC / "app.js"
    if not style_src.is_file() or not app_src.is_file():
        sys.stderr.write(f"Missing assets — expected:\n  {style_src}\n  {app_src}\n")
        return 1

    # Discover nav groups (Reference + one per L## lecture)
    global CHAPTERS, CHAPTER_LIST
    CHAPTERS = discover_chapters()
    CHAPTER_LIST = [Chapter(
        slug=v["slug"], number=v["number"], title=v["title"],
        path_label=v["path_label"], subtitle=v["subtitle"],
        icon=v["icon"], color=v["color"], nav_label=v["nav_label"],
    ) for v in CHAPTERS.values()]
    chapter_by_slug = {c.slug: c for c in CHAPTER_LIST}

    # Discover & classify markdown
    files = find_md_files()
    docs: List[Doc] = []
    doc_by_src: Dict[str, Doc] = {}
    skipped: List[str] = []
    filtered_count = 0

    for src in files:
        rel = str(src.relative_to(ROOT))
        info = classify(rel)
        if not info:
            skipped.append(rel)
            continue
        raw = src.read_text(encoding="utf-8", errors="replace")
        fm, _ = parse_frontmatter(raw)
        if ONLY_COMPLETE and info["kind"] == "page":
            status = fm.get("status")
            if isinstance(status, str) and status != "complete":
                filtered_count += 1
                continue
        title = title_for(rel, raw, fm)
        doc = Doc(
            src=src, rel=rel,
            chapter=info["chapter"],
            module=info["module"],
            module_label=info["module_label"],
            module_order=list(info["module_order"]),
            kind=info["kind"],
            title=title,
            out_rel=info["out_rel"],
            raw=raw,
            frontmatter=fm,
        )
        docs.append(doc)
        doc_by_src[str(src.resolve())] = doc

    # Group into modules
    modules: Dict[str, Module] = {}
    for d in docs:
        mod = modules.get(d.module)
        if not mod:
            mod = Module(key=d.module, label=d.module_label,
                         chapter=d.chapter, order=list(d.module_order))
            modules[d.module] = mod
        mod.docs.append(d)

    # Refine each chapter module's label from its chapter-README title.
    for mod in modules.values():
        if not mod.key.startswith("l") or ":c" not in mod.key:
            continue
        cnum = mod.key.split(":c")[-1]
        overview = next((d for d in mod.docs if d.kind == "overview"), None)
        if overview and overview.title:
            mod.label = f"C{cnum} · {overview.title}"
        else:
            mod.label = f"C{cnum}"
        for d in mod.docs:
            d.module_label = mod.label

    for mod in modules.values():
        chapter_by_slug[mod.chapter].modules.append(mod)

    import functools
    for ch in CHAPTER_LIST:
        ch.modules.sort(key=functools.cmp_to_key(lambda a, b: compare_orders(a.order, b.order)))
        for m in ch.modules:
            ch.docs.extend(m.docs)

    # Render markdown bodies
    print(f"Rendering {len(docs)} docs…", flush=True)
    for i, d in enumerate(docs, 1):
        html_body = render_markdown(d.raw)
        html_body = rewrite_links(html_body, d.src, doc_by_src, d)
        html_body = post_process_html(html_body)
        d.body_html = html_body
        if i % 50 == 0:
            print(f"  {i}/{len(docs)}", flush=True)

    # Write the output tree
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    (OUT_DIR / "assets").mkdir(parents=True)
    shutil.copy2(style_src, OUT_DIR / "assets" / "style.css")
    shutil.copy2(app_src, OUT_DIR / "assets" / "app.js")

    search_index = build_search_index(docs)
    (OUT_DIR / "assets" / "search-index.json").write_text(
        json.dumps(search_index, ensure_ascii=False), encoding="utf-8"
    )

    for d in docs:
        ch = chapter_by_slug[d.chapter]
        page = build_doc_page(d, ch)
        out_path = OUT_DIR / d.out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page, encoding="utf-8")

    for ch in CHAPTER_LIST:
        page = build_category_index(ch)
        out_path = OUT_DIR / ch.slug / "index.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page, encoding="utf-8")

    total_modules = sum(len(c.modules) for c in CHAPTER_LIST)
    total_lectures = sum(1 for c in CHAPTER_LIST if c.slug != "reference")
    (OUT_DIR / "index.html").write_text(
        build_landing(len(docs), total_modules, total_lectures), encoding="utf-8"
    )

    total_bytes = 0
    for p in OUT_DIR.rglob("*"):
        if p.is_file():
            total_bytes += p.stat().st_size
    print(
        f"\nBuilt dochub/ — {len(docs)} docs, {total_modules} chapters "
        f"across {len(CHAPTER_LIST)} nav groups ({total_bytes // 1024} KB total)"
    )
    for ch in CHAPTER_LIST:
        print(
            f"  · {ch.slug.ljust(10)} {str(len(ch.modules)).rjust(3)} chapters "
            f"/ {str(len(ch.docs)).rjust(3)} docs"
        )
    if filtered_count:
        print(f"Filtered {filtered_count} non-complete topics (DOCHUB_ONLY_COMPLETE=1)")
    if skipped:
        preview = ", ".join(skipped[:8])
        more = " …" if len(skipped) > 8 else ""
        print(f"Skipped {len(skipped)} file(s): {preview}{more}")
    print("\nOpen: dochub/index.html")
    print("Or serve:  python3 -m http.server -d dochub 8000")
    return 0


if __name__ == "__main__":
    sys.exit(main())
