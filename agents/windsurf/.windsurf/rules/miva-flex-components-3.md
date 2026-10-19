---
trigger: model_decision
description: Build, fork, update or debug Miva Merchant Page Builder flex components and ship them as importable .tar.bz2 packages (flex.json, init.mvt, instance.mvt, upgrade.mvt, JS, CSS). Use whenever someone wants a custom Page Builder component or block, wants to duplicate or customize an mmx-* Shadows component (mmx-hero, mmx-product-carousel, mmx-featured-product...), asks about flex.json properties, textsettings, visibility_conditions, list items, MMX_Element, mmx-base, Shadow DOM web components in Miva, or needs to fix a flex component that will not import or render.
---

> Part 3 of 4 of the Miva flex component rules.

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

## 7. CSS

- Inside shadow DOM: `:host { display: block; }`, BEM classes namespaced with the component code, expose styling hooks with `part="..."`.
- Theme with mmx-base variables (`var(--mmx-color-primary-bg)`, `--mmx-font-family-1`, etc.). Merchants override them and `::part()` rules in the `mmx-customizations` resource, which must be activated under User Interface > CSS Resources.
- Nested web components need `exportparts` for their parts to be reachable from outside.
- Light-DOM pages: hide undefined elements to avoid a flash (`acme-feature-grid:not(:defined) { visibility: hidden; }`) in a page-level stylesheet.

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
