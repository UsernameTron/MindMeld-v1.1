#!/usr/bin/env python3
import os
import json
import argparse
import fnmatch

def is_ignored(path, ignore_patterns):
    for pat in ignore_patterns:
        # match full names or fnmatch patterns
        if path == pat or fnmatch.fnmatch(path, pat) or path.startswith(pat + os.sep):
            return True
    return False

def detect_language(ext):
    mapping = {
        '.py':'Python', '.js':'JavaScript', '.ts':'TypeScript',
        '.tsx':'TSX', '.jsx':'JSX', '.java':'Java', '.cs':'C#',
        '.md':'Markdown', '.json':'JSON', '.yml':'YAML', '.yaml':'YAML',
        '.sh':'Shell', '.ps1':'PowerShell'
    }
    return mapping.get(ext.lower(),'Other')

def analyze_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        count_defs = sum(1 for l in lines if l.strip().startswith(('def ','class ','function ')))
        return len(lines), count_defs
    except:
        return None, None

def walk_directory(root, ignore):
    files = []
    summary = {'total_files': 0, 'total_lines': 0, 'languages': {}}

    for dirpath, dirnames, filenames in os.walk(root):
        # prune ignored dirs early
        dirnames[:] = [d for d in dirnames if not is_ignored(os.path.relpath(os.path.join(dirpath, d), root), ignore)]

        for fn in filenames:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, root)

            if is_ignored(rel, ignore):
                continue

            ext = os.path.splitext(fn)[1]
            lang = detect_language(ext)
            lines, defs = analyze_file(full)

            files.append({
                'path': rel,
                'language': lang,
                'lines': lines,
                'definitions': defs
            })

            summary['total_files'] += 1
            if lines:
                summary['total_lines'] += lines
            summary['languages'].setdefault(lang, 0)
            summary['languages'][lang] += 1

    return {'files': files, 'summary': summary}

def main():
    parser = argparse.ArgumentParser(description='Generate a JSON outline of the codebase.')
    parser.add_argument('-r','--root', default='.', help='Root directory to scan')
    parser.add_argument('-i','--ignore', nargs='*',
                        default=['.git','node_modules','run','logs','output'],
                        help='Paths or patterns to ignore')
    parser.add_argument('-o','--output', default='codebase_outline.json',
                        help='Path to write the JSON report')
    args = parser.parse_args()

    report = walk_directory(args.root, args.ignore)
    with open(args.output, 'w', encoding='utf-8') as out:
        json.dump(report, out, indent=2)
    print(f'Codebase outline written to {args.output}')

if __name__ == '__main__':
    main()
