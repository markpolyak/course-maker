#!/usr/bin/env python3

import sys
from pathlib import Path
import unicodedata


def contains_non_english_letters(text: str) -> bool:
    """
    Возвращает True, если строка содержит буквы,
    не относящиеся к латинскому алфавиту.
    """

    for ch in text:
        # Нас интересуют только буквы
        if not unicodedata.category(ch).startswith("L"):
            continue

        name = unicodedata.name(ch, "")

        # Латинские буквы пропускаем
        if "LATIN" in name:
            continue

        # Любая другая буква считается неанглийской
        return True

    return False


def scan_markdown_files(root_dir: str):
    root = Path(root_dir)

    for md_file in root.rglob("*.md"):
        try:
            with md_file.open("r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    if contains_non_english_letters(line):
                        print(f"{md_file}:{line_num}: {line.rstrip()}")

        except Exception as e:
            print(f"ERROR reading {md_file}: {e}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <directory>")
        sys.exit(1)

    scan_markdown_files(sys.argv[1])
