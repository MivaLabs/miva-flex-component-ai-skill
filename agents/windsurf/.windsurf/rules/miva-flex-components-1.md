---
trigger: model_decision
description: Build, fork, update or debug Miva Merchant Page Builder flex components and ship them as importable .tar.bz2 packages (flex.json, init.mvt, instance.mvt, upgrade.mvt, JS, CSS). Use whenever someone wants a custom Page Builder component or block, wants to duplicate or customize an mmx-* Shadows component (mmx-hero, mmx-product-carousel, mmx-featured-product...), asks about flex.json properties, textsettings, visibility_conditions, list items, MMX_Element, mmx-base, Shadow DOM web components in Miva, or needs to fix a flex component that will not import or render.
---

> Part 1 of 4 of the Miva flex component rules.

# Miva Page Builder Flex Component Generator

Produce a working flex component package (`{code}.tar.bz2`) that imports cleanly in **Miva Admin > User Interface > Flex Components > Upload Component** and renders correctly in Page Builder.

Current baseline: **Shadows 26.02.00** (mmx-base 26.02.00). The framework changes several times a year, so treat anything in this file about specific mmx components as a summary and pull live source before copying patterns.

## 1. Sources of truth (look things up, don't guess)

Use the **Miva Docs MCP server** first when it is configured for this agent; otherwise go straight to the GitHub repos below. It tracks the current Shadows release.

| Need | Tool call |
|---|---|
| A Shadows component's templates (init/instance/upgrade), JS source, and property tree | `get_shadows_framework(code="mmx-hero")` |
| flex.json fields, property types, preview selectors, styling, guides | `search_miva_developer_docs(query, doc_type="developer_docs")` or `doc_type="flex_component"` |
| Shadows/MMX snippets by topic ("makeComponent", "textsettings button") | `search_miva_developer_docs(query, doc_type="shadows_framework")` |
| Runtime JSON API functions (e.g. `Runtime_ProductList_Load_Query`) | `get_json_api_function(...)` / `doc_type="json_api"` |

`get_shadows_framework` returns a **summarized property tree, not the raw flex.json**. When you need the exact flex.json (forking, copying defaults, textsettings options, sample_data_types), get it from the public GitHub repos:

```bash
git clone --depth 1 https://github.com/mivaecommerce/shadows.git        # flex-components/{code}/ = full source, all files
git clone --depth 1 https://github.com/mivaecommerce/flex-components.git # examples/, schema/types.d.ts, guides/
```

Useful in `flex-components`: `examples/ex-basic`, `ex-web-component`, `mmx-example` (the three architectures), `ex-faqs` (list of groups), `ex-comparison-table`, `ex-kitchen-sink` (almost every property type), `dup-featured-product` (an official fork), and `schema/types.d.ts` (flex.json schema with comments).

If neither the MCP nor GitHub is reachable, say so and ask the user to download the component from Miva Admin (Flex Components > check it > Download Component) and attach it.

**When sources disagree**, trust them in this order: current Shadows source > `schema/types.d.ts` > developer docs prose. Known doc drift: the docs show `depends` as an array and `visibility_conditions` as `{"code": true}`. Real components use an object for `depends` and `{"code": {"value": [..]}}` for conditions.

## 2. Workflow

1. **Classify the request**: new component, fork of an mmx component, or change/fix to an existing package (if they attached a .tar.bz2, extract it and run the validator in §10 first).
2. **Gather requirements in one or two rounds**, not ten single questions. Skip anything the request already answers and use sensible defaults for the rest (state them). Typical round:
   - name + code (`/^[a-z][a-z0-9-]+$/`, never starting with `mmx-`), category, short description
   - what editors configure (content fields, repeatable items, settings) and what the shopper sees/does
   - architecture (§3), or let the assistant pick and explain why
   - whether it must work on stores older than 26.02 (affects §6 features and `depends`)
3. **Research**: pull the closest Shadows component or example via §1 and copy its real patterns.
4. **Build** the files (§4–§7). Write files directly; for a fork, start from the real source files.
5. **Validate** with the script in §10 and fix every ERROR. Read WARNs and fix the ones that apply.
6. **Package and deliver** (§10) with a README.
7. Summarize: code, architecture, properties, dependencies, how to import, and anything the user still has to do in Admin (for example activating `mmx-customizations`).

## 3. Choose an architecture

| | Basic | Web Component | MMX |
|---|---|---|---|
| What | Plain HTML from instance.mvt + optional JS/CSS | Vanilla Custom Element, own Shadow DOM | `class X extends MMX_Element` from mmx-base |
| Pick when | Simple display, SEO-heavy markup, no encapsulation | Style isolation, no framework | Theme typography/buttons, `mmx-text`/`mmx-button`, JSON API, MMX helpers, consistency with Shadows |
| `depends` | none | none | `mmx-base` (+ any mmx libs used) |
| CSS placement | normal `<mvt:item>` in init.mvt | inside a `<template>` cloned into the shadow root | inside `<template class="mmx-resources">` + listed in `styleResourceCodes` |
| Reference | `examples/ex-basic` | `examples/ex-web-component` | `examples/mmx-example` + nearest Shadows component |

Default to **MMX** when the store runs Shadows and the component shows text/buttons editors will want to theme. Default to **Basic** for simple one-off markup.
