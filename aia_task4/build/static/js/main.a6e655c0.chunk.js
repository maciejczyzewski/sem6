(this["webpackJsonpmy-app"]=this["webpackJsonpmy-app"]||[]).push([[0],[,,,,,,function(e,t,a){e.exports=a.p+"static/media/doge.6a2998cf.svg"},,,function(e,t,a){e.exports=a.p+"static/media/star-full.37ced0d0.svg"},function(e,t,a){e.exports=a.p+"static/media/star-empty.023a90fe.svg"},function(e,t,a){e.exports=a.p+"static/media/help.3d138fd1.svg"},function(e,t,a){e.exports=a(19)},,,,,function(e,t,a){},function(e,t,a){},function(e,t,a){"use strict";a.r(t);var n=a(0),l=a.n(n),s=a(8),o=a.n(s),r=(a(17),a(1)),i=a(2),c=a(5),u=a(3),m=a(4),d=(a(18),a(9)),h=a.n(d),p=a(10),g=a.n(p),v=a(11),f=a.n(v),E=a(6),b=a.n(E),O=[{idx:1,name:"Thermal Physics test tomorrow. Wish me luck.",desc:"#physicsmemes",image:"https://preview.redd.it/ogvvnpnmvji31.jpg?width=640&crop=smart&auto=webp&s=1c0d23d491b7ec45977a8068553ef39770a6bce0",rating:5,opacity:1},{idx:2,name:"Oof-size: large",desc:"#physicsmemes",image:"https://preview.redd.it/lsn1s3akgia41.jpg?width=640&crop=smart&auto=webp&s=2d88c1d549a8837a0437f5375536b4747e557747",rating:4,opacity:1},{idx:3,name:"High iq meme",desc:"#physicsmemes",image:"https://preview.redd.it/xkax2cyhtbf41.jpg?width=640&crop=smart&auto=webp&s=b9a5e758957bd390852b60d0c4eedeb3ad7a3d98",rating:1,opacity:1}];function k(e){return!!new RegExp("^(https?:\\/\\/)?((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|((\\d{1,3}\\.){3}\\d{1,3}))(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*(\\?[;&a-z\\d%_.~+=-]*)?(\\#[-a-z\\d_]*)?$","i").test(e)}var y=function(e){Object(m.a)(a,e);var t=Object(u.a)(a);function a(){var e;Object(r.a)(this,a);for(var n=arguments.length,l=new Array(n),s=0;s<n;s++)l[s]=arguments[s];return(e=t.call.apply(t,[this].concat(l))).handleClick=function(){console.log("this is:",Object(c.a)(e)),e.props.handle(Object(c.a)(e))},e}return Object(i.a)(a,[{key:"render",value:function(){return void 0===this.props.toggle?l.a.createElement("button",{className:"button",onClick:this.handleClick},this.props.name):this.props.toggle?l.a.createElement("button",{className:"button",onClick:this.handleClick},this.props.name," ",l.a.createElement("i",{className:"icon icon-arrow-down"})):l.a.createElement("button",{className:"button",onClick:this.handleClick},this.props.name," ",l.a.createElement("i",{className:"icon icon-arrow-up"}))}}]),a}(n.Component),C=function(e){Object(m.a)(a,e);var t=Object(u.a)(a);function a(e){var n;return Object(r.a)(this,a),(n=t.call(this,e)).handleClick=function(){console.log("HELLO!",n.state.showModal),n.setState((function(e){return{showModal:!n.state.showModal}}))},n.state={showModal:!1},n}return Object(i.a)(a,[{key:"render",value:function(){return l.a.createElement("span",null,l.a.createElement("button",{className:"button help",onClick:this.handleClick},l.a.createElement("img",{src:f.a,alt:"help"})),l.a.createElement("div",{className:"modal "+(this.state.showModal?"active":"")},l.a.createElement("a",{href:"#close",className:"modal-overlay","aria-label":"Close",onClick:this.handleClick}),l.a.createElement("div",{className:"modal-container"},l.a.createElement("div",{className:"modal-header"},l.a.createElement("a",{href:"#close",className:"btn btn-clear float-right","aria-label":"Close",onClick:this.handleClick}),l.a.createElement("div",{className:"modal-title h5"},"Help")),l.a.createElement("div",{className:"modal-body"},l.a.createElement("div",{className:"content columns"},l.a.createElement("div",{className:"column col-6"},l.a.createElement("b",null,"Usage"),l.a.createElement("p",null,"Memes can be saved by using button"," ",l.a.createElement("kbd",null,"add"),", ",l.a.createElement("kbd",null,"ctrl+v")," or"," ",l.a.createElement("kbd",null,"drag&drop"),"."),l.a.createElement("b",null,"Edit"),l.a.createElement("p",null,"Click on place which you want to edit (there is possibility to change:"," ",l.a.createElement("i",null,"title"),", ",l.a.createElement("i",null,"description"),","," ",l.a.createElement("i",null,"image url"),").")),l.a.createElement("div",{className:"column col-6"},l.a.createElement("b",null,"Commands"),l.a.createElement("ul",null,l.a.createElement("li",null,l.a.createElement("mark",null,"/demo")," to restore default memes for presentation purpose"),l.a.createElement("li",null,l.a.createElement("mark",null,"/clear")," to remove all memes from your local history")),l.a.createElement("i",null,"(write commands in search area)")))),l.a.createElement("div",{className:"modal-footer"},"Maciej A. Czyzewski"))))}}]),a}(n.Component),j=function(e){Object(m.a)(a,e);var t=Object(u.a)(a);function a(e){var n;Object(r.a)(this,a),(n=t.call(this,e)).handleClick=function(){!0===n.state.isToggleOn&&n.setState((function(e){return{isToggleOn:!1}}))},n.onBlur=function(){n.setState({isToggleOn:!0})};var l=n.props.data[n.props.idx][n.props.name];return n.state={isToggleOn:!0,value:l,isDefault:"Description"===l||"Title"===l},n}return Object(i.a)(a,[{key:"onInputChange",value:function(e){this.props.data[this.props.idx][this.props.name]=e,this.setState((function(t){return{value:e,isDefault:"Description"===e||"Title"===e}}))}},{key:"modifier",value:function(){return l.a.createElement("p",null,this.state.value)}},{key:"render",value:function(){var e=this;return this.state.isToggleOn?l.a.createElement("div",{className:"column "+this.props.bonusClass+" "+(this.state.isDefault?"bg-warning":""),onClick:this.handleClick},this.modifier()):l.a.createElement("div",{className:"column "+this.props.bonusClass+" "+(this.state.isDefault?"bg-warning":""),onClick:this.handleClick},l.a.createElement("input",{ref:function(e){return e&&e.focus()},onChange:function(t){return e.onInputChange(t.target.value)},onBlur:this.onBlur,type:"text",className:"button form-input",value:this.state.value}))}}]),a}(n.Component),w=function(e){Object(m.a)(a,e);var t=Object(u.a)(a);function a(){return Object(r.a)(this,a),t.apply(this,arguments)}return Object(i.a)(a,[{key:"modifier",value:function(){return l.a.createElement("h1",null,this.state.value)}}]),a}(j),N=function(e){Object(m.a)(a,e);var t=Object(u.a)(a);function a(){return Object(r.a)(this,a),t.apply(this,arguments)}return Object(i.a)(a,[{key:"modifier",value:function(){return l.a.createElement("img",{className:"meme",src:this.state.value,alt:""})}}]),a}(j),x=function(e){Object(m.a)(a,e);var t=Object(u.a)(a);function a(){var e;Object(r.a)(this,a);for(var n=arguments.length,l=new Array(n),s=0;s<n;s++)l[s]=arguments[s];return(e=t.call.apply(t,[this].concat(l))).handleClick=function(){console.log("CLICK",e.props.rate),e.props.parent.handleClick(e.props.rate)},e.handleHover=function(){console.log("HOVER",e.props.rate),e.props.parent.handleHover(e.props.rate)},e.handleOut=function(){console.log("OUT",e.props.rate),e.props.parent.handleOut(e.props.rate)},e}return Object(i.a)(a,[{key:"render",value:function(){return l.a.createElement("img",{src:this.props.type,className:"star",alt:"star",onClick:this.handleClick,onMouseOver:this.handleHover,onMouseOut:this.handleOut})}}]),a}(n.Component),S=function(e){Object(m.a)(a,e);var t=Object(u.a)(a);function a(e){var n;Object(r.a)(this,a),(n=t.call(this,e)).handleClick=function(e){console.log("PARENT CLICK",e),isFinite(String(e))&&(n.setState({value:e}),n.props.data[n.props.idx].rating=e)},n.handleHover=function(e){console.log("PARENT HOVER",e),n.setState({fakeValue:e})},n.handleOut=function(e){console.log("PARENT OUT",e,n.state.value),n.setState({fakeValue:n.state.value})};var l=n.props.data[n.props.idx][n.props.name];return n.state={isToggleOn:!0,value:l,isDefault:"?"===l,fakeValue:l},n}return Object(i.a)(a,[{key:"generate",value:function(e){var t,a=[];for(t=1;t<=e;t++)a.push(l.a.createElement(x,{key:t,rate:t,type:h.a,parent:this}));for(t=1;t<=5-e;t++)a.push(l.a.createElement(x,{key:e+t,rate:e+t,type:g.a,parent:this}));return a}},{key:"modifier",value:function(){return l.a.createElement("div",{className:"stars-view"},this.generate(this.state.fakeValue),l.a.createElement("small",null,this.state.value))}}]),a}(j),T=function(e){Object(m.a)(a,e);var t=Object(u.a)(a);function a(){return Object(r.a)(this,a),t.apply(this,arguments)}return Object(i.a)(a,[{key:"render",value:function(){return l.a.createElement("div",{className:"column"},l.a.createElement(y,{name:"delete",handle:this.props.handle}))}}]),a}(n.Component),D=function(e){Object(m.a)(a,e);var t=Object(u.a)(a);function a(e){var n;return Object(r.a)(this,a),(n=t.call(this,e)).handleClick=function(){console.log("DELETE this is:",Object(c.a)(n)),n.props.parent.delete(n.props.data[n.props.idx].idx)},console.log(n.props.parent),n}return Object(i.a)(a,[{key:"render",value:function(){return l.a.createElement("div",{className:"row columns col-gapless "+(0===this.props.data[this.props.idx].opacity?"bg-shadow":"")},l.a.createElement(N,{idx:this.props.idx,name:"image",data:this.props.data,bonusClass:"meme"})," ",l.a.createElement("div",{className:"column info"},l.a.createElement(w,{idx:this.props.idx,name:"name",data:this.props.data})," ",l.a.createElement(j,{idx:this.props.idx,name:"desc",data:this.props.data})," ",l.a.createElement(S,{idx:this.props.idx,name:"rating",data:this.props.data})," ",l.a.createElement(T,{handle:this.handleClick})))}}]),a}(n.Component),I=function(e){Object(m.a)(a,e);var t=Object(u.a)(a);function a(e){var n;Object(r.a)(this,a),(n=t.call(this,e)).handleDragOver=function(e){var t=e;t.stopPropagation(),t.preventDefault(),console.log("OMG WE HAVE IT--\x3e",t);var a=t.dataTransfer.getData("text/html");if(""!==a){console.log("FIND!!!");var l=/src="?([^"\s]+)"?\s*/.exec(a);console.log(a),l[1]=l[1].replace(/&amp;/g,"&"),console.log("-----\x3e",l[1]),n.new(l[1])}},n.handlePaste=function(e){var t=e.clipboardData.getData("Text");k(t)&&n.new(t)};var l=[],s="",o=null,i=null;try{o=JSON.parse(localStorage.getItem("data")),i=localStorage.getItem("search")}catch(c){console.log("ERROR",c)}return l=null!==o?o:O,null!==i&&(s=i),n.state={data:l,isToggleOn:!0,inputValue:s},n}return Object(i.a)(a,[{key:"componentDidMount",value:function(){console.log("STARTING");var e=setInterval(this.checkpoint.bind(this),3e3);this.setState({intervalId:e})}},{key:"componentWillUnmount",value:function(){clearInterval(this.state.intervalId)}},{key:"generate",value:function(){for(var e=[],t=0;t<this.state.data.length;t++)e.push(l.a.createElement(D,{idx:t,key:this.state.data[t].name+this.state.data[t].idx,data:this.state.data,parent:this}));return e}},{key:"checkpoint",value:function(){console.log("SAVING FOR LATER!"),console.log("DEBUG",this.state.data),localStorage.setItem("search",this.state.inputValue),localStorage.setItem("data",JSON.stringify(this.state.data))}},{key:"new",value:function(e){console.log("new player!");var t=this.state.data,a=Math.random(),n="https://picsum.photos/400/300/?random=".concat(a);k(e)&&(n=e),t.unshift({idx:a,name:"Title",desc:"Description",image:n,rating:0,opacity:1}),this.setState({data:t})}},{key:"delete",value:function(e){console.log("PARENT DELETE",e);var t=this.state.data,a=t.map((function(e){return e.idx})).indexOf(e);console.log("YEAY",t),delete t[a],t=t.filter(Boolean),console.log("YEAY",t),this.setState({data:t})}},{key:"search",value:function(){var e=this.state.inputValue;console.log("SEARHC",e);for(var t=[],a=[],n=0;n<this.state.data.length;n++){var l=this.state.data[n];l.name.includes(e)||l.desc.includes(e)?(l.opacity=1,t.push(l)):(l.opacity=0,a.push(l))}"/clear"===e?(console.log("CLEAR"),localStorage.clear(),this.setState({data:[]})):"/demo"===e?(console.log("DEMO"),this.setState({data:O})):(console.log("SEARHC2",e),this.setState({data:t.concat(a)}))}},{key:"sort",value:function(){console.log("SORT");var e=this.state.data;this.setState((function(e){return{isToggleOn:!e.isToggleOn}})),e.sort((function(e,t){return e.rating-t.rating})),this.state.isToggleOn&&(e=e.reverse()),this.setState({data:e})}},{key:"updateInputValue",value:function(e){var t=this;console.log(),this.setState({inputValue:e},(function(){t.search()}))}},{key:"render",value:function(){var e=this;return l.a.createElement("div",{className:"App container",onDragOver:this.handleDragOver,onDrop:this.handleDragOver,onPaste:this.handlePaste},l.a.createElement("img",{className:"show-xl logo-small",src:b.a,alt:"doge territory"}),l.a.createElement("hr",{className:"separator"}),l.a.createElement("div",{className:"columns"},l.a.createElement("div",{className:"logo hide-xl column col-4"},l.a.createElement("h2",null,l.a.createElement("img",{src:b.a,alt:"doge territory"})," Meme Professor")),l.a.createElement("div",{className:"column col-xl-6 col-4"},l.a.createElement(y,{name:"add",handle:this.new.bind(this)})," ",l.a.createElement(y,{name:"sort by rating",handle:this.sort.bind(this),toggle:this.state.isToggleOn})," ",l.a.createElement(C,null)),l.a.createElement("div",{className:"column col-xl-6 col-4"},l.a.createElement("input",{type:"text",onChange:function(t){return e.updateInputValue(t.target.value)},value:this.state.inputValue,className:"button form-input",placeholder:"write here to search"}))),l.a.createElement("hr",{className:"separator"}),this.generate())}}]),a}(n.Component);Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));o.a.render(l.a.createElement(l.a.StrictMode,null,l.a.createElement(I,null)),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}))}],[[12,1,2]]]);
//# sourceMappingURL=main.a6e655c0.chunk.js.map