import{r as t,h as s}from"./p-3278c467.js";class e{constructor(s){t(this,s),this.readout="",this.setNumber=t=>{let s;if(this.new)this.setNew(!1),s=`${t}`;else{const e=`${this.readout}${t}`;s=e.length>this.maxDigits?e.substr(e.length-this.maxDigits):e}this.setReadout(s)}}render(){return s("div",{class:"number-pad"},s("button",{class:"button _7",onClick:()=>this.setNumber(7)},"7"),s("button",{class:"button _8",onClick:()=>this.setNumber(8)},"8"),s("button",{class:"button _9",onClick:()=>this.setNumber(9)},"9"),s("button",{class:"button _4",onClick:()=>this.setNumber(4)},"4"),s("button",{class:"button _5",onClick:()=>this.setNumber(5)},"5"),s("button",{class:"button _6",onClick:()=>this.setNumber(6)},"6"),s("button",{class:"button _1",onClick:()=>this.setNumber(1)},"1"),s("button",{class:"button _2",onClick:()=>this.setNumber(2)},"2"),s("button",{class:"button _3",onClick:()=>this.setNumber(3)},"3"),s("button",{class:"button back",onClick:()=>this.backspace()},s("img",{src:"/assets/images/backspace.svg"})),s("button",{class:"button _0",onClick:()=>this.setNumber(0)},"0"),s("button",{class:"button close",onClick:()=>this.close()},s("img",{src:"/assets/images/times.svg"})))}static get style(){return".number-pad{padding:20px 6px;display:grid;grid-template-columns:1fr 1fr 1fr;grid-gap:19px}.button{border-radius:6px;border:none;padding:12px 8px;font-size:26px;text-align:center;cursor:pointer;background-color:#fff;-webkit-box-shadow:inset 0 0 15px #444,1px 3px 6px rgba(0,0,0,.6);box-shadow:inset 0 0 15px #444,1px 3px 6px rgba(0,0,0,.6)}.button:hover{background-color:#ccc}.button:active{-webkit-box-shadow:inset 0 0 15px #444,1px 1px 1px rgba(0,0,0,.6);box-shadow:inset 0 0 15px #444,1px 1px 1px rgba(0,0,0,.6)}.back img,.close img{height:26px}.back,.close{display:-ms-flexbox;display:flex;-ms-flex-align:center;align-items:center;-ms-flex-pack:center;justify-content:center}"}}export{e as number_pad};