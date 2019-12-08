var __awaiter=this&&this.__awaiter||function(e,t,n,r){return new(n||(n=Promise))(function(i,o){function s(e){try{u(r.next(e))}catch(e){o(e)}}function a(e){try{u(r["throw"](e))}catch(e){o(e)}}function u(e){e.done?i(e.value):new n(function(t){t(e.value)}).then(s,a)}u((r=r.apply(e,t||[])).next())})};var __generator=this&&this.__generator||function(e,t){var n={label:0,sent:function(){if(o[0]&1)throw o[1];return o[1]},trys:[],ops:[]},r,i,o,s;return s={next:a(0),throw:a(1),return:a(2)},typeof Symbol==="function"&&(s[Symbol.iterator]=function(){return this}),s;function a(e){return function(t){return u([e,t])}}function u(s){if(r)throw new TypeError("Generator is already executing.");while(n)try{if(r=1,i&&(o=s[0]&2?i["return"]:s[0]?i["throw"]||((o=i["return"])&&o.call(i),0):i.next)&&!(o=o.call(i,s[1])).done)return o;if(i=0,o)s=[s[0]&2,o.value];switch(s[0]){case 0:case 1:o=s;break;case 4:n.label++;return{value:s[1],done:false};case 5:n.label++;i=s[1];s=[0];continue;case 7:s=n.ops.pop();n.trys.pop();continue;default:if(!(o=n.trys,o=o.length>0&&o[o.length-1])&&(s[0]===6||s[0]===2)){n=0;continue}if(s[0]===3&&(!o||s[1]>o[0]&&s[1]<o[3])){n.label=s[1];break}if(s[0]===6&&n.label<o[1]){n.label=o[1];o=s;break}if(o&&n.label<o[2]){n.label=o[2];n.ops.push(s);break}if(o[2])n.ops.pop();n.trys.pop();continue}s=t.call(e,n)}catch(e){s=[6,e];i=0}finally{r=o=0}if(s[0]&5)throw s[1];return{value:s[0]?s[1]:void 0,done:true}}};System.register(["./p-e28de766.system.js","./p-5a8f6e15.system.js"],function(e){"use strict";var t,n,r;return{setters:[function(e){t=e.r;n=e.h},function(e){r=e.U}],execute:function(){var i=function(){function e(e){var n=this;t(this,e);this.componentDidLoad=function(){return __awaiter(n,void 0,void 0,function(){return __generator(this,function(e){switch(e.label){case 0:return[4,this.getLogs()];case 1:e.sent();return[2]}})})};this.getLogs=function(){return __awaiter(n,void 0,void 0,function(){var e,t;return __generator(this,function(n){switch(n.label){case 0:return[4,r.get("logs.json")];case 1:e=n.sent();return[4,e.json()];case 2:t=n.sent();if(e.ok){this.info=t.data}else{this.serverMsg=t.message}return[2]}})})}}e.prototype.render=function(){if(!this.info)return;return n("div",{class:"logs"},n("server-notice",{message:this.serverMsg}),n("h1",null,"Logs"),n("div",{class:"inner"},n("div",{class:"scrollable"},n("pre",null,this.info))))};Object.defineProperty(e,"style",{get:function(){return".logs{margin-bottom:60px}h1{font-weight:100;text-align:center;color:#fff;margin-top:60px}.inner{border-radius:8px;background:#eee;max-width:640px;margin:0 auto;color:#444;-webkit-box-shadow:2px 2px 4px rgba(0,0,0,.4);box-shadow:2px 2px 4px rgba(0,0,0,.4)}.scrollable{max-width:600px;margin:20px;overflow:auto}"},enumerable:true,configurable:true});return e}();e("logs_page",i)}}});