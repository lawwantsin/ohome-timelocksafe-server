import{r as t,h as e,g as s,c as o}from"./p-3278c467.js";import{m as i,a as n,s as r,b as a,c,g as l,d as h,e as u,f as p,h as d,i as f,j as m,k as g,l as y,n as b,o as T,p as w}from"./p-8f0955b7.js";import{A as P}from"./p-eb9a731e.js";class O{constructor(e){t(this,e)}render(){return e("div",null,e("div",{class:"spotbg"}),e("main",null,e("stencil-router",null,e("stencil-route-switch",{scrollTopOffset:0},e("stencil-route",{url:"/html",component:"home-page",exact:!0}),e("stencil-route",{url:"/html/setup",component:"setup-page"}),e("stencil-route",{url:"/html/login",component:"login-page"}),e("stencil-route",{url:"/html/locked",component:"locked-page"}),e("stencil-route",{url:"/html/register",component:"register-page"}),e("stencil-route",{url:"/html/list",component:"list-page"}),e("stencil-route",{url:"/html/detail",component:"detail-page"}),e("stencil-route",{url:"/html/edit/:id?",component:"edit-page"})))))}static get style(){return"h1{font-size:1.4rem;font-weight:500;color:#fff;padding:0 12px}.spotbg{position:fixed;top:0;left:0;bottom:0;right:0;z-index:-1;background:#333}"}}class v{constructor(e){t(this,e),this.group=null,this.match=null,this.componentProps={},this.exact=!1,this.scrollOnNextRender=!1,this.previousMatch=null}computeMatch(t){const e=null!=this.group||null!=this.el.parentElement&&"stencil-route-switch"===this.el.parentElement.tagName.toLowerCase();if(t&&!e)return this.previousMatch=this.match,this.match=i(t.pathname,{path:this.url,exact:this.exact,strict:!0})}async loadCompleted(){let t={};this.history&&this.history.location.hash?t={scrollToId:this.history.location.hash.substr(1)}:this.scrollTopOffset&&(t={scrollTopOffset:this.scrollTopOffset}),"function"==typeof this.componentUpdated?this.componentUpdated(t):this.match&&!n(this.match,this.previousMatch)&&this.routeViewsUpdated&&this.routeViewsUpdated(t)}async componentDidUpdate(){await this.loadCompleted()}async componentDidLoad(){await this.loadCompleted()}render(){if(!this.match||!this.history)return null;const t=Object.assign({},this.componentProps,{history:this.history,match:this.match});return this.routeRender?this.routeRender(Object.assign({},t,{component:this.component})):this.component?e(this.component,Object.assign({},t)):void 0}get el(){return s(this)}static get watchers(){return{location:["computeMatch"]}}static get style(){return"stencil-route.inactive{display:none}"}}P.injectProps(v,["location","history","historyType","routeViewsUpdated"]);const L=()=>((1e17*Math.random()).toString().match(/.{4}/g)||[]).join("-"),E=(t,e,s)=>i(t,{path:e,exact:s,strict:!0}),k=t=>"STENCIL-ROUTE"===t.tagName;class x{constructor(e){t(this,e),this.group=L(),this.subscribers=[],this.queue=o(this,"queue")}componentWillLoad(){null!=this.location&&this.regenerateSubscribers(this.location)}async regenerateSubscribers(t){if(null==t)return;let e=-1;if(this.subscribers=Array.prototype.slice.call(this.el.children).filter(k).map((s,o)=>{const i=E(t.pathname,s.url,s.exact);return i&&-1===e&&(e=o),{el:s,match:i}}),-1===e)return;if(this.activeIndex===e)return void(this.subscribers[e].el.match=this.subscribers[e].match);this.activeIndex=e;const s=this.subscribers[this.activeIndex];this.scrollTopOffset&&(s.el.scrollTopOffset=this.scrollTopOffset),s.el.group=this.group,s.el.match=s.match,s.el.componentUpdated=t=>{this.queue.write(()=>{this.subscribers.forEach((t,e)=>{if(t.el.componentUpdated=void 0,e===this.activeIndex)return t.el.style.display="";this.scrollTopOffset&&(t.el.scrollTopOffset=this.scrollTopOffset),t.el.group=this.group,t.el.match=null,t.el.style.display="none"})}),this.routeViewsUpdated&&this.routeViewsUpdated(Object.assign({scrollTopOffset:this.scrollTopOffset},t))}}render(){return e("slot",null)}get el(){return s(this)}static get watchers(){return{location:["regenerateSubscribers"]}}}P.injectProps(x,["location","routeViewsUpdated"]);const S=(t,...e)=>{t||console.warn(...e)},U=()=>{let t,e=[];return{setPrompt:e=>(S(null==t,"A history supports only one prompt at a time"),t=e,()=>{t===e&&(t=null)}),confirmTransitionTo:(e,s,o,i)=>{if(null!=t){const n="function"==typeof t?t(e,s):t;"string"==typeof n?"function"==typeof o?o(n,i):(S(!1,"A history needs a getUserConfirmation function in order to use a prompt message"),i(!0)):i(!1!==n)}else i(!0)},appendListener:t=>{let s=!0;const o=(...e)=>{s&&t(...e)};return e.push(o),()=>{s=!1,e=e.filter(t=>t!==o)}},notifyListeners:(...t)=>{e.forEach(e=>e(...t))}}},j=(t,e="scrollPositions")=>{let s=new Map;const o=(e,o)=>{if(s.set(e,o),r(t,"sessionStorage")){const e=[];s.forEach((t,s)=>{e.push([s,t])}),t.sessionStorage.setItem("scrollPositions",JSON.stringify(e))}};if(r(t,"sessionStorage")){const o=t.sessionStorage.getItem(e);s=o?new Map(JSON.parse(o)):s}return"scrollRestoration"in t.history&&(history.scrollRestoration="manual"),{set:o,get:t=>s.get(t),has:t=>s.has(t),capture:e=>{o(e,[t.scrollX,t.scrollY])}}},A={hashbang:{encodePath:t=>"!"===t.charAt(0)?t:"!/"+T(t),decodePath:t=>"!"===t.charAt(0)?t.substr(1):t},noslash:{encodePath:T,decodePath:u},slash:{encodePath:u,decodePath:u}},R=(t,e)=>{const s=0==t.pathname.indexOf(e)?"/"+t.pathname.slice(e.length):t.pathname;return Object.assign({},t,{pathname:s})},C={browser:(t,e={})=>{let s=!1;const o=t.history,i=t.location,n=t.navigator,r=a(t),b=!c(n),T=j(t),w=null!=e.forceRefresh&&e.forceRefresh,P=null!=e.getUserConfirmation?e.getUserConfirmation:l,O=null!=e.keyLength?e.keyLength:6,v=e.basename?h(u(e.basename)):"",L=()=>{try{return t.history.state||{}}catch(t){return{}}},E=t=>{t=t||{};const{key:e,state:s}=t,{pathname:o,search:n,hash:r}=i;let a=o+n+r;return S(!v||f(a,v),'You are attempting to use a basename on a page whose URL path does not begin with the basename. Expected path "'+a+'" to begin with "'+v+'".'),v&&(a=m(a,v)),p(a,s,e||d(O))},k=U(),x=t=>{T.capture(B.location.key),Object.assign(B,t),B.location.scrollPosition=T.get(B.location.key),B.length=o.length,k.notifyListeners(B.location,B.action)},A=t=>{y(n,t)||C(E(t.state))},R=()=>{C(E(L()))},C=t=>{if(s)s=!1,x();else{const e="POP";k.confirmTransitionTo(t,e,P,s=>{s?x({action:e,location:t}):H(t)})}},H=t=>{let e=V.indexOf(B.location.key),o=V.indexOf(t.key);-1===e&&(e=0),-1===o&&(o=0);const i=e-o;i&&(s=!0,Y(i))},I=E(L());let V=[I.key],M=0,_=!1;const q=t=>v+g(t),Y=t=>{o.go(t)},N=e=>{1===(M+=e)?(t.addEventListener("popstate",A),b&&t.addEventListener("hashchange",R)):0===M&&(t.removeEventListener("popstate",A),b&&t.removeEventListener("hashchange",R))},B={length:o.length,action:"POP",location:I,createHref:q,push:(t,e)=>{S(!("object"==typeof t&&void 0!==t.state&&void 0!==e),"You should avoid providing a 2nd state argument to push when the 1st argument is a location-like object that already has state; it is ignored");const s=p(t,e,d(O),B.location);k.confirmTransitionTo(s,"PUSH",P,t=>{if(!t)return;const e=q(s),{key:n,state:a}=s;if(r)if(o.pushState({key:n,state:a},"",e),w)i.href=e;else{const t=V.indexOf(B.location.key),e=V.slice(0,-1===t?0:t+1);e.push(s.key),V=e,x({action:"PUSH",location:s})}else S(void 0===a,"Browser history cannot push state in browsers that do not support HTML5 history"),i.href=e})},replace:(t,e)=>{S(!("object"==typeof t&&void 0!==t.state&&void 0!==e),"You should avoid providing a 2nd state argument to replace when the 1st argument is a location-like object that already has state; it is ignored");const s=p(t,e,d(O),B.location);k.confirmTransitionTo(s,"REPLACE",P,t=>{if(!t)return;const e=q(s),{key:n,state:a}=s;if(r)if(o.replaceState({key:n,state:a},"",e),w)i.replace(e);else{const t=V.indexOf(B.location.key);-1!==t&&(V[t]=s.key),x({action:"REPLACE",location:s})}else S(void 0===a,"Browser history cannot replace state in browsers that do not support HTML5 history"),i.replace(e)})},go:Y,goBack:()=>Y(-1),goForward:()=>Y(1),block:(t="")=>{const e=k.setPrompt(t);return _||(N(1),_=!0),()=>(_&&(_=!1,N(-1)),e())},listen:t=>{const e=k.appendListener(t);return N(1),()=>{N(-1),e()}},win:t};return B},hash:(t,e={})=>{let s=!1,o=null,i=0,n=!1;const r=t.location,a=t.history,c=b(t.navigator),y=null!=e.keyLength?e.keyLength:6,{getUserConfirmation:T=l,hashType:P="slash"}=e,O=e.basename?h(u(e.basename)):"",{encodePath:v,decodePath:L}=A[P],E=()=>{const t=r.href,e=t.indexOf("#");return-1===e?"":t.substring(e+1)},k=t=>{const e=r.href.indexOf("#");r.replace(r.href.slice(0,e>=0?e:0)+"#"+t)},x=()=>{let t=L(E());return S(!O||f(t,O),'You are attempting to use a basename on a page whose URL path does not begin with the basename. Expected path "'+t+'" to begin with "'+O+'".'),O&&(t=m(t,O)),p(t,void 0,d(y))},j=U(),R=t=>{Object.assign(B,t),B.length=a.length,j.notifyListeners(B.location,B.action)},C=()=>{const t=E(),e=v(t);if(t!==e)k(e);else{const t=x(),e=B.location;if(!s&&w(e,t))return;if(o===g(t))return;o=null,H(t)}},H=t=>{if(s)s=!1,R();else{const e="POP";j.confirmTransitionTo(t,e,T,s=>{s?R({action:e,location:t}):I(t)})}},I=t=>{let e=q.lastIndexOf(g(B.location)),o=q.lastIndexOf(g(t));-1===e&&(e=0),-1===o&&(o=0);const i=e-o;i&&(s=!0,Y(i))},V=E(),M=v(V);V!==M&&k(M);const _=x();let q=[g(_)];const Y=t=>{S(c,"Hash history go(n) causes a full page reload in this browser"),a.go(t)},N=(t,e)=>{1===(i+=e)?t.addEventListener("hashchange",C):0===i&&t.removeEventListener("hashchange",C)},B={length:a.length,action:"POP",location:_,createHref:t=>"#"+v(O+g(t)),push:(t,e)=>{S(void 0===e,"Hash history cannot push state; it is ignored");const s=p(t,void 0,d(y),B.location);j.confirmTransitionTo(s,"PUSH",T,t=>{if(!t)return;const e=g(s),i=v(O+e);if(E()!==i){o=e,(t=>r.hash=t)(i);const t=q.lastIndexOf(g(B.location)),n=q.slice(0,-1===t?0:t+1);n.push(e),q=n,R({action:"PUSH",location:s})}else S(!1,"Hash history cannot PUSH the same path; a new entry will not be added to the history stack"),R()})},replace:(t,e)=>{S(void 0===e,"Hash history cannot replace state; it is ignored");const s=p(t,void 0,d(y),B.location);j.confirmTransitionTo(s,"REPLACE",T,t=>{if(!t)return;const e=g(s),i=v(O+e);E()!==i&&(o=e,k(i));const n=q.indexOf(g(B.location));-1!==n&&(q[n]=e),R({action:"REPLACE",location:s})})},go:Y,goBack:()=>Y(-1),goForward:()=>Y(1),block:(e="")=>{const s=j.setPrompt(e);return n||(N(t,1),n=!0),()=>(n&&(n=!1,N(t,-1)),s())},listen:e=>{const s=j.appendListener(e);return N(t,1),()=>{N(t,-1),s()}},win:t};return B}};class H{constructor(e){t(this,e),this.root="/",this.historyType="browser",this.titleSuffix="",this.routeViewsUpdated=(t={})=>{if(this.history&&t.scrollToId&&"browser"===this.historyType){const e=this.history.win.document.getElementById(t.scrollToId);if(e)return e.scrollIntoView()}this.scrollTo(t.scrollTopOffset||this.scrollTopOffset)},this.isServer=o(this,"isServer"),this.queue=o(this,"queue")}componentWillLoad(){this.history=C[this.historyType](this.el.ownerDocument.defaultView),this.history.listen(t=>{t=R(t,this.root),this.location=t}),this.location=R(this.history.location,this.root)}scrollTo(t){const e=this.history;if(null!=t&&!this.isServer&&e)return"POP"===e.action&&Array.isArray(e.location.scrollPosition)?this.queue.write(()=>{e&&e.location&&Array.isArray(e.location.scrollPosition)&&e.win.scrollTo(e.location.scrollPosition[0],e.location.scrollPosition[1])}):this.queue.write(()=>{e.win.scrollTo(0,t)})}render(){if(this.location&&this.history)return e(P.Provider,{state:{historyType:this.historyType,location:this.location,titleSuffix:this.titleSuffix,root:this.root,history:this.history,routeViewsUpdated:this.routeViewsUpdated}},e("slot",null))}get el(){return s(this)}}export{O as app_root,v as stencil_route,x as stencil_route_switch,H as stencil_router};