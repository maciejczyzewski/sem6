/**
 * @license
 * Nani | Released under MIT license | Copyright Maciej A. Czyzewski
 */

// nani.min.js -> https://skalman.github.io/UglifyJS-online/
var nani = (function() {
	var defs = {
		'#': {},
		'!': {},
	};

	Element.prototype.remove = function() {
		this.parentElement.removeChild(this);
	}

	Element.prototype.set = function(key, val) {
		this.setAttribute("js-" + key, val);
	}

	Element.prototype.get = function(key) {
		return this.getAttribute("js-" + key);
	}

	function exists(e, key) {
		return null !== e.getAttribute(key);
	}

	function root(e) {
		return exists(e, "@") ? e : root(e.parentNode);
	}

	function _dynamic_input() {
		var onChange = function(e) {
			e.target.setAttribute('value', e.target.value);
		};
		Array.prototype.forEach.call(
			document.querySelectorAll('input'),
			function(inputs, i) {
				inputs.addEventListener('input', onChange, false);
			});
	}

	function render() {
		Array.prototype.forEach.call(
			document.querySelectorAll("[\\@]"),
			function(component, i) {
				component.setAttribute('id', "i" + i);

				Array.prototype.forEach.call(
					component.querySelectorAll("[\\#]"),
					function(el, i) {
						console.log("[render]", component, el);
						nani.defs['#'][el.getAttribute('#')](component, el);
					});
			});

		_dynamic_input();
	}

	function hooks() {
		Array.prototype.forEach.call(
			document.querySelectorAll('[\\!]'),
			function(_el, i) {
				_el.onclick = function(el) {
					var component = root(el.target);
					console.log("[hooks]", component, el.target);
					nani.defs['!'][el.target.getAttribute('!')](component, el.target);
					hooks();
				}
			});
	}

	document.addEventListener("DOMContentLoaded", function() {
		render(), hooks();
	});

	return {
		render: render,
		defs: defs,
	}
})();
