import{r as s,h as t}from"./p-3278c467.js";import{P as i,D as e,U as h,F as a}from"./p-51b2ba9a.js";import{m as d}from"./p-349cadab.js";class o{constructor(t){s(this,t),this.hour=4,this.min=20,this.freq=1,this.base=12,this.meridian=i,this.days={},this.mode=e,this.dfn=0,this.hfn=0,this.serverMsg="",this.componentDidLoad=async()=>{const s=this.match.params.id;if(s){const t=await h.get("alarms",{id:s});this.hour=t.hour,this.min=t.min,this.freq=t.frequency}},this.setDFN=s=>{this.dfn=s},this.setHFN=s=>{this.hfn=s},this.setMode=s=>{this.mode=s},this.setTime=s=>{const{hour:t,min:i}=h.setTime(s,this.base);this.hour=t,this.min=i},this.setDay=s=>{this.days=Object.assign({},this.days,{[s]:!this.days[s]})},this.setAll=s=>{this.days=s?{0:!0,1:!0,2:!0,3:!0,4:!0,5:!0,6:!0}:{}},this.setMeridian=s=>{this.meridian=s},this.setFreq=s=>{this.freq=s},this.submitPayload=async()=>{const s=s=>encodeURIComponent(String(s)),{min:t,days:e,meridian:a}=this,d={h:s(a==i?this.hour+12:this.hour),m:s(t),mb:1,mf:1};["m","t","w","h","f","s","u"].map((s,t)=>{e[t]&&(d["dow"+s]=`${t}`)});const o=await h.get("edit.json",d),r=await o.json();o.ok?this.history.replace("/list"):this.serverMsg=r.message}}render(){const s=this.mode===a,i=d().add(this.dfn,"d").add(this.hfn,"h").format("dddd, MMMM Do YYYY, h:mm A"),e=t("h2",null,"Will open ",i);return t("div",{class:"edit"},t("nav-header",null),t("server-notice",{message:this.serverMsg}),t("h1",null,"Set Alarm"),t("h2",null,"I want to UNLOCK the box"),t("mode-selector",{onMode:this.setMode,selectedValue:this.mode}),s?e:"",t("div",{class:"hidden"},t("form-wizard",null,t("day-setter",{setFreq:this.setFreq,setDay:this.setDay,setAll:this.setAll,setDFN:this.setDFN,freq:this.freq,days:this.days,slot:"page1",dfn:this.dfn,mode:this.mode}),t("time-setter",{hour:this.hour,min:this.min,hfn:this.hfn,base:this.base,meridian:this.meridian,setMeridian:this.setMeridian,setTime:this.setTime,setHFN:this.setHFN,slot:"page2",mode:this.mode}))),t("post-button",{onClick:()=>this.submitPayload()},"Save"))}static get style(){return".edit{max-width:920px;margin:0 auto}h1{font-size:35px;margin-bottom:0}h1,h2{color:#fff;font-weight:100;text-align:center}h2{font-size:18px;margin:20px 0 10px 0}"}}export{o as edit_page};