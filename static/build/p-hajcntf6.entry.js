import{r as t,h as s}from"./p-3278c467.js";const e=280,i=t=>t<10?"0"+t:""+t;class a{constructor(s){t(this,s),this.clockSize=300,this.byFives=!0}componentDidLoad(){this.hourHand=document.querySelector(".hourHand")}handleMousemove(t){if(0===t.buttons)return;let s,a,h;const o=e/2;(s=Math.atan2(o-t.offsetY,o-t.offsetX)*(180/Math.PI)-90)<0&&(s+=360),this.deg=s,a=s/30,h=s/30*60%60,h=Math.round(h),a=Math.round(a),(h=Math.ceil(h/5*5))<0&&(h=0),a<=0&&(a=12);const r=isNaN(a)||0===a?"":i(a);let n=isNaN(h)?"":i(h);this.setAutoSet(!1),this.setReadout(`${r}${n}`)}watchHandler(t){this.deg=30*t}render(){let t;return t=Math.round(6*this.min),t=this.byFives?5*Math.ceil(t/5):Math.ceil(t),s("div",{class:"clock-face",onPointerMove:t=>this.handleMousemove(t)},s("div",{class:"hour3 hour"},"3"),s("div",{class:"hour6 hour"},"6"),s("div",{class:"hour9 hour"},"9"),s("div",{class:"hour12 hour"},"12"),s("div",{class:"marker oneseven"}),s("div",{class:"marker twoeight"}),s("div",{class:"marker fourten"}),s("div",{class:"marker fiveeleven"}),s("div",{class:"inner"},s("div",{class:"center"}),s("div",{class:"minuteHand",style:{transform:`rotate(${t}deg)`}}),s("div",{class:"hourHand",style:{transform:`rotate(${this.deg}deg)`}})))}static get watchers(){return{hour:["watchHandler"]}}static get style(){return".clock-face{position:relative;height:280px;width:280px;margin:20px auto;-webkit-box-shadow:inset -1px -1px 6px #222;box-shadow:inset -1px -1px 6px #222;background-color:#fff;border-radius:100%}.marker,.time-setter:after,.time-setter:before{content:\"\";position:absolute;width:24px;height:100%;z-index:0;left:50%;margin-left:-12px;top:0}.time-setter:after{-webkit-transform:rotate(90deg);transform:rotate(90deg)}.inner{position:relative;width:84%;height:84%;background:#fff;z-index:1;left:8%;top:8%}.center,.inner{border-radius:100%;pointer-events:none}.center{position:absolute;height:10px;width:10px;background-color:var(--color1);top:50%;left:50%;margin-left:-5px;margin-top:-5px;z-index:2}.hour{pointer-events:none;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none}.minuteHand{margin-top:-110px;height:110px;background-color:#000;-webkit-transform:rotate(15deg);transform:rotate(15deg);-webkit-transform-origin:50% 100%;transform-origin:50% 100%}.hourHand,.minuteHand{position:absolute;top:50%;left:50%;margin-left:-2px;width:4px;pointer-events:none}.hourHand{margin-top:-70px;height:70px;background-color:var(--color1);-webkit-transform:rotate(45deg);transform:rotate(45deg);-webkit-transform-origin:50% 100%;transform-origin:50% 100%}.hour3{margin-left:-12px;right:0;text-align:center}.hour3,.hour9{width:24px;height:24px;margin-top:-12px;font-size:20px;font-weight:900;position:absolute;top:50%;z-index:2}.hour9{left:5px}.hour6{margin-top:-12px;top:269px}.hour6,.hour12{width:24px;height:24px;margin-left:-12px;font-size:20px;font-weight:900;position:absolute;left:50%}.hour12{top:4px}.meridian{font-size:25px;line-height:25px;border-radius:6px;-webkit-box-shadow:1px 3px 6px rgba(0,0,0,.2),inset 0 0 3px #fff;box-shadow:1px 3px 6px rgba(0,0,0,.2),inset 0 0 3px #fff;display:inline;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;text-decoration:none;letter-spacing:2px;cursor:pointer;border:1px solid #444;color:#fff;padding:8px;outline:none;background:#444;font-weight:600;width:60px}.meridian,.text-input input{text-align:center}.marker{background:#444;width:6px;margin-left:-3px;pointer-events:none}.marker.oneseven{-moz-transform:rotate(30deg);-ms-transform:rotate(30deg);-webkit-transform:rotate(30deg);transform:rotate(30deg)}.marker.twoeight{-moz-transform:rotate(60deg);-ms-transform:rotate(60deg);-webkit-transform:rotate(60deg);transform:rotate(60deg)}.marker.fourten{-moz-transform:rotate(120deg);-ms-transform:rotate(120deg);-webkit-transform:rotate(120deg);transform:rotate(120deg)}.marker.fiveeleven{-moz-transform:rotate(150deg);-ms-transform:rotate(150deg);-webkit-transform:rotate(150deg);transform:rotate(150deg)}"}}class h{constructor(s){t(this,s)}render(){const t=isNaN(this.hour)||0===this.hour?"":this.hour;let e=isNaN(this.min)?"":this.min<10?"0"+this.min:""+this.min;return e=0===this.min&&0===this.hour?"":e,s("div",{class:"digital-time"},s("span",{class:"hour"},t),":",s("span",{class:"min"},e))}static get style(){return".digital-time{background-color:rgba(0,0,0,.3);-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;padding:8px;border-radius:6px;display:-ms-flexbox;display:flex;font-size:38px;-ms-flex-align:center;align-items:center;-ms-flex-pack:center;justify-content:center;color:#fff;font-family:monospace;cursor:pointer;border:4px solid #2c5cd6}.digital-time:hover{background-color:rgba(0,0,0,.2)}"}}class o{constructor(s){t(this,s)}onClick(t){this.selectedValue=t,this.buttonClick(t)}render(){const t=t=>t===this.selectedValue?"highlighted":"",e=this.buttons.map(e=>{const{value:i,label:a}=e;return s("div",{class:`button ${t(i)}`,onClick:()=>this.onClick(i)},a)});return s("div",{class:"radio-buttons"},e)}static get style(){return".radio-buttons{display:grid;grid-template-columns:1fr 1fr;height:63px;grid-gap:0;width:100%}.button{font-size:18px;-webkit-box-shadow:1px 3px 6px rgba(0,0,0,.2),inset 0 0 5px #999;box-shadow:1px 3px 6px rgba(0,0,0,.2),inset 0 0 5px #999;text-align:center;display:-ms-flexbox;display:flex;-ms-flex-pack:center;justify-content:center;-ms-flex-align:center;align-items:center;-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none;text-decoration:none;letter-spacing:1px;cursor:pointer;color:#fff;padding:4px 0;outline:none;background:#444;margin:0}.button:first-of-type{border-top-left-radius:6px;border-bottom-left-radius:6px}.button:last-of-type{border-top-right-radius:6px;border-bottom-right-radius:6px}.highlighted{background:var(--color1);-webkit-box-shadow:1px 3px 6px rgba(0,0,0,.2),inset 0 0 5px var(--color2);box-shadow:1px 3px 6px rgba(0,0,0,.2),inset 0 0 5px var(--color2)}"}}const r=1,n=0;class c{constructor(s){t(this,s),this.setAutoSet=()=>{},this.label="At this Time",this.readout=`${this.hour}${this.min}`,this.clockVisible=!0,this.new=!0,this.close=()=>{this.clockVisible=!0},this.backspace=()=>{const t=this.readout;if(void 0===t)return;const s=t.substring(0,t.length-1);s.length<=0?(this.close(),this.new=!0):(this.readout=s,this.new=!1),this.setTime(s)},this.setNew=t=>this.new=t,this.setReadout=t=>{this.readout=t,this.autoSet=!1,this.setTime(t)}}watchHandler(t){this.autoSet&&(this.hour=t.getHours(),this.min=t.getMinutes(),this.meridian=this.hour>12?r:n)}render(){const t=this.hour>12&&12===this.base?this.hour-12:this.hour,e=[{label:"AM",value:n},{label:"PM",value:r}];return s("div",{class:"time-setter"},s("div",{class:"top"},s("h2",null,this.label),s("digital-time",{hour:t,min:this.min,onClick:()=>{this.clockVisible=!1,this.new=!0}}),s("radio-buttons",{buttons:e,selectedValue:this.meridian,buttonClick:t=>{this.meridian=t}})),s("div",{class:"setters"},this.clockVisible?s("clock-face",{setReadout:this.setReadout,hour:this.hour,min:this.min,setAutoSet:this.setAutoSet}):s("number-pad",{maxDigits:4,backspace:this.backspace,close:this.close,new:this.new,setNew:this.setNew,setReadout:this.setReadout,readout:this.readout})))}static get watchers(){return{currentTime:["watchHandler"]}}static get style(){return".time-setter{display:-ms-flexbox;display:flex;-ms-flex-flow:column;flex-flow:column;-ms-flex-align:space-between;align-items:space-between;position:relative;padding:8px 4px 0 4px;min-width:350px}.top{display:grid;grid-template-columns:1fr 136px 1fr;grid-gap:12px}\@media (max-width:768px){.time-setter{min-width:0}.top{grid-template-columns:70px 130px 1fr;grid-gap:4px}}"}}export{a as clock_face,h as digital_time,o as radio_buttons,c as time_setter};