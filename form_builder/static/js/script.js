(function() {
	function getArray(col) {
		return Array.prototype.slice.call(col);
	}

	function file_clickHandler(fil) {
		fil.click();
	}

	function file_changeHandler(txt, fil) {
		txt.value = fil.files[0].name;
	}

	function toggleNewLogo(logo, group) {
		var file_group = group.querySelector(".file-group");

		if (logo.value == "new") {
			group.style.display = "block";
		}
		else {
			group.style.display = "none";
			file_group.children[0].value = "";
			file_group.children[2].value = null;
		}
	}

	function toProperCase(str) {
		return str[0].toUpperCase() + str.substr(1).toLowerCase();
	}
	
	function Item(num) {
		this.num = num.toString();
	}
	
	Item.prototype.getItemGroup = function(itm) {
		var div = document.createElement("div");
		div.id  = "item-group-" + itm.num;
		div.appendChild(itm.getItemTitle("title"));
		div.appendChild(itm.getItemPrice("price"));
		div.appendChild(itm.getItemImage("image"))
		div.appendChild(itm.getItemSizes("sizes"));
		
		return div;
	}
	
	Item.prototype.getItemTitle = function(str) {
		var div       = document.createElement("div");
		div.className = "form-group";

		var lbl = document.createElement("label");
		lbl.htmlFor   = "item-" + str + "-" + this.num;
		lbl.innerHTML = "Item " + this.num + " " + toProperCase(str) + ":";

		var txt = document.createElement("input");
		txt.type = "text";
		txt.id   = lbl.htmlFor;
		txt.name = txt.id;

		div.appendChild(lbl);
		div.appendChild(txt);

		return div;
	}
	
	Item.prototype.getItemPrice = function(str) {
		return this.getItemTitle(str);
	}
	
	Item.prototype.getItemImage = function(str) {
		var div       = document.createElement("div");
		div.className = "form-group";

		var lbl       = document.createElement("label");
		lbl.htmlFor   = "item-" + str + "-text-" + this.num;
		lbl.innerHTML = "Item " + this.num + " " + toProperCase(str) + ":";

		var grp       = document.createElement("div");
		grp.className = "file-group";

		var txt      = document.createElement("input");
		txt.type     = "text";
		txt.id       = lbl.htmlFor;
		txt.name     = txt.id;
		txt.readOnly = true;

		var btn       = document.createElement("button");
		btn.type      = "button";
		btn.id        = "item-image-button-" + this.num;
		btn.name      = btn.id;
		btn.className = "fas fa-caret-square-up";

		var fil    = document.createElement("input");
		fil.type   = "file";
		fil.id     = "item-image-file-" + this.num;
		fil.name   = fil.id;
		fil.accept = "image/gif, image/jpeg, image/png";

		btn.addEventListener("click",  file_clickHandler.bind(this, fil));
		fil.addEventListener("change", file_changeHandler.bind(this, txt, fil));

		grp.appendChild(txt);
		grp.appendChild(btn);
		grp.appendChild(fil);

		div.appendChild(lbl);
		div.appendChild(grp);

		return div;
	}
	
	Item.prototype.getItemSizes = function(str) {
		var div       = document.createElement("div");
		div.className = "form-group";

		var lbl       = document.createElement("label");
		lbl.htmlFor   = "item-" + str + "-" + this.num;
		lbl.innerHTML = "Item " + this.num + " " + toProperCase(str) + ":";

		var txt         = document.createElement("textarea");
		txt.id          = lbl.htmlFor;
		txt.name        = txt.id;
		txt.placeholder = "(enter each size on separate line)";

		div.appendChild(lbl);
		div.appendChild(txt);

		return div;
	}

	function displayItems(form, sel) {
		var groups       = document.querySelectorAll("[id^='item-group']");
		var groups_count = groups.length;
		var num          = Number(sel.value);

		while (groups_count > num) {
			form.removeChild(groups[groups_count-1]);
			groups_count--;
		}

		for (var i=groups_count+1; i<=num; i++) {
			var itm = new Item(i);
			form.insertBefore(itm.getItemGroup(itm), form.lastElementChild);
		}
	}
	
	function displayErrors(form, err) {
		var ul       = document.createElement("ul");
		var li       = document.createElement("li");
		ul.id        = "errors";
		li.innerHTML = "ERRORS:";
		ul.appendChild(li);
		
		err.forEach(function(e) {
			li = document.createElement("li");
			li.innerHTML = e;
			ul.appendChild(li);
		});
		
		if (err.length > 0) {
			var errors = document.getElementById("errors");
			
			if (errors) {
				form.replaceChild(ul, errors);
			}
			else {				
				var group_1 = document.querySelector(".form-group");
				
				if (group_1) {
					form.insertBefore(ul, group_1);
				}	
			}
			
			ul.scrollIntoView();
		}
	}
	
	function submitFormAjax(form, e)	{		
		e.preventDefault();
		
		var els = getArray(form.elements);
		var flt = function(el) {
			return el.name.indexOf("-button") < 0 && el.name.indexOf("-text") < 0 && el.type != "submit";
		};
		
		var fd = new FormData();
		
		els.filter(flt).forEach(function(el) {
			if (el.type == "radio" && !el.checked) {
				var val = fd.has(el.name) ? fd.get(el.name) : "";
				fd.set(el.name, val);
			}
			else if (el.type == "file" && el.files.length > 0) {
				fd.set(el.name, el.files[0], el.files[0].fileName);
			}
			else {
				fd.set(el.name, el.value);
			}
		});
				
		var xmlHttp = new XMLHttpRequest();
		
		xmlHttp.onreadystatechange = function() {
			if(xmlHttp.readyState == 4 && xmlHttp.status == 200) {
				var obj = JSON.parse(xmlHttp.responseText);
				
				if (obj.hasOwnProperty("url")) {
					location.href = obj.url;
				}
				else if (obj.hasOwnProperty("post")) {
					form.action = obj.post;
					form.submit();
				}
				else {
					displayErrors(form, obj);	
				}				
			}
		}
		
		xmlHttp.open("post", form.action);
		xmlHttp.setRequestHeader("X-Requested-With", "XMLHttpRequest");
		xmlHttp.send(fd);
	}
	
	function gotoPage(form, page, val, e) {
		e.preventDefault();
		
		page.value = val;
		form.submit();
	}
	
	function toggleNav(nav, icon) {
		var isClose = (icon.className.indexOf('exit-on') >= 0);
		var ul      = nav.firstElementChild;
		var lis     = getArray(ul.children).filter(function(el) {
			return el.tagName.toLowerCase() == "li";
		})
		
		var toggleItems = function(items, str) {
			items.forEach(function(item) {
				item.style.display = str;
			});
		}
		
		if (isClose) {
			nav.className  = "nav-off";
			ul.className   = "border-off";
			icon.className = "fas fa-bars exit-off";
			toggleItems(lis, "none");
		}
		else {
			nav.className  = "nav-on";
			ul.className   = "border-on";
			icon.className = "fas fa-times exit-on";
			toggleItems(lis, "block");
		}
		
		dimMenu(icon);
	}
	
	function dimMenu(icon) {
		isOff = (icon.className.indexOf("exit-off") >= 0);
		
		if (window.pageYOffset >= 150 && isOff) {
			icon.style.opacity = "0.3";
		}
		else {
			icon.style.opacity = "1";
		}
	}
	
	function events() {
		var form            = document.getElementById("form");
		var logo_new_group  = document.getElementById("logo-new-group");
		var logo_new_text   = document.getElementById("logo-new-text");
		var logo_new_button = document.getElementById("logo-new-button");
		var logo_new_file   = document.getElementById("logo-new-file");
		var for_sale        = document.getElementById("for-sale");
		var page_link       = document.querySelectorAll(".page-link");
		var page            = document.getElementById("page");
		var nav             = document.getElementById("nav");
		var exit            = document.getElementById("exit");

		if (logo_new_button && logo_new_file) {
			logo_new_button.addEventListener("click", file_clickHandler.bind(this, logo_new_file));
		}

		if (logo_new_text && logo_new_file) {
			logo_new_file.addEventListener("change", file_changeHandler.bind(this, logo_new_text, logo_new_file));
		}

		if (form) {
			var logo = form.elements.namedItem("logo");

			if (logo && logo_new_group) {
				getArray(logo).forEach(function(l) {
					l.addEventListener("click", toggleNewLogo.bind(this, logo, logo_new_group));
				});

				toggleNewLogo(logo, logo_new_group);
			}
			
			form.addEventListener("submit", submitFormAjax.bind(this, form));
		}

		if (for_sale) {
			for_sale.addEventListener("change", displayItems.bind(this, form, for_sale));
			
			for (var i=1; i<=Number(for_sale.value); i++) {
				var txt = document.getElementById("item-image-text-"+i.toString());
				var btn = document.getElementById("item-image-button-"+i.toString());
				var fil = document.getElementById("item-image-file-"+i.toString());

				if (btn && fil) {
					btn.addEventListener("click", file_clickHandler.bind(this, fil));
				}

				if (txt && fil) {
					fil.addEventListener("change", file_changeHandler.bind(this, txt, fil));
				} 
			}
			
			displayItems(form, for_sale);
		}
		
		if (page_link.length > 0 && page) {
			getArray(page_link).forEach(function(p) {
				p.addEventListener("click", gotoPage.bind(this, form, page, p.innerHTML));
			});
		}
		
		if (nav && exit) {
			exit.addEventListener("click", toggleNav.bind(this, nav, exit));
			window.addEventListener("scroll", dimMenu.bind(this, exit));
			toggleNav(nav, exit);
		}
	}
	
	events();
})();