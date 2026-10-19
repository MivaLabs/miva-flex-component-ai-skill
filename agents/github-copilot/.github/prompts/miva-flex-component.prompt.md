---
agent: agent
description: Build, fork, update or debug a Miva Page Builder flex component
---

Follow these instructions for the request: ${input:request:Describe the component}

# Miva Page Builder Flex Component Generator

Produce a working flex component package (`{code}.tar.bz2`) that imports cleanly in **Miva Admin > User Interface > Flex Components > Upload Component** and renders correctly in Page Builder.

Current baseline: **Shadows 26.02.00** (mmx-base 26.02.00). The framework changes several times a year, so treat anything in this file about specific mmx components as a summary and pull live source before copying patterns.

---

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

---

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

---

## 3. Choose an architecture

| | Basic | Web Component | MMX |
|---|---|---|---|
| What | Plain HTML from instance.mvt + optional JS/CSS | Vanilla Custom Element, own Shadow DOM | `class X extends MMX_Element` from mmx-base |
| Pick when | Simple display, SEO-heavy markup, no encapsulation | Style isolation, no framework | Theme typography/buttons, `mmx-text`/`mmx-button`, JSON API, MMX helpers, consistency with Shadows |
| `depends` | none | none | `mmx-base` (+ any mmx libs used) |
| CSS placement | normal `<mvt:item>` in init.mvt | inside a `<template>` cloned into the shadow root | inside `<template class="mmx-resources">` + listed in `styleResourceCodes` |
| Reference | `examples/ex-basic` | `examples/ex-web-component` | `examples/mmx-example` + nearest Shadows component |

Default to **MMX** when the store runs Shadows and the component shows text/buttons editors will want to theme. Default to **Basic** for simple one-off markup.

---

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

---

## 5. Templates

### init.mvt (runs once per page; Miva de-duplicates by resource code)

MMX architecture, in this order:

```mvt
<mvt:item name="head" param="css:mmx-base" />
<mvt:item name="head" param="css:mm-theme-styles" />
<mvt:item name="head" param="css:mmx-customizations" />

<template class="mmx-resources">
	<mvt:item name="head" param="css:mmx-text" />
	<mvt:item name="head" param="css:acme-feature-grid" />
</template>

<mvt:item name="head" param="js:mmx-base" />
<mvt:item name="head" param="js:mmx-text" />
<mvt:item name="head" param="js:acme-feature-grid" />
```

Shadow-DOM CSS goes inside `<template class="mmx-resources">`; JS and page-level CSS stay outside. Basic: just the component's css/js items. Web Component: js item outside, a `<template id="{code}-template">` containing the css item and initial markup.

Product/basket components also render Miva clientside scripts; copy those lines from the nearest Shadows component (`mmx-featured-product`, `mmx-quick-order`) instead of retyping them.

### instance.mvt (runs per placement)

MMX boilerplate used by every Shadows component:

```mvt
<mvt:if expr="l.settings:instance:advanced:loading:value EQ 'eager' OR (ISNULL l.settings:instance:advanced:loading:value AND l.settings:total_sequence_item_pos EQ 1)">
	<mvt:assign name="l.settings:instance:fetchpriority" value="'high'" />
	<mvt:assign name="l.settings:instance:loading" value="'eager'" />
<mvt:else>
	<mvt:assign name="l.settings:instance:fetchpriority" value="'low'" />
	<mvt:assign name="l.settings:instance:loading" value="'lazy'" />
</mvt:if>

<mvt:if expr="NOT ISNULL l.settings:fragment:code">
	<mvt:assign name="l.settings:page_code" value="l.settings:fragment:code" />
	<mvt:assign name="l.settings:component_id" value="l.settings:page_code $ '__' $ l.settings:instance_item:component_code $ '__' $ l.settings:instance_item:item_code" />
<mvt:else>
	<mvt:assign name="l.settings:page_code" value="l.settings:page:code" />
	<mvt:assign name="l.settings:component_id" value="l.settings:instance_item:component_code $ '__' $ l.settings:instance_item:item_code" />
</mvt:if>

<acme-feature-grid
	id="&mvte:component_id;"
	data-page-code="&mvte:page_code;"
	data-flex-component="&mvte:instance_item:component_code;"
	data-flex-item="&mvte:instance_item:item_code;"
	class="mmx-wrapper"
	style="margin-top: &mvte:instance:advanced:spacing:top:value;px; margin-bottom: &mvte:instance:advanced:spacing:bottom:value;px;"
	data-init="script"
>
	<script type="application/json">
		<mvt:eval expr="miva_json_encode( l.settings:instance, '' )" />
	</script>
	<!-- server-rendered slot content (mmx-text, picture, etc.) -->
</acme-feature-grid>
```

- `data-init="script"` + the JSON script is how `this.data` gets populated. Without it the element renders empty.
- The id/data attributes must match `preview_component_selector`.
- Server-render text into slots with `<mmx-text slot="..." data-theme=... data-theme-class=... data-style=... data-tag=...>` and the theme/legacy `<template>` blocks. Copy the exact block from `mmx-image-and-text`'s instance.mvt for each text/button field.
- Escape with `&mvte:` in attributes and text; use `&mvt:` (raw) only for theme stylesheets and trusted markdown/HTML.
- Debug the data shape with `<mvt:assign name="g.mvt_debug" value="glosub( miva_array_serialize( l.settings:instance ), ',', asciichar( 10 ) )" />` then `<!-- &mvt:global:mvt_debug; -->` (remove before shipping).
- Only for components with `initial_display`: compute `formatted_value` like `mmx-product-carousel` and add `--mmx-initial-height: ...;` to the style attribute.

### upgrade.mvt (optional, runs on saved instances after a version bump)

Gate each migration on the version the data was saved with:

```mvt
<mvt:if expr="l.settings:instance:_flex:settings_version LT '1.1.0'">
	<mvt:assign name="l.settings:instance:items:new_field:value" value="'default'" />
	<mvt:eval expr="miva_member_delete( l.settings:instance, 'old_field' )" />
</mvt:if>
```

Add `"upgrade_template": "src/templates/upgrade.mvt"` to flex.json only when the file exists.

---

## 6. JavaScript

### MMX component (26.02 pattern)

```javascript
class Acme_FeatureGrid extends MMX_Element {
	static get props() {
		return {
			columns: { allowAny: true, isNumeric: true, default: 3 },   // reads data-columns
			'show-icons': { isBoolean: true, default: true }
		};
	}

	styleResourceCodes = ['mmx-base', 'mmx-text', 'acme-feature-grid'];
	renderUniquely = true;

	constructor() {
		super();
		this.makeComponent();          // 26.02+: shadow root + ElementInternals states
	}

	onDataChange() {                   // this.data = parsed instance JSON
		this.setSpacing(this.data?.advanced?.spacing);
	}

	styles() {
		return /*css*/`:host { --acme-feature-grid__columns: ${this.getPropValue('columns')}; }`;
	}

	render() {
		const items = this.data?.items?.children ?? [];
		return /*html*/`
			<div class="acme-feature-grid" part="wrapper">
				<slot name="heading"></slot>
				${items.map(item => /*html*/`
					<div class="acme-feature-grid__item" part="item">
						${this.renderTextProperty(item?.title, { prefix: 'title_', className: 'acme-feature-grid__title', defaultStyle: 'title-3', defaultTag: 'h3' })}
					</div>`).join('')}
			</div>`;
	}

	afterRender() {
		this.on('click', '.acme-feature-grid__item', (e, item) => { /* delegated, survives re-render */ });
	}
}

if (!customElements.get('acme-feature-grid')) {
	customElements.define('acme-feature-grid', Acme_FeatureGrid);
}
```

Every user value that ends up in markup goes through `MMX.encodeEntities()` or `renderTextProperty`/`renderButtonProperty`. Their `prefix` option must match the textsettings field codes: `prefix: 'title_'` reads `title_style` / `title_tag` (theme from `typography_theme`); `renderButtonProperty` defaults to `prefix: 'button_'` and reads `button_theme`, `button_style`, `button_size`.

**What 26.02 added to mmx-base** (use when `depends.mmx-base >= 26.02.00`; otherwise fall back to `makeShadow()` and skip the rest):

| Feature | Use |
|---|---|
| `makeComponent()` | Replaces `makeShadow()` in constructors. Adds custom states `:state(mmx)`, `rendered`, `styled`, `ready`. mmx-base CSS fades an element in only once it is styled and ready, which removes the flash of unstyled content. |
| `setLifecycleReady(false)` / `forceUpdate()` | For async components: call `setLifecycleReady(false)` before fetching so the element stays hidden (with `--mmx-initial-height` reserving space), then `forceUpdate()` when data arrives. If you forget the `forceUpdate()`, the component stays invisible. |
| Adoptable styles | Add `{"name":"rel","value":"preload"}, {"name":"as","value":"style"}, {"name":"data-mmx-resource-type","value":"adoptable"}` to a style resource in `<template class="mmx-resources">`. `MMX.styleManager` fetches it once and shares a `CSSStyleSheet` across every shadow root. Still list the code in `styleResourceCodes`. Requires mmx-base ≥ 26.02 (with `rel=preload`, older bases never apply the sheet). |
| `this.on(events, selector, handler)` / `MMX.on(...)` | Delegated listeners on the shadow root; events can be a comma list (`'mouseover, touchstart'`). |
| `MMX.Runtime_JSON_API_Call({params, cached: true})` | De-duplicates identical requests across instances on the page. |
| `MMX.cacheKeysFilters(records)` | Builds a `cache_keys` filter from `dt_updated` so cached API responses bust when records change. |
| `static formAssociated = true` | Makes the element a real form control; then use `setFormValue`, `setValidity`, `checkValidity`, `reportValidity`, `validity`. |

**Core MMX_Element members**: `getPropValue(name)`, `hasPropValue(name)`, `this.data`, `styleResourceCodes`, `themeResourcePattern`, `renderUniquely`, `hideOnEmpty`, hooks `connected`, `disconnected`, `onDataChange`, `beforeRender`, `afterRender`, `attributeChanged(name, old, new)`, renderers `renderTextProperty`, `renderButtonProperty`, `renderThemeStylesheetTemplate`, `renderContentIntoLightDomSlot`, `renderProductFragment`, `getLoadingAttributeString()`, `setSpacing()`, `getStylesFromGroup()`.

**MMX utilities worth knowing**: `encodeEntities`, `coerceNumber`, `coerceString`, `isTruthy`, `valueIsEmpty`, `arrayIsEmpty`, `copy`, `assign`, `createElement`, `setElementAttributes`, `setElementStyles`, `closestElement` (crosses shadow roots), `debounce`, `elementInViewport`, `longMerchantUrl`, `fetchForm`, `getCustomFieldValueFromRecord`, `objectToCssShorthand`, `composeUnitValue`, `boxShadowObjectToCssValue`, `renderBreakpointStyle`, `getBreakpoints`. For anything else, read mmx-base via `get_shadows_framework(code="mmx-base")`.

### Basic and Web Component

Basic: `document.addEventListener('DOMContentLoaded', () => document.querySelectorAll('.{code}').forEach(el => {...}))`. Web Component: `class X extends HTMLElement`, `attachShadow({mode:'open'})` in the constructor, clone `#{code}-template` in `connectedCallback`, `observedAttributes` + `attributeChangedCallback`. Always guard `customElements.define` with `customElements.get`.

---

## 7. CSS

- Inside shadow DOM: `:host { display: block; }`, BEM classes namespaced with the component code, expose styling hooks with `part="..."`.
- Theme with mmx-base variables (`var(--mmx-color-primary-bg)`, `--mmx-font-family-1`, etc.). Merchants override them and `::part()` rules in the `mmx-customizations` resource, which must be activated under User Interface > CSS Resources.
- Nested web components need `exportparts` for their parts to be reachable from outside.
- Light-DOM pages: hide undefined elements to avoid a flash (`acme-feature-grid:not(:defined) { visibility: hidden; }`) in a page-level stylesheet.

---

## 8. Data from the store

Use `MMX.Runtime_JSON_API_Call` and look up function parameters with `get_json_api_function`. Example:

```javascript
MMX.Runtime_JSON_API_Call({ cached: true, params: {
	function: 'Runtime_ProductList_Load_Query', count: 0,
	filter: [{ name: 'search', value: [{ field: 'code', operator: 'IN', value: codes.join(',') }] },
	         { name: 'ondemandcolumns', value: ['CustomField_Values:customfields:brand'] }]
}}).then(r => r.data.data);
```

Custom fields: a `productcustomfieldlookup` value is already `"module:field"` (e.g. `customfields:brand`). Request it as `CustomField_Values:${value}` (don't add another `customfields:`), and read it as `product.CustomField_Values[module][field]` after `value.split(':')`. `CustomField_Values.customfields` is a flat object keyed by field code. Merchandising showcases pass `MerchandisingShowcase_Code` (and an optional `Merchandising_Context` of product/category id); see `mmx-product-carousel`.

---

## 9. Forking an mmx component (official process)

Pull the full source from the shadows repo (§1), then:

1. Copy `flex-components/{mmx-code}/` to a folder named after the new code.
2. flex.json: new `code`, `name`, `version` (1.0.0), `resourcegroup_code`; `managed: false`; new `resource_code` and `filepath` for each script/style you keep; remove all `integrity` attributes; keep `depends` but change `=26.02.00` pins to `>=26.02.00` unless the user wants exact pins; drop `conflicts` unless needed.
3. **JS**: rename the file, the class, and the tag (`mmx-featured-product` → `acme-featured-product`) and update `customElements.get/define`. Replace the component's own code in `styleResourceCodes` with the new CSS resource code. If the JS extends another mmx class (e.g. `MMX_Hero`), keep extending it and keep that dependency.
4. **CSS**: rename the file. Optionally rename the class namespace (`.mmx-featured-product` → `.acme-featured-product`) in both the CSS and the JS `render()`.
5. **init.mvt**: swap only the component's own `css:`/`js:` params for the new resource codes; leave dependency lines alone.
6. **instance.mvt / upgrade.mvt**: change the custom element tag to the new tag; otherwise copy as is. Usually drop `upgrade.mvt` and its flex.json field: a fork never receives data saved by the original, and with the version reset to 1.0.0 every `settings_version LT '26.x'` check in it would fire on the fork's own data and reset settings.
7. Keep `src/images/preview.svg`/`detailed_preview.svg` if flex.json references them.

Never ship a fork that still defines an `mmx-*` tag. The `customElements.get` guard means whichever script loads first wins, so the fork silently runs Miva's class (or Miva's runs yours), and the fork's renamed CSS never reaches the shadow root.

If the user only wants restyling, suggest `mmx-customizations` (CSS variables + `::part()`) before forking.

---

## 10. Validate, package, deliver

Save this validator to a temporary folder outside the component folder and run it on the component folder. Use `--managed` only when checking an untouched Miva component.

```python
#!/usr/bin/env python3
"""Validate a Miva flex component folder. Usage: python3 validate_flex.py <component-dir> [--managed]"""
import json, os, re, sys
KNOWN = {'text','textarea','texteditor','checkbox','radio','select','selector','color','date','datetime','slider',
 'distributedslider','image','imagetype','link','fragment','product','category','customlookup','productcustomfieldlookup',
 'categorycustomfieldlookup','merchandisingshowcase','merchandisingprompt','group','list','font','typography','button',
 'padding','lengthunit','cornerradius','borderthickness','dropshadow','breakpoint','breakpointgroup','page'}
GLOBAL_RES = {'mm-theme-styles', 'mmx-customizations'}
err, warn = [], []
def main(d, managed_ok):
    fj = os.path.join(d, 'flex.json')
    if not os.path.isfile(fj): return err.append('flex.json missing at component root')
    try: f = json.load(open(fj))
    except Exception as e: return err.append(f'flex.json is not valid JSON: {e}')
    for k in ('code', 'name', 'type', 'version'):
        if not f.get(k): err.append(f'flex.json missing "{k}"')
    code = f.get('code', '')
    if code and not re.fullmatch(r'[a-z][a-z0-9-]+', code): err.append(f'code "{code}" must be lowercase letters, digits, hyphens')
    if f.get('resourcegroup_code') != code: warn.append('resourcegroup_code usually equals code')
    if f.get('managed', True) and not managed_ok: err.append('custom components need "managed": false')
    deps = f.get('depends') or {}
    if not isinstance(deps, dict): err.append('depends must be an object {"code": ">=version"}'); deps = {}
    for p in ('initialization_template', 'instance_template', 'upgrade_template', 'preview', 'detailed_preview'):
        if f.get(p) and not os.path.isfile(os.path.join(d, f[p])): err.append(f'{p} file not found: {f[p]}')
    own = {}
    for kind in ('scripts', 'styles'):
        for r in f.get(kind, []):
            if not os.path.isfile(os.path.join(d, r.get('filepath', ''))): err.append(f'{kind} file not found: {r.get("filepath")}')
            own[('js' if kind == 'scripts' else 'css') + ':' + r.get('resource_code', '')] = r
            names = {a.get('name'): a.get('value') for a in r.get('attributes', [])}
            if 'integrity' in names and not managed_ok: err.append(f'remove "integrity" attribute from {r.get("filepath")}')
            if names.get('data-mmx-resource-type') == 'adoptable' and code != 'mmx-base' and not re.search(r'26\.0[2-9]|2[7-9]\.|[3-9]\d\.', str(deps.get('mmx-base', ''))):
                err.append(f'{r.get("filepath")} is adoptable: depends.mmx-base must be >=26.02.00')
    for im in f.get('images', []):
        if not os.path.isfile(os.path.join(d, im.get('source_filepath', ''))): err.append(f'images source not found: {im.get("source_filepath")}')
    init = read(d, f.get('initialization_template'))
    used = set(re.findall(r'param="((?:css|js):[\w-]+)"', init))
    for key in own:
        if key not in used and f.get('type') != 'library': err.append(f'init.mvt never outputs own resource "{key}"')
    for key in used - set(own):
        rc = key.split(':', 1)[1]
        if rc not in GLOBAL_RES and rc not in deps: warn.append(f'init.mvt loads "{key}" but "{rc}" is not in depends')
    walk(f.get('properties'), 'properties'); walk(f.get('advanced_properties') or [], 'advanced_properties')
    js = ''.join(read(d, r['filepath']) for r in f.get('scripts', []))
    inst = read(d, f.get('instance_template'))
    defined = set(re.findall(r"customElements\.define\(\s*['\"]([\w-]+)", js))
    if re.search(r'extends MMX_\w+', js):
        if 'mmx-base' not in deps: err.append('JS extends MMX_* but depends has no mmx-base')
        if 'makeShadow()' in js and 'makeComponent()' not in js: warn.append('use this.makeComponent() (26.02+) instead of makeShadow()')
        rcs = ''.join(re.findall(r'styleResourceCodes\s*=\s*\[([^\]]*)\]', js))
        for key in own:
            if key.startswith('css:') and rcs and key[4:] not in rcs: warn.append(f'styleResourceCodes lacks "{key[4:]}"; its CSS will not reach the shadow DOM')
    for tag in defined:
        if f"customElements.get('{tag}')" not in js and f'customElements.get("{tag}")' not in js: warn.append(f'guard define of <{tag}> with if (!customElements.get(...))')
        if tag.startswith('mmx-') and not code.startswith('mmx-'): err.append(f'custom component redefines Miva tag <{tag}>; rename the tag and class')
    tags = set(re.findall(r'<([a-z]\w*-[\w-]+)[\s>]', inst)) - {'mmx-text', 'mmx-button', 'mmx-icon'}
    if defined and tags and not tags & defined: warn.append(f'instance.mvt tags {sorted(tags)} not defined by this JS {sorted(defined)}')
def walk(props, path):
    seen = set()
    for p in props or []:
        c, t, here = p.get('code'), p.get('type'), f"{path}>{p.get('code')}"
        if not c or not t: err.append(f'{here}: property needs code and type'); continue
        if c in seen: warn.append(f'{here}: duplicate code among siblings')
        seen.add(c)
        if t not in KNOWN: warn.append(f'{here}: unknown type "{t}" (check MCP/schema)')
        if t in ('select', 'radio', 'selector') and not p.get('options'): err.append(f'{here}: {t} needs options')
        if t == 'list':
            if not p.get('list_type'): err.append(f'{here}: list needs list_type')
            ipp = p.get('item_prompt_property')
            if ipp and ':' not in ipp: err.append(f'{here}: item_prompt_property needs a member suffix, e.g. "{ipp}:value"')
        for tf in (p.get('textsettings') or {}).get('fields', []):
            if not tf.get('pseudoclasses'): warn.append(f'{here}: textsettings field {tf.get("code")} has no pseudoclasses')
        walk(p.get('properties'), here)
def read(d, rel):
    try: return open(os.path.join(d, rel)).read() if rel else ''
    except OSError: return ''
if __name__ == '__main__':
    main(sys.argv[1], '--managed' in sys.argv)
    for m in err: print('ERROR  ', m)
    for m in warn: print('WARN   ', m)
    print('PASS' if not err else f'FAIL ({len(err)} errors)'); sys.exit(1 if err else 0)
```

Also syntax-check the JS (`node --check src/js/*.js`) when Node is available.

**Package** from inside the component folder so `flex.json` sits at the archive root, and create folders with separate `mkdir -p` calls (brace expansion can produce a literal `{templates,js,css}` folder in some shells):

```bash
cd "$WORK/acme-feature-grid" && tar -cjf "../acme-feature-grid.tar.bz2" flex.json README.md src
tar -tjf "$WORK/acme-feature-grid.tar.bz2" | sort     # expect flex.json, README.md, src/... (no parent folder)
```

**README.md** (inside the package): name, description, code/version/category/architecture, dependencies table, properties table (code, prompt, type, default), files table, changelog starting at the flex.json version, and install steps (Upload Component, then add it in Page Builder).

**Deliver** the `.tar.bz2` and a copy of the README in the workspace, or in the folder the user named. Mention that after import the component appears under Page Builder > Add Component, and that iterative edits can be done with `mmt checkout` / `mmt push` against `properties/flex/{code}.json`, `templates/flex-initialization-template-{code}.mvt`, `templates/flex-instance-template-{code}.mvt`, `css/{code}.css`, `js/{code}.js`.

---

## 11. Troubleshooting

| Symptom | Likely cause |
|---|---|
| Import fails | flex.json not at archive root, a referenced file (preview, template, filepath, image) missing, invalid JSON, `managed: true`, or a leftover `integrity` hash |
| Component missing from Page Builder | `type: "library"`, or `code`/`resource_code` collides with an existing component |
| CSS or JS not loading | `resource_code` in flex.json ≠ `param` in init.mvt |
| Styles missing inside shadow DOM | CSS item not inside `<template class="mmx-resources">`, or its code not in `styleResourceCodes` |
| Element renders empty | No `data-init="script"` / JSON script in instance.mvt, or `render()` reads the wrong `this.data` path (dump it with the debug snippet) |
| Element stays invisible (26.02) | `setLifecycleReady(false)` without a later `forceUpdate()`, or an adoptable stylesheet failed to load |
| Fork looks or behaves like the original | Fork still defines an `mmx-*` tag; rename tag + class (§9) |
| List rows labelled `[object Object]` | `item_prompt_property` without `:value` |
| Theme typography ignored | Missing theme `<template data-theme-stylesheet>` block on the `mmx-text`, or `mm-theme-styles` not loaded |
| Custom field empty | Doubled `customfields:` prefix in `CustomField_Values:` request |
