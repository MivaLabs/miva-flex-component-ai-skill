---
trigger: model_decision
description: Build, fork, update or debug Miva Merchant Page Builder flex components and ship them as importable .tar.bz2 packages (flex.json, init.mvt, instance.mvt, upgrade.mvt, JS, CSS). Use whenever someone wants a custom Page Builder component or block, wants to duplicate or customize an mmx-* Shadows component (mmx-hero, mmx-product-carousel, mmx-featured-product...), asks about flex.json properties, textsettings, visibility_conditions, list items, MMX_Element, mmx-base, Shadow DOM web components in Miva, or needs to fix a flex component that will not import or render.
---

> Part 2 of 4 of the Miva flex component rules.

## 4. flex.json

```json
{
  "code": "acme-feature-grid",
  "name": "Feature Grid",
  "type": "component",
  "managed": false,
  "version": "1.0.0",
  "resourcegroup_code": "acme-feature-grid",
  "category": "text-utility",
  "description": "## Feature Grid\nIcon + text tiles in a responsive grid.",
  "preview_component_selector": "[data-page-code=\"%page_code%\"][data-flex-component=\"%component_code%\"][data-flex-item=\"%element_code%\"]",
  "initialization_template": "src/templates/init.mvt",
  "instance_template": "src/templates/instance.mvt",
  "properties": [],
  "advanced_properties": [],
  "defaults": {},
  "scripts": [{"filepath": "src/js/acme-feature-grid.js", "resource_code": "acme-feature-grid",
               "attributes": [{"name": "type", "value": "text/javascript"}]}],
  "styles":  [{"filepath": "src/css/acme-feature-grid.css", "resource_code": "acme-feature-grid",
               "attributes": [{"name": "type", "value": "text/css"}, {"name": "rel", "value": "stylesheet"}]}],
  "depends": {"mmx-base": ">=26.02.00", "mmx-text": ">=26.02.00"}
}
```

Rules that cause failed imports or broken pages when ignored:

- `type`: `"component"` (shows in Page Builder) or `"library"` (scripts/styles only, no templates or properties; use for shared code other components depend on).
- `managed: false` for anything custom. Remove every `integrity` attribute (Miva's SRI hashes won't match your files).
- `resourcegroup_code` = `code`. Every `resource_code` must be unique store-wide and must match the `css:`/`js:` params in init.mvt.
- `version`: `1.0.0` for new work. Bump it whenever you ship a change, and add an `upgrade_template` if saved instance data must change shape.
- `depends`/`conflicts` are **objects**: `{"mmx-base": ">=26.02.00"}`. Operators `=`, `>=`, `>`, `<`, `<=`. Use `>=` for custom work; Shadows pins `=` because it ships as a set. Every mmx resource loaded in init.mvt should be listed.
- `preview`, `detailed_preview`, `upgrade_template` and every `filepath` must exist in the archive or the import fails. Drop the field rather than pointing at a missing file.
- `images`: copies bundled files to the store on import. `[{"source_filepath": "src/images/placeholder.jpg", "destination_filepath": "graphics/%STORE_ID%/acme/placeholder.jpg"}]`; then use that destination path in `defaults`.
- `sample_data_types`: tells Page Builder which mock data to load for preview. Types `product`, `category`, `search`, `order`, `payment`; optional conditions joined with OR inside an array and AND across keys: `[{"type":"product","conditions":{"settings:source:value":["auto"]}}]`. Add it when the component reads the current page's product/category.
- `category` (controls the icon): `accordion`, `category-carousel`, `combination-facet`, `contact-form`, `featured-product`, `image`, `image-across`, `image-slider`, `image-text`, `non-element`, `product-carousel`, `product-display`, `product-fitment-list`, `product-list`, `quick-order`, `text-area`, `text-banner`, `text-editor`, `text-utility`, `video`.
- `preview_component_selector` (component root) and per-property `preview_property_selector` drive Page Builder's live highlight. Tokens: `%component_code%`, `%page_code%`, `%element_code%`, `%element_item_code%`, `%sequence_code%`, `%sequence_item_code%`; inside lists `%nth-child%` / `%nth-of-type%`; ` :shadow ` steps into a shadow root, e.g. `":shadow [part~=\"content\"]"`.

### 4a. Property types

Every property: `code`, `prompt`, `type`; optional `required`, `tooltip: {title, content}`, `visibility_conditions`, `preview_property_selector`.

| Type | Notes / extra keys |
|---|---|
| `text` | `text_type`: text, email, url, password, tel, **number** (+ `min`,`max`,`step`); `label`, `placeholder`, `minlength`, `maxlength`, `validation_pattern`, `validation_message`, `textsettings` |
| `textarea` | `markdown: 1` stores markdown; render with `data-source="markdown"` on `mmx-text` |
| `texteditor` | Rich text (HTML) in a modal |
| `checkbox` | stored as 0/1 |
| `select` / `radio` | `options: [{text, value}]`; an option with no `value` = empty/default |
| `selector` | button group; icon options `{"type":"icon","text":"<miva icon>","value":..}` |
| `date` / `datetime` | `min`, `max`, `serverdate` |
| `color`, `font` (`style`,`weight`), `typography` / `button` (`supports_customization`, `supports_legacy`) | theme pickers |
| `slider` | `range_low`, `range_high`, `scale`, `precision`, `label` |
| `distributedslider` | `breaks` |
| `image` | `width`, `height`, `responsive_images: [{code, prompt, width, height}]` |
| `imagetype`, `link` (`supports_new_tab`), `page`, `fragment`, `product`, `category` | pickers |
| `productcustomfieldlookup`, `categorycustomfieldlookup` | value is `"module:field"` (see §8) |
| `customlookup` | `lookup: {module_code, module_function, selection_column, columns[...]}` |
| `merchandisingshowcase` | **26.02** replacement for `merchandisingprompt` (value at `...:showcase:code`, context ids at `:showcase:context`) |
| `padding`, `lengthunit`, `cornerradius`, `borderthickness`, `dropshadow` | style values objects (`{value, unit}` etc.) |
| `breakpoint`, `breakpointgroup` (`include_default`, nested `properties`) | responsive settings |
| `group` | `properties`, `collapsed`, `can_disable` (adds `:settings:enabled`) |
| `list` | `list_type`: text, image, product, category, color, date, datetime, link, group; `min_count`, `max_count`, `template` (values for a newly added item); for groups also `properties`, `group_prompt`, `item_prompt_property` |

Pull the exact shape of anything unusual from `examples/ex-kitchen-sink/flex.json` or a Shadows component that uses it.

### 4b. Lists

```json
{"code": "items", "prompt": "Items", "type": "list", "list_type": "group",
 "group_prompt": "Item", "item_prompt_property": "title:value", "min_count": 1, "max_count": 12,
 "template": {"title": {"value": "New item"}},
 "properties": [{"code": "title", "prompt": "Title", "type": "text"},
                {"code": "img", "prompt": "Image", "type": "image", "width": 400, "height": 400}]}
```

- `item_prompt_property` needs the member path: `"title:value"` for text. A bare `"title"` shows `[object Object]` in the editor. Non-text members use their own field, e.g. `"category:category_code"`.
- Defaults for lists use `children`: `"items": {"children": [{"title": {"value": "One"}}, {"title": {"value": "Two"}}]}`.
- In MVT: `<mvt:foreach iterator="item" array="instance:items:children"> &mvte:item:title:value; </mvt:foreach>`.

### 4c. textsettings (theme typography/buttons on a text field)

Copy the block from a Shadows component (e.g. `mmx-image-and-text` heading/button) rather than writing it by hand. Shape:

```json
"textsettings": {"fields": [
  {"code": "typography_theme", "prompt": "Typography", "type": "typography", "pseudoclasses": ["normal"], "supports_customization": 1, "supports_legacy": 1},
  {"code": "heading_style", "prompt": "Heading Style", "type": "select", "pseudoclasses": ["normal"],
   "options": [{"text": "Default"}, {"text": "Title One", "value": "title-1"}],
   "visibility_conditions": {"normal": {"typography_theme": {"theme_mode": [0]}}}},
  {"code": "heading_tag", "prompt": "Heading Tag", "type": "select", "pseudoclasses": ["normal"],
   "options": [{"text": "Default"}, {"text": "h2", "value": "h2"}],
   "visibility_conditions": {"normal": {"typography_theme": {"theme_mode": [0]}}}}
]}
```

For buttons use a `button` type field named `button_theme` plus `button_style`/`button_size` selects (see `mmx-hero`).

### 4d. visibility_conditions and defaults

```json
"visibility_conditions": {"source": {"value": ["category", "hybrid"]}}           // sibling select/radio
"visibility_conditions": {"normal": {"typography_theme": {"theme_mode": [0]}}}    // inside textsettings
```

Conditions are exact matches; multiple keys are ANDed, multiple values ORed.

`defaults` mirrors the property tree. Advanced-property defaults nest under `"advanced"`. Text-like values are objects: `{"value": "..."}`; groups with `can_disable` use `{"settings": {"enabled": 1}}`; textsettings defaults look like `{"value": "Heading", "textsettings": {"fields": {"normal": {"typography_theme": {"code": "title-1", "theme_mode": 1}}}}}`. Give every visible field a default so the component previews well when dropped in.

### 4e. Standard advanced properties (Shadows convention)

`loading` (select: Default/lazy/eager), `spacing` group (`top`/`bottom`, text number px, min -50 max 200), and for components that fetch data after load (26.02) `initial_display` group: `initial_height` select (auto/custom/none) + `initial_height_amount` lengthunit shown when custom. Copy them from `mmx-image-and-text` / `mmx-product-carousel`.
