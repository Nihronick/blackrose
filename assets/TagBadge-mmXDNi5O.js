import{c,j as e,a as d,h,r as m,B as x}from"./index-By_55chJ.js";import{B as f}from"./badge-BTmLjVpi.js";import{I as g}from"./input-C61VEZmw.js";import{H as p}from"./hash-5BflUQxN.js";import{X as y}from"./x-CDpUHJFT.js";/**
 * @license lucide-react v1.14.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const k=[["path",{d:"M20 6 9 17l-5-5",key:"1gmf2c"}]],L=c("check",k);/**
 * @license lucide-react v1.14.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const b=[["path",{d:"m6 9 6 6 6-6",key:"qrunsl"}]],B=c("chevron-down",b);/**
 * @license lucide-react v1.14.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const j=[["path",{d:"M3 5h.01",key:"18ugdj"}],["path",{d:"M3 12h.01",key:"nlz23k"}],["path",{d:"M3 19h.01",key:"noohij"}],["path",{d:"M8 5h13",key:"1pao27"}],["path",{d:"M8 12h13",key:"1za7za"}],["path",{d:"M8 19h13",key:"m83p4d"}]],E=c("list",j);/**
 * @license lucide-react v1.14.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const v=[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"M12 5v14",key:"s699le"}]],N=c("plus",v),u=({tag:t,onClick:o,onRemove:a,active:r,className:l})=>e.jsxs(f,{variant:r?"default":"secondary",className:d("cursor-pointer gap-1.5 rounded-lg border-border/30 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider transition-all active:scale-95",!r&&"bg-muted/50 hover:bg-muted text-muted-foreground",r&&"bg-primary text-primary-foreground shadow-sm shadow-primary/20",l),onClick:o?()=>{var n,s;(s=(n=h).light)==null||s.call(n),o(t)}:void 0,children:[e.jsx(p,{className:d("size-2.5 opacity-60",r&&"opacity-100")}),t,a&&e.jsx("button",{className:"ml-1 rounded-full p-0.5 hover:bg-white/20 transition-colors",onClick:n=>{n.stopPropagation(),a(t)},children:e.jsx(y,{className:"size-3"})})]}),I=({tags:t,onTagClick:o,className:a})=>!Array.isArray(t)||t.length===0?null:e.jsx("div",{className:d("flex flex-wrap gap-2",a),children:t.map(r=>e.jsx(u,{tag:r,onClick:o},r))}),T=({tags:t,onChange:o})=>{const[a,r]=m.useState(""),l=s=>{const i=s.trim().toLowerCase().replace(/\s+/g,"-").replace(/[^a-zа-яё0-9_-]/gi,"");!i||t.includes(i)||t.length>=20||(o([...t,i]),r(""))},n=s=>o(t.filter(i=>i!==s));return e.jsxs("div",{className:"flex flex-col gap-4 py-2",children:[e.jsx("div",{className:"flex flex-wrap gap-2",children:t.map(s=>e.jsx(u,{tag:s,onRemove:n,active:!0},s))}),e.jsxs("div",{className:"flex gap-2",children:[e.jsxs("div",{className:"relative flex-1 group/field",children:[e.jsx(p,{className:"absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within/field:text-primary"}),e.jsx(g,{className:"h-11 border-none bg-muted/50 pl-9 text-sm focus-visible:bg-background focus-visible:ring-2 focus-visible:ring-primary/20",placeholder:"Добавить тег...",value:a,onChange:s=>r(s.target.value),onKeyDown:s=>{(s.key==="Enter"||s.key===",")&&(s.preventDefault(),l(a))},maxLength:30})]}),e.jsx(x,{size:"icon",className:"h-11 w-11 shrink-0 rounded-xl",type:"button",onClick:()=>l(a),disabled:!a.trim(),children:e.jsx(N,{className:"size-5"})})]}),e.jsx("p",{className:"px-1 text-[10px] font-bold uppercase tracking-widest text-muted-foreground/40",children:"Enter или запятая · макс. 20 тегов"})]})};export{B as C,E as L,N as P,I as T,L as a,T as b};
//# sourceMappingURL=TagBadge-mmXDNi5O.js.map
