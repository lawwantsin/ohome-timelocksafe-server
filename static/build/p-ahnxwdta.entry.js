import{r as s,h as t}from"./p-3278c467.js";import{U as e}from"./p-51b2ba9a.js";class a{constructor(t){s(this,t),this.componentDidLoad=async()=>{await this.getLogs()},this.getLogs=async()=>{const s=await e.get("logs.json"),t=await s.json();s.ok?this.info=t.data:this.serverMsg=t.message}}render(){if(this.info)return t("div",{class:"logs"},t("server-notice",{message:this.serverMsg}),t("h1",null,"Logs"),t("div",{class:"inner"},t("div",{class:"scrollable"},t("pre",null,this.info))))}static get style(){return".logs{margin-bottom:60px}h1{font-weight:100;text-align:center;color:#fff;margin-top:60px}.inner{border-radius:8px;background:#eee;max-width:640px;margin:0 auto;color:#444;-webkit-box-shadow:2px 2px 4px rgba(0,0,0,.4);box-shadow:2px 2px 4px rgba(0,0,0,.4)}.scrollable{max-width:600px;margin:20px;overflow:auto}"}}export{a as logs_page};