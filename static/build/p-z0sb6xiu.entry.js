import{r as s,h as a}from"./p-3278c467.js";import{U as e}from"./p-683f8e74.js";const t=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];class l{constructor(a){s(this,a),this.alarms=[],this.componentDidLoad=async()=>{const s=await e.get("alarms.json");this.alarms=e.parseAlarms(s.data)}}render(){const s=this.alarms.sort((s,a)=>a.id-s.id).map(s=>{const e=s.hour<12?"AM":"PM";let l="PM"===e?s.hour-12:s.hour;0==l&&(l=12);const i=s.min<10?`0${s.min}`:s.min,r=t.map((e,t)=>a("div",{class:`day ${s.days[t]?"active":""}`},e)),n=a("div",{class:"weekdays"},r),c=a("div",{class:"frequency"},"Every ",s.freq," days"),d=s.freq?c:n;return a("li",{class:"item"},a("div",{class:"switch"},a("toggle-switch",{vertical:!0,frozen:!0,enabled:s.enabled})),a("div",{class:"time"},a("span",{class:"hour"},l),a("span",{class:"colon"},":"),a("span",{class:"minute"},i),a("span",{class:"meridian"},e)),a("div",{class:"days"},d))});return a("div",{class:"list"},a("nav-header",null),a("h1",null,"Nope."),a("h2",null,"The Box is LOCKED."),a("h2",null,"Will UNLOCK at these times."),a("ul",{class:"items"},s))}static get style(){return".list{max-width:640px;margin:0 auto}.item{display:grid;grid-template-columns:35px 210px 1fr 80px;grid-gap:8px;padding:12px;background-color:#eee;margin:8px 0;border-radius:6px;-webkit-box-shadow:inset 0 0 15px #444,1px 3px 6px rgba(0,0,0,.6);box-shadow:inset 0 0 15px #444,1px 3px 6px rgba(0,0,0,.6)}.switch{display:-ms-flexbox;display:flex;-ms-flex-align:center;align-items:center}.enable p{margin:0}h1{font-size:35px;margin-bottom:0}h1,h2{color:#fff;font-weight:100;text-align:center}h2{font-size:18px;margin:20px 0 10px 0}ul{list-style:none;padding:0}a{text-decoration:none}.time{display:-ms-flexbox;display:flex;-ms-flex-align:end;align-items:flex-end;-ms-flex-pack:end;justify-content:flex-end;font-size:55px;line-height:55px}.meridian{color:#999;padding:0 5px;margin:0 5px;font-size:40px;text-transform:uppercase}.weekdays{display:block;font-size:.8em}.day{border-radius:11px;display:inline-block;padding:6px 7px;margin:0 5px 3px 0}.weekdays{color:#999}.frequency{font-size:45px;line-height:55px}.active{border-color:#444;background-color:#666;color:#fff}.buttons{display:-ms-flexbox;display:flex;-ms-flex-pack:distribute;justify-content:space-around}\@media (max-width:768px){.list{margin:0 4px}.time{-ms-flex-pack:start;justify-content:flex-start;-ms-flex-align:start;align-items:flex-start;line-height:24px;font-size:24px}.frequency{font-size:20px;line-height:20px}.meridian{font-size:inherit}.switch{-ms-flex-align:start;align-items:flex-start;grid-row:1/3}.item{position:relative;display:grid;grid-template-columns:34px 1fr;grid-gap:8px;padding:13px 12px}.weekdays{width:198px}.day{display:inline-block;padding:4px;margin:0 6px 0 0}.buttons{position:absolute;right:13px;top:12px;display:grid;grid-template-columns:1fr;grid-gap:4px}}"}}export{l as locked_page};