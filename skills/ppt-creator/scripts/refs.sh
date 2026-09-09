#!/usr/bin/env bash
#
# Reference collection helper for the ppt-creator skill.
#
# Usage:
#   refs.sh fetch   <dest-dir> <url> [filename]   download one reference into <dest-dir>
#   refs.sh extract <file>                        dump text and figures next to the file
#   refs.sh init    <dest-dir> <slug>             create <dest-dir> and an empty index.org
#
# extract writes to <dir-of-file>/extracted/<basename-without-extension>/ :
#   text.txt    plain text of the document
#   img-*.png   embedded raster figures
#   page-*.png  full-page renders (pdf only), for vector diagrams pdfimages cannot pull

set -euo pipefail

die() { echo "refs.sh: $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || die "missing tool: $1"; }

# Downloads a URL and refuses HTML error pages saved under a document filename.
cmd_fetch() {
  local dest="${1:-}" url="${2:-}" name="${3:-}"
  [ -n "$dest" ] && [ -n "$url" ] || die "fetch <dest-dir> <url> [filename]"
  need curl
  mkdir -p "$dest"
  if [ -z "$name" ]; then
    name="$(basename "${url%%\?*}")"
    case "$name" in *.*) ;; *) name="$name.pdf" ;; esac
  fi
  local out="$dest/$name"
  curl -fL --retry 2 --max-time 120 \
       -A 'Mozilla/5.0 (compatible; ppt-creator/1.0)' \
       -o "$out" "$url"
  local kind
  kind="$(file -b --mime-type "$out")"
  case "$name:$kind" in
    *.pdf:text/html|*.pptx:text/html|*.docx:text/html)
      rm -f "$out"; die "got HTML, not a document: $url" ;;
  esac
  echo "$out  ($kind, $(du -h "$out" | cut -f1))"
}

# Extracts text and raster figures from a pdf, dropping images below 200px.
extract_pdf() {
  local src="$1" out="$2"
  need pdftotext; need pdfimages; need pdftoppm
  pdftotext -layout "$src" "$out/text.txt"
  pdfimages -png -p "$src" "$out/img" || true
  pdftoppm -png -r 110 "$src" "$out/page" || true
  prune_small "$out"
}

# Extracts text and media from an OOXML container (pptx or docx).
extract_ooxml() {
  local src="$1" out="$2" media="$3"
  need unzip
  unzip -o -q -j "$src" "$media/*" -d "$out" 2>/dev/null || true
  local i=0
  for f in "$out"/*; do
    case "$f" in
      "$out"/text.txt|"$out"/img-*) continue ;;
      *.png|*.jpg|*.jpeg|*.gif|*.emf|*.wmf|*.svg)
        i=$((i + 1))
        mv "$f" "$(printf '%s/img-%03d.%s' "$out" "$i" "${f##*.}")" ;;
    esac
  done
  python3 - "$src" "$out/text.txt" <<'PY'
import re, sys, zipfile

src, dest = sys.argv[1], sys.argv[2]
TEXT = re.compile(rb"<a:t>(.*?)</a:t>|<w:t[^>]*>(.*?)</w:t>", re.S)


def slide_key(name):
    """Sorts slideN.xml / documentN.xml numerically instead of lexically."""
    m = re.search(r"(\d+)", name)
    return (int(m.group(1)) if m else 0, name)


chunks = []
with zipfile.ZipFile(src) as z:
    parts = [n for n in z.namelist()
             if re.match(r"(ppt/slides/slide\d+\.xml|word/document\d*\.xml)$", n)]
    for name in sorted(parts, key=slide_key):
        body = z.read(name)
        words = [(a or b).decode("utf-8", "replace") for a, b in TEXT.findall(body)]
        if words:
            chunks.append(f"--- {name} ---\n" + " ".join(words))
with open(dest, "w") as f:
    f.write("\n\n".join(chunks) + "\n")
PY
  prune_small "$out"
}

# Deletes figures smaller than 200px on either side; those are icons and logos.
prune_small() {
  local out="$1"
  command -v python3 >/dev/null || return 0
  python3 - "$out" <<'PY'
import pathlib, struct, sys

d = pathlib.Path(sys.argv[1])


def png_size(path):
    """Returns (width, height) of a PNG, or None when the header is not a PNG."""
    head = path.read_bytes()[:24]
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", head[16:24])


for p in sorted(d.glob("img-*.png")):
    size = png_size(p)
    if size and (size[0] < 200 or size[1] < 200):
        p.unlink()
PY
}

cmd_extract() {
  local src="${1:-}"
  [ -n "$src" ] || die "extract <file>"
  [ -f "$src" ] || die "no such file: $src"
  local base name out
  base="$(cd "$(dirname "$src")" && pwd)"
  name="$(basename "$src")"
  out="$base/extracted/${name%.*}"
  mkdir -p "$out"
  case "${name##*.}" in
    pdf)        extract_pdf "$src" "$out" ;;
    pptx)       extract_ooxml "$src" "$out" "ppt/media" ;;
    docx)       extract_ooxml "$src" "$out" "word/media" ;;
    ppt|doc|odp)
      need soffice
      soffice --headless --convert-to pdf --outdir "$base" "$src" >/dev/null
      extract_pdf "$base/${name%.*}.pdf" "$out" ;;
    *)          die "unsupported format: $name" ;;
  esac
  echo "$out"
  ls -1 "$out" | head -20
}

cmd_init() {
  local dest="${1:-}" slug="${2:-deck}"
  [ -n "$dest" ] || die "init <dest-dir> <slug>"
  mkdir -p "$dest"
  local idx="$dest/index.org"
  [ -f "$idx" ] && { echo "$idx exists"; return 0; }
  cat > "$idx" <<EOF
#+TITLE: $slug 레퍼런스
#+DATE: $(date +%Y-%m-%d)

| 파일 | 출처 | 접근일 | 요지 | 사용 |
|---+---+---+---+---|

* 그림 인벤토리

* 근거
EOF
  echo "$idx"
}

case "${1:-}" in
  fetch)   shift; cmd_fetch "$@" ;;
  extract) shift; cmd_extract "$@" ;;
  init)    shift; cmd_init "$@" ;;
  *)       die "usage: refs.sh {fetch|extract|init} ..." ;;
esac
