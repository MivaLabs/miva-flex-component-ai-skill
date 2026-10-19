# Miva flex component AI skill

This repo gives your AI assistant the instructions it needs to build custom blocks for Miva Page Builder.

In Miva, these blocks are called flex components. A flex component is anything you can drop onto a page in Page Builder: a banner, an FAQ list, a row of featured products, a comparison table. Miva ships a set of them with the Shadows theme. With this skill installed, you can describe a new one in plain words and the assistant builds it for you as a file you upload to your store.

You can also use it to:

- copy one of Miva's built-in components and change how it looks or works
- add a setting or field to a component you already have
- figure out why a component won't upload or won't show up on the page

## What you need

- A Miva store that uses Page Builder. The skill targets the Shadows theme, version 26.02 or newer. Older versions mostly work, and the assistant will ask.
- Admin access to your store, so you can upload the finished component.
- An account with an AI assistant. Claude has the simplest setup. ChatGPT and the coding tools listed below work too.

## Before you start

Try new components on a development or staging store first. If you don't have one, ask your Miva account contact or your developer.

AI assistants make mistakes. Before a component goes on your live store, check it in Page Builder on desktop and mobile. If it loads data or handles anything about orders or customers, have a developer review it.

## Install

Pick the assistant you use. You only need one of these.

### Claude on the web (claude.ai)

This is the easiest option. Skills need a paid Claude plan. On a Team or Enterprise plan, your admin may need to turn skills on first.

1. Download the skill file: open [downloads/miva-page-builder-flex-component-generator.zip](downloads/miva-page-builder-flex-component-generator.zip) and click the download button (the downward arrow near the top right of the page). Don't unzip it.
2. Go to [claude.ai](https://claude.ai) and sign in.
3. Click your name in the bottom left corner, then click **Settings**.
4. Open **Capabilities**. If "Code execution and file creation" is off, turn it on. Claude needs it to create the component file.
5. Find the **Skills** section and click **Upload skill**.
6. Choose the zip file you downloaded.
7. Make sure the new skill's switch is on.

That's it. Start a new chat and ask for a component. Claude loads the skill on its own when your request is about Miva flex components or Page Builder.

### ChatGPT

1. Download the instructions file: open [agents/generic/miva-flex-components.md](agents/generic/miva-flex-components.md) and click the download button near the top right.
2. In ChatGPT, create a new project (look for **New project** in the left sidebar). Name it something like "Miva components".
3. Add the file you downloaded to the project's files.
4. Open the project's instructions and paste this:

   ```
   For every request in this project, follow the attached file miva-flex-components.md.
   ```

5. Start chats inside that project when you want to build a component.

The same approach works with most other chat assistants: create a project or workspace, attach `miva-flex-components.md`, and tell the assistant to follow it.

### Claude Code

1. Download the zip file the same way as in step 1 of the claude.ai instructions.
2. Unzip it. You get a folder named `miva-page-builder-flex-component-generator`.
3. Move that folder into your Claude skills folder:
   - Windows: `C:\Users\YOUR-NAME\.claude\skills\`
   - Mac or Linux: `~/.claude/skills/`

   Create the `skills` folder if it doesn't exist yet.
4. Restart Claude Code.

### Coding tools (GitHub Copilot, Cursor, Windsurf, Codex, Gemini CLI, Cline)

These tools read instruction files from the project folder you have open.

1. At the top of this repo's page on GitHub, click the green **Code** button, then **Download ZIP**.
2. Unzip the download.
3. Open the `agents` folder and then the folder for your tool:

   | Tool | Folder | What's inside |
   |---|---|---|
   | GitHub Copilot | `agents/github-copilot` | a `.github` folder |
   | Cursor | `agents/cursor` | a `.cursor` folder |
   | Windsurf | `agents/windsurf` | a `.windsurf` folder |
   | OpenAI Codex | `agents/codex` | an `AGENTS.md` file and a `.agents` folder |
   | Gemini CLI | `agents/gemini-cli` | a `GEMINI.md` file |
   | Cline | `agents/cline` | a `.clinerules` folder |

4. Copy everything inside that folder into the top level of the project you work in.

Folders that start with a dot are hidden by default. To see them on a Mac, press Command + Shift + period in Finder. On Windows, open File Explorer, click **View**, then **Show**, then **Hidden items**.

If your project already has a `.github` folder, `AGENTS.md` or `GEMINI.md`, merge the new files in rather than replacing what's there.

In GitHub Copilot Chat you can also type `/miva-flex-component` to start a request with the instructions loaded.

## Using it

Describe what you want the way you'd explain it to a developer. Include what shoppers should see, what you want to be able to change in Page Builder, and anything that should look like the rest of your theme. A screenshot or link to an example helps.

Example requests:

```
Build a Page Builder component that shows 3 to 6 store benefits in a row,
each with an icon, a short title and one sentence. On phones they should
stack. I want to edit the text and pick the icons in Page Builder.
```

```
Make a copy of mmx-hero called "promo-hero" that adds a countdown timer
under the button. I want to set the end date in Page Builder.
```

```
This component won't upload. Here's the file and the error message.
```

The assistant may ask a few questions first. When it's done, you get a file ending in `.tar.bz2` and a README that explains the component's settings.

### Upload the component to your store

1. In Miva Admin, go to **User Interface**, then **Flex Components**.
2. Click **Upload Component** and choose the `.tar.bz2` file.
3. Open Page Builder, edit a page and click **Add Component**. Your new component is in the list.

To change a component later, attach its `.tar.bz2` file to a new chat and say what to change. The assistant updates the version number so Miva knows it's an update.

## If something goes wrong

| Problem | What to do |
|---|---|
| The assistant doesn't seem to know about Miva components | Mention it directly: "Use the Miva flex component instructions." In claude.ai, check that the skill's switch is on. |
| The upload fails | Copy the error message from Miva Admin and paste it into the chat along with the file. |
| The component uploads but looks wrong or empty on the page | Take a screenshot of the page and the component's settings, and send them to the assistant. |
| You want to restyle a built-in Miva component without copying it | Ask for changes using the `mmx-customizations` stylesheet. It's simpler than a copy and keeps getting Miva's updates. |

## For developers

The rest of this page covers how the repo is organized.

### Repository layout

```
skills/miva-page-builder-flex-component-generator/SKILL.md   source of truth
scripts/build.py                                             generates everything below
agents/<tool>/...                                            per-tool instruction files
downloads/miva-page-builder-flex-component-generator.zip     claude.ai upload package
tools/validate_flex.py                                       component validator
```

### Making changes

Edit only `SKILL.md`, then regenerate the other files:

```bash
python scripts/build.py
```

The build writes each tool's file with the frontmatter it expects, swaps a few Claude-specific phrases for neutral wording, splits the Windsurf rules into parts under Windsurf's 12,000-character limit, rebuilds the zip and extracts the validator. Commit the regenerated files with the `SKILL.md` change.

When a new Shadows release ships, update the baseline version in `SKILL.md`, check section 6 against the mmx-base changes and rebuild.

### Validator

`tools/validate_flex.py` checks a component folder for the problems that most often break an upload: missing files, `managed: true`, leftover `integrity` hashes, resource codes that don't match init.mvt, `depends` written as an array, list prompts missing `:value`, and copies of Miva components that still use an `mmx-*` tag.

```bash
python tools/validate_flex.py path/to/component-folder
```

Add `--managed` only when checking an unmodified Miva component.

### Miva Docs MCP server

The instructions tell the assistant to look up current Shadows source and documentation instead of relying on memory. If your assistant supports MCP and you have access to the Miva Docs MCP server, connect it. Without it, the assistant uses the public repos:

- https://github.com/mivaecommerce/shadows
- https://github.com/mivaecommerce/flex-components
