#!/usr/bin/env python3
"""Generate the per-agent instruction files from the canonical SKILL.md.

Usage: python scripts/build.py

SKILL.md is the only file to edit by hand. Everything under agents/ and
tools/validate_flex.py is regenerated from it.
"""
import os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_NAME = 'miva-page-builder-flex-component-generator'
SKILL = os.path.join(ROOT, 'skills', SKILL_NAME, 'SKILL.md')
AGENTS = os.path.join(ROOT, 'agents')
RULE = 'miva-flex-components'
GLOBS = ['**/flex.json', '**/*.mvt']
WINDSURF_LIMIT = 12000  # Windsurf rejects rule files above 12,000 characters

# Wording that only makes sense inside Claude, swapped for agent-neutral text.
NEUTRAL = [
    ('Save this validator to the scratchpad (not inside the component folder)',
     'Save this validator to a temporary folder outside the component folder'),
    ("using the session's file-delivery mechanism (an outputs folder or file-send tool); if the user has a folder connected, save them there.",
     'in the workspace, or in the folder the user named.'),
    ('Use the **Miva Docs MCP server** first.',
     'Use the **Miva Docs MCP server** first when it is configured for this agent; otherwise go straight to the GitHub repos below.'),
    ('let Claude pick', 'let the assistant pick'),
]


def read_skill():
    text = open(SKILL, encoding='utf-8').read()
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    meta = dict(re.findall(r'^(\w+): (.*)$', m.group(1), re.M))
    return meta, text[m.end():].lstrip('\n')


def neutral(body):
    for old, new in NEUTRAL:
        if old not in body:
            raise SystemExit(f'build.py: expected text not found in SKILL.md: {old[:60]}...')
        body = body.replace(old, new)
    return body


def sections(body):
    """Split on top-level '## ' headings, ignoring anything inside code fences."""
    parts, cur, fenced = [], [], False
    for line in body.splitlines(keepends=True):
        if line.startswith('```'):
            fenced = not fenced
        if not fenced and line.startswith('## ') and cur:
            parts.append(''.join(cur))
            cur = []
        cur.append(line)
    parts.append(''.join(cur))
    return [p.replace('\n---\n', '\n').strip() + '\n' for p in parts]


def chunk(parts, limit):
    chunks, cur = [], ''
    for p in parts:
        if cur and len(cur) + len(p) + 1 > limit:
            chunks.append(cur)
            cur = ''
        if len(p) > limit:
            raise SystemExit(f'build.py: section over {limit} chars: {p.splitlines()[0]}')
        cur += ('\n' if cur else '') + p
    return chunks + [cur]


def write(rel, content):
    path = os.path.join(AGENTS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(content)
    print(f'  agents/{rel.replace(os.sep, "/")} ({len(content):,} chars)')


def main():
    meta, body = read_skill()
    desc = meta['description']
    generic = neutral(body)
    shutil.rmtree(AGENTS, ignore_errors=True)

    # Validator as a standalone script
    validator = re.search(r'```python\n(.*?)```', body, re.S).group(1)
    with open(os.path.join(ROOT, 'tools', 'validate_flex.py'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(validator)
    print('  tools/validate_flex.py')

    # Agents that read the Agent Skills format (SKILL.md in a named folder)
    for rel in ('codex/.agents/skills', 'github-copilot/.github/skills'):
        write(os.path.join(rel, SKILL_NAME, 'SKILL.md'), f'---\nname: {SKILL_NAME}\ndescription: {desc}\n---\n\n{generic}')

    # Cursor project rule, attached on matching files or when the agent judges it relevant
    write(f'cursor/.cursor/rules/{RULE}.mdc',
          f'---\ndescription: {desc}\nglobs: {",".join(GLOBS)}\nalwaysApply: false\n---\n\n{generic}')

    # GitHub Copilot: path-scoped instructions plus a /miva-flex-component prompt
    write(f'github-copilot/.github/instructions/{RULE}.instructions.md',
          f'---\napplyTo: "{",".join(GLOBS)}"\ndescription: {desc}\n---\n\n{generic}')
    write('github-copilot/.github/prompts/miva-flex-component.prompt.md',
          '---\nagent: agent\ndescription: Build, fork, update or debug a Miva Page Builder flex component\n---\n\n'
          f'Follow these instructions for the request: ${{input:request:Describe the component}}\n\n{generic}')

    # Single-file instruction formats
    write('codex/AGENTS.md', generic)
    write('gemini-cli/GEMINI.md', generic)
    write(f'cline/.clinerules/{RULE}.md', generic)
    write(f'generic/{RULE}.md', generic)

    # Windsurf: model-decided rules, split at section boundaries to stay under the size limit
    header = f'---\ntrigger: model_decision\ndescription: {desc}\n---\n\n'
    parts = chunk(sections(generic), WINDSURF_LIMIT - len(header) - 200)
    for i, part in enumerate(parts, 1):
        note = f'> Part {i} of {len(parts)} of the Miva flex component rules.\n\n' if len(parts) > 1 else ''
        write(f'windsurf/.windsurf/rules/{RULE}-{i}.md', header + note + part)


if __name__ == '__main__':
    main()
