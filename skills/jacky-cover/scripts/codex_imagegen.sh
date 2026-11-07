#!/bin/sh
# 用 Codex 内置 image_gen 生成一张图并保存到指定路径。
# 用法：codex_imagegen.sh <输出.png> <提示词文件> <参考图1> [参考图2 ...]
# 参考图按顺序即提示词里的 image 1、image 2……
set -eu
out="$1"; prompt_file="$2"; shift 2
[ -e "$out" ] && { echo "已存在，不覆盖：$out" >&2; exit 1; }
mkdir -p "$(dirname "$out")"
out_abs="$(cd "$(dirname "$out")" && pwd)/$(basename "$out")"

# Rebuild "$@" as -i <absolute path> pairs so paths with spaces stay intact.
n=$#
for f in "$@"; do
  [ -f "$f" ] || { echo "参考图不存在：$f" >&2; exit 1; }
  set -- "$@" -i "$(cd "$(dirname "$f")" && pwd)/$(basename "$f")"
done
shift "$n"

instr="Use your built-in image generation tool exactly ONCE with the prompt below and the attached reference images (attached order = image 1, image 2, ...). Do not rewrite or shorten the prompt. Then copy the generated PNG to: $out_abs
Do nothing else: no edits, no retries, no other files. Reply only with the saved path.

PROMPT:
$(cat "$prompt_file")"

codex exec --skip-git-repo-check -s workspace-write -C "$(dirname "$out_abs")" "$@" -- "$instr" < /dev/null
[ -f "$out_abs" ] || { echo "未生成：$out_abs" >&2; exit 2; }
echo "OK $out_abs"
