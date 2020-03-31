## nani (0.1kB) - toy web framework

```js
/**
 * @license
 * Nani | Released under MIT license | Copyright Maciej A. Czyzewski
 */
var nani=function(){function t(){Array.prototype.forEach.call(document.querySelectorAll("[\\@]"),function(t,e){t.setAttribute("id","i"+e),Array.prototype.forEach.call(t.querySelectorAll("[\\#]"),function(e,n){nani.defs["#"][e.getAttribute("#")](t,e)})}),function t(){var t=function(t){t.target.setAttribute("value",t.target.value)};Array.prototype.forEach.call(document.querySelectorAll("input"),function(e,n){e.addEventListener("input",t,!1)})}()}function e(){Array.prototype.forEach.call(document.querySelectorAll("[\\!]"),function(t,n){t.onclick=function(t){var n=function t(e){return function n(t,e){return null!==t.getAttribute(e)}(e,"@")?e:t(e.parentNode)}(t.target);nani.defs["!"][t.target.getAttribute("!")](n,t.target),e()}})}return Element.prototype.remove=function(){this.parentElement.removeChild(this)},Element.prototype.set=function(t,e){this.setAttribute("js-"+t,e)},Element.prototype.get=function(t){return this.getAttribute("js-"+t)},document.addEventListener("DOMContentLoaded",function(){t(),e()}),{render:t,defs:{"#":{},"!":{}}}}();
```

---

![](screen.png)

```html
<h1>Welcome to my book collection</h1>
<button @ !=new>Add new book</button>

<ul>
    <li class="header">
        <cell>Name</cell>
        <cell>Author</cell>
        <cell>Action</cell>
    </li>
    <li js-edit=1 @>
        <cell #=data>Daniel Kahneman</cell>
        <cell #=data>Thinking, Fast and Slow</cell>
        <cell #=menu>?</cell>
    </li>
    <li @>
        <cell #=data>Maciej A. Czyzewski</cell>
        <cell #=data>Reading Rainbow</cell>
        <cell #=menu>?</cell>
    </li>
</ul>
```

```js
nani.defs = {
	'#': {
		'data': function(component, el) {
			var input = el.querySelectorAll("input");

			if (component.get('edit') == true) {
				if (input.length == 0) {
					el.innerHTML = `
							<input type="text" value="${el.innerHTML}">
						`;
				}
			} else {
				if (input.length != 0) {
					el.innerHTML = `${input[0].value}`;
				}
			}
		},
		'menu': function(component, el) {
			if (component.get('edit') == true) {
				el.innerHTML = `
						<button !=save>save</button>
						<button !=remove>remove</button>
					`;
			} else {
				el.innerHTML = `
						<button !=edit>edit</button>
						<button !=remove>remove</button>
					`;
			}
		}
	},
	'!': {
		'remove': function(component, el) {
			component.remove();
		},
		'edit': function(component, el) {
			component.set('edit', 1);
			nani.render();
		},
		'save': function(component, el) {
			component.set('edit', 0);
			nani.render();
		},
		'new': function(component, el) {
			var ul = document.querySelectorAll("ul")[0];
			ul.insertAdjacentHTML('beforeend', `
					<li js-edit=1 @>
						<cell #=data>?</cell>
						<cell #=data>?</cell>
						<cell #=menu>?</cell>
					</li>
				`);
			nani.render();
		}
	}
};
```
