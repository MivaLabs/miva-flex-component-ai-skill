# Miva Flex Component AI Skill

Instructions that teach AI coding assistants how to build, fork, update and debug Miva Merchant Page Builder flex components. With them loaded, an assistant can produce a `{code}.tar.bz2` package (flex.json, init.mvt, instance.mvt, upgrade.mvt, JS, CSS) that imports through **Miva Admin > User Interface > Flex Components > Upload Component** and renders in Page Builder.

The instructions cover:

- choosing between the Basic, Web Component and MMX (`MMX_Element`) architectures
- flex.json fields, every property type, lists, textsettings, visibility conditions and defaults
- init.mvt, instance.mvt and upgrade.mvt patterns used by the Shadows framework
- mmx-base 26.02 features (`makeComponent()`, lifecycle states, adoptable styles, delegated events, cached JSON API calls)
- loading store data through the Runtime JSON API, including custom fields
- the official process for forking an `mmx-*` component
- a validator script, packaging steps and a troubleshooting table

Baseline: **Shadows 26.02.00**.

## Supported assistants

| Assistant | File(s) | Where to put them |
|---|---|---|
| Claude (Claude Code, claude.ai) | `skills/miva-page-builder-flex-component-generator/SKILL.md` | Claude Code: `~/.claude/skills/` or `.claude/skills/` in a project. claude.ai: zip the folder and upload it under Settings > Capabilities > Skills. |
| OpenAI Codex | `agents/codex/AGENTS.md` or `agents/codex/.agents/skills/...` | Copy `AGENTS.md` to the project root (merge it into an existing one), or copy the skill folder into the project's `.agents/skills/`. |
| GitHub Copilot | `agents/github-copilot/.github/` | Copy into the project's `.github/` folder. Includes a skill, path-scoped instructions for `flex.json` and `.mvt` files, and a `/miva-flex-component` prompt for Copilot Chat. |
| Cursor | `agents/cursor/.cursor/rules/miva-flex-components.mdc` | Copy into the project's `.cursor/rules/`. Attaches when `flex.json` or `.mvt` files are in context, and the agent can pull it in when a request matches the description. |
| Windsurf | `agents/windsurf/.windsurf/rules/` | Copy the four files into the project's `.windsurf/rules/`. They are split because Windsurf limits each rule file to 12,000 characters. |
| Gemini CLI | `agents/gemini-cli/GEMINI.md` | Copy to the project root, or to `~/.gemini/GEMINI.md` for all projects. |
| Cline | `agents/cline/.clinerules/miva-flex-components.md` | Copy into the project's `.clinerules/` folder. |
| Anything else | `agents/generic/miva-flex-components.md` | Paste it into the assistant's system prompt or project instructions, or attach it as a knowledge file. |

Each assistant's folder mirrors the paths it expects, so you can copy the contents of `agents/<assistant>/` straight into a project root.

## Recommended: Miva Docs MCP server

The instructions tell the assistant to look things up rather than rely on its own memory of the framework. If your assistant supports MCP and you have access to the Miva Docs MCP server, connect it. It returns current Shadows component source, flex.json documentation and JSON API function references.

Without it, the assistant falls back to the public repos:

- https://github.com/mivaecommerce/shadows
- https://github.com/mivaecommerce/flex-components

## Validator

`tools/validate_flex.py` checks a component folder for the problems that most often break an import: missing files, `managed: true`, leftover `integrity` hashes, resource codes that don't match init.mvt, `depends` written as an array, list prompts missing `:value`, forks that still define an `mmx-*` tag, and more.

```bash
python tools/validate_flex.py path/to/acme-feature-grid
```

Add `--managed` only when checking an unmodified Miva component.

## Repository layout

```
skills/miva-page-builder-flex-component-generator/SKILL.md   source of truth
scripts/build.py                                             generates agents/ and tools/
agents/<assistant>/...                                       generated per-assistant files
tools/validate_flex.py                                       generated validator
```

## Making changes

Edit only `skills/miva-page-builder-flex-component-generator/SKILL.md`, then regenerate everything else:

```bash
python scripts/build.py
```

The build swaps a few Claude-specific phrases for neutral wording, writes each assistant's file with the frontmatter it expects, splits the Windsurf rules, and extracts the validator from the skill. Commit the regenerated files together with the SKILL.md change.

When a new Shadows release ships, update the baseline version in SKILL.md, check the mmx-base changes against section 6, and rebuild.
