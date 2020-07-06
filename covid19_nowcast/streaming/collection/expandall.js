/*
@original-author FARLEY Jens-Ingo
@URL http://com.hemiola.com/bookmarklet/
@modified-by BETTINGER Matthieu
*/
let todo=6;
const EXPAND_POST=1;
const EXPAND_COMMENTS=2;
const EXPAND_REPLIES=4;
const EXPAND_XLAT=8;
const EXPAND_FILTER=16;
const WAIT_TIME=100;
const MAX_WAIT=20;
const END_DELAY=2.5;
const POST_ARTICLE="[aria-posinset][role=\"article\"]";
const VIDEO_ARTICLE="._6x84,[data-pagelet=\"TahoeRightRail\"]";
const FS_ARTICLE=".o36gj0jk:not([role=\"navigation\"])";
const NEW_ARTICLE=POST_ARTICLE+","+FS_ARTICLE+","+VIDEO_ARTICLE;
const POST_ACTION=".sjgh65i0 > div > div > div > div > div > span,.jifvfom9[role=\"button\"],.p24jkzn5";
const POST_ROOT=".userContentWrapper,.uiScrollableAreaContent,"+NEW_ARTICLE;
const RESPONSE_COUNTER="[aria-label][role=\"article\"]";
const CLASSIC_GET_CONTENT="._4sxc";
const CLASSIC_GET_REPLIES="._4sso";
const NEW_GET_CONTENT=".fv0vnmcu > .lrazzd5p";
const NEW_GET_COMMENTS=".bkfpd7mw .jklb3kyz .lrazzd5p";
const SHOW_COMMENTS="[data-ft=\u0027{\"tn\":\"O\"}\u0027]";
const SINGLE_COMMENT_AREA="._3w53,._6iiv,._7a9a";
const FILTER_ROOT=POST_ROOT+",.uiScrollableAreaContent,.uiStreamStory";
const FILTER_DONE="h6 ~ ul > li";
const FILTER_ATTR="data-ordering";
const FILTER_VALUE="RANKED_UNFILTERED";
const FILTER_NEW=".bp9cbjyn > .p8dawk7l[role=\"button\"]:not([aria-label]):not([aria-haspopup]):not(.jifvfom9):not(._4sxc)";
const CSS_LOGIN_STUFF="._5hn6, ._67m7, .generic_dialog_modal";
const BASE_SEE_MORE=".text_exposed_link .see_more_link_inner";
const EXPOSE_CONTENT=".text_exposed_link";
const CSS_SEE_MORE=".fss:not(._5shl)";
const SMN=".lrazzd5p[role=\"button\"]";
const SEE_MORE_NEW=POST_ARTICLE+" "+SMN+","+FS_ARTICLE+" "+SMN+","+VIDEO_ARTICLE+" "+SMN;
const _NONE="no-value";
const _COMMENTS="-comments";
const _REPLIES="-replies";
const SETTINGS_KEY="expand-all-todo";
function bind(obj,fn){
	return function(){
		fn.apply(obj,arguments);
	};
}
let Global=null;
if(!document.querySelectorAll("xx").forEach){
	Object.prototype.forEach=function(callback){
		let T;
		if(arguments.length>1){
			T=arguments[1];
		}
		let O=Object(this);
		let len=O.length>>>0;
		let k=0;
		while(k<len){
			if(k in O){
				callback.call(T,O[k],k,O);
			}k++;
		}
	};
}
function EscHandler(){
	this.abortNow=false;
	this.handler=bind(this,this.docKeyDown);
}
EscHandler.prototype.shouldAbort=function(){
	return this.abortNow;
};
EscHandler.prototype.abort=function(value){
	if(value&&!this.shouldAbort()&&!Global.cfg){
		Global.log("Aborting...");
	}
	this.abortNow=value;
};
EscHandler.prototype.on=function(){
	this.abortNow=false;
document.addEventListener("keydown",this.handler);
};
EscHandler.prototype.off=function(){
	this.abortNow=true;
document.removeEventListener("keydown",this.handler);
};
EscHandler.prototype.docKeyDown=function(e){
	if(e.keyCode==27){
		e.preventDefault();
		this.abort(true);
		if(Global.cfg){
			Session.trulyEnd();
		}
	}
};
function CfgHandler(){
	this.doConfig=false;
	this.handler=bind(this,this.docKeyDown);
}
CfgHandler.prototype.shouldConfig=function(){
	return this.doConfig;
};
CfgHandler.prototype.on=function(){
	this.doConfig=false;
	document.addEventListener("keydown",this.handler);
};
CfgHandler.prototype.off=function(){
	this.doConfig=true;
	document.removeEventListener("keydown",this.handler);
};
CfgHandler.prototype.docKeyDown=function(e){
	if(e.keyCode==="S".charCodeAt(0)){
		e.preventDefault();
		if(e.ctrlKey){
			Settings.removeKey(SETTINGS_KEY);
			Global.log("Will use default settings");
			return;
		}
		this.doConfig=true;
		if(Global.ending){
			CfgWindow.showIt();
		}
	}
};
function Settings(){
}
new Settings();
Settings.hasValue=function(value){
	return window.localStorage.getItem(value)!==null;
};
Settings.getValue=function(value,deflt){
	if(arguments.length<2){
		deflt=null;
	}
	if(!Settings.hasValue(value)){
		return deflt;
	}
	return window.localStorage.getItem(value);
};
Settings.getInt=function(value,deflt){
	if(arguments.length<2){
		deflt=-1;
	}
	return Number.parseInt(Settings.getValue(value,deflt),10);
};
Settings.getBoolean=function(value,deflt){
	if(arguments.length<2){
		deflt="false";
	}
	return Settings.getValue(value,""+deflt)=="true";
};
Settings.setValue=function(key,value){
	return window.localStorage.setItem(key,""+value);
};
Settings.removeKey=function(key){
	return window.localStorage.removeItem(key);
};
function BaseWindow(){
	this.id="base-window";
}
BaseWindow.prototype.show=function(){
	const WANT_W=300;
	const WANT_H=200;
	const sizer=document.querySelector("html");
	const w=sizer.clientWidth;
	const h=sizer.clientHeight;
	let x=0;
	if(w>WANT_W){
		x=(w-WANT_W)/2;
	}
	let y=0;
	if(h>WANT_H){
		y=(h-WANT_H)/3;
	}
	let div=document.createElement("div");
	div.id=this.id;
	div.style.direction="ltr";
	div.style.position="fixed";
	div.style.zIndex="999999";
	div.style.left=x+"px";
	div.style.width=WANT_W+"px";
	div.style.top=y+"px";
	div.style.height=WANT_H+"px";
	div.style.color="#fff";
	div.style.backgroundColor="#425f9c";
	document.body.insertAdjacentElement("afterbegin",div);
	this.create(div);
	this.init(div);
};
BaseWindow.prototype.create=function(div){
};
BaseWindow.prototype.init=function(div){
};
BaseWindow.prototype.hide=function(){
	document.querySelectorAll("#"+this.id).forEach(item=>document.body.removeChild(item));
};
function CfgWindow(){
	this.id="cfg-window";
}
CfgWindow.prototype=Object.create(BaseWindow.prototype);
CfgWindow.prototype.create=function(div){
	let node=document.createElement("p");
	div.appendChild(node);
	node.innerHTML="<i>Expand All</i> Settings";
	node.style.marginLeft="4px";
	node.style.fontWeight="bold";
	const boxes=[["In Classic Facebook, click <i>Continue Reading</i> links.",EXPAND_POST],["Expand comments.",EXPAND_COMMENTS],["Expand replies.",EXPAND_REPLIES],["Don't force <i>All Comments</i> filter.",EXPAND_FILTER]];
	boxes.forEach(item=>{
		node=document.createElement("p");
		div.appendChild(node);
		node.style.marginTop="2px";
		node.style.marginBottom="2px";
		let node2=document.createElement("input");
		node.appendChild(node2);
		node2.type="checkbox";
		node2.value=item[1];
		node2.style.marginLeft="15px";
		node2.style.cursor="pointer";
		node2=document.createElement("label");
		node.appendChild(node2);
		node2.innerHTML=item[0];
		node2.style.cursor="pointer";
		node2.style.paddingBottom="5px";
		node2.style.fontWeight="normal";
		node2.style.color="#fff";
	});
	node=document.createElement("div");
	div.appendChild(node);
	node.style.textAlign="center";
	let node2=document.createElement("button");
	node.appendChild(node2);
	node2.innerHTML="Done";
	node2.style.cursor="pointer";
	node2.addEventListener("click",Session.trulyEnd);
	div.addEventListener("CheckboxStateChange",CfgWindow.check);
	div.addEventListener("click",CfgWindow.check);
};
CfgWindow.check=function(e){
	let node=Dom.upThenDown(e.target,"p","input");
	if(node!=e.target){
		node.checked=!node.checked;
	}if(node.checked){
		todo|=Number.parseInt(node.value);
	}else{
		todo&=~Number.parseInt(node.value);
	}
	Settings.setValue(SETTINGS_KEY,todo);
};
CfgWindow.prototype.init=function(div){
	let boxes=div.querySelectorAll("input");
	if(boxes.length===4){
		boxes[0].checked=(todo&EXPAND_POST)!=0;
		boxes[1].checked=(todo&EXPAND_COMMENTS)!=0;
		boxes[2].checked=(todo&EXPAND_REPLIES)!=0;
		boxes[3].checked=(todo&EXPAND_FILTER)!=0;
	}
};
CfgWindow.showIt=function(){
	Global.logger.hide();
	Global.cfg=new CfgWindow();
	Global.cfg.show();
};
function LogWindow(){
	this.id="log-window";
	this.timeouts=0;
	this.phantoms=0;
	this.edit=null;
}
LogWindow.prototype=Object.create(BaseWindow.prototype);
LogWindow.prototype.create=function(div){
	this.edit=document.createElement("textarea");
	this.edit.style.width="100%";
	this.edit.style.height="100%";
	this.edit.style.color="#fff";
	this.edit.style.backgroundColor="#425f9c";
	div.appendChild(this.edit);
};
LogWindow.prototype.hide=function(){
	BaseWindow.prototype.hide.call(this);
	this.edit=null;
};
LogWindow.prototype.log=function(s){
	console.log(s);
	if(this.edit){
		this.edit.value=s+"\n"+this.edit.value;
	}
};
LogWindow.prototype.timeout=function(){
	this.timeouts++;
};
LogWindow.prototype.phantom=function(){
	this.phantoms++;
};
LogWindow.prototype.counts=function(){
	if(this.timeouts>0){
	this.log(this.timeouts+" timeout(s)");
	}
	if(this.phantoms>0){
		this.log(this.phantoms+" phantom(s)");
	}
	this.log("Responses = "+Global.root.queryAll(RESPONSE_COUNTER).length);
};
function Root(){
	this.rootNode=document.body;
	this.usingBody=true;
}
Root.removeOverlay=function(){
	document.querySelectorAll(CSS_LOGIN_STUFF).forEach(item=>{
		Global.log("Removing overlay stuff");
		item.parentNode.removeChild(item);
	});
};
Root.prototype.query=function(s){
	return this.rootNode.querySelector(s);
};
Root.prototype.queryAll=function(s){
	return this.rootNode.querySelectorAll(s);
};
Root.prototype.determine=function(){
	const EXPANDING="Expanding: ";
	const div=Dom.findFirstVisible(document.querySelectorAll(POST_ARTICLE));
	if(!!div){
		let canPost=!!document.querySelector(POST_ACTION);
		let topOnly=!canPost;
		if(topOnly){
			topOnly=Dom.filterHidden(document.querySelectorAll("[role=\"navigation\"]")).length==2;
		}
		else{
			topOnly=Dom.filterHidden(document.querySelectorAll("[role=\"feed\"]")).length>1;
		}
		if(topOnly){
			Global.log(EXPANDING+"Topmost post");
			this.rootNode=div.parentNode;
			this.usingBody=false;
		}
	}
	if(!this.usingBody){
		return;
	}
	const USE_PARENT=true;
	let check=[];
	check.push([".uiStreamStory","Video comments on right",!USE_PARENT]);
	check.push(["div.rhcScroller .uiScrollableAreaContent","Theater mode",USE_PARENT]);
	check.push([".uiLayer:not(.hidden_elem)","Overlaid post",!USE_PARENT]);
	check.push([".permalinkPost","Permalinked post",!USE_PARENT]);
	check.push(["[data-pagelet=\"TahoeRightRail\"]","Full-browser video",USE_PARENT]);
	check.push([FS_ARTICLE,"Full-browser",USE_PARENT]);
	check.push(["[role=\"main\"]","Main content area",!USE_PARENT]);
	check.push(["[role=\"feed\"]","Feed",!USE_PARENT]);
	check.find(item=>{
		const divs=Dom.filterHidden(document.querySelectorAll(item[0]));
		let div=null;
		if(divs.length==1){
			div=divs[0];
		}
		if(divs.length==2){
			div=divs[1];
		}
		if(!!div){
			Global.log(EXPANDING+item[1]);
			if(item[2]==USE_PARENT){
				div=div.parentNode;
			}
			this.rootNode=div;
			this.usingBody=false;
			return true;
		}
	});
};
Root.prototype.getRoot=function(){
	return this.rootNode;
};
Root.prototype.getResponseCount=function(){
	return getResponseCount(this.rootNode);
};
Root.prototype.getContentSize=function(){
	let result=this.rootNode.scrollHeight;
	result+=this.getResponseCount();
	return result;
};
Root.isClassicVideo=function(){
	const result=!!document.querySelector(".uiStreamStory");
	return result;
};
Root.prepIfClassicVideo=function(onDone){
	let wait=0;
	if(Root.isClassicVideo()){
		const links=document.querySelectorAll(SHOW_COMMENTS);
		if(links.length>0){
			Global.log("Making sure video comments are showing");
			links[links.length-1].click();
			wait=100;
		}
	}
	if(onDone){
		window.setTimeout(onDone,wait);
	}
};
Root.prototype.isFullBrowserNew=function(){
	let result=!!Global.root.query(FS_ARTICLE);
	return result;
};
Root.prototype.isSearchResults=function(){
	let result=!!Global.root.query("#pagelet_group_search,.p8dawk7l[role=\"presentation\"]");
	return result;
};
Root.prototype.countPosts=function(){
	if(Root.isClassicVideo()){
		return 1;
	}
	let filter=Array.from(Global.root.queryAll(POST_ROOT));
	filter=filter.filter(item=>!item.querySelector(POST_ROOT));
	return filter.length;
};
function Dom(){}
new Dom();
Dom.getStyle=function(node){
	return node.ownerDocument.defaultView.getComputedStyle(node,null);
};
Dom.isHidden=function(node){
	while(node&&node.ownerDocument){
		if(Dom.getStyle(node)["display"]=="none"){
			return true;
		}
		if(Dom.getStyle(node)["visibility"]=="hidden"){
			return true;
		}
		node=node.parentNode;
	}
	return false;
};
Dom.filterHidden=function(nodes){
	let result=[];
	nodes.forEach(item=>{
		if(!Dom.isHidden(item)){
			result.push(item);
		}
	});
	return result;
};
Dom.findFirstVisible=function(nodes){
	let filtered=Dom.filterHidden(nodes);
	return filtered.length>=1?filtered[0]:null;
};
Dom.dumpAncestors=function(node){
	while(node){
	let s=node.nodeName;
if(node.id){
	s+=" id=\""+node.id+"\"";
}if(node.className){
	s+=" class=\""+node.className+"\"";
}if(Dom.isHidden(node)){
	s+=" hidden";
}Global.log(s);
node=node.parentNode;
}};
Dom.upThenDown=function(node,ancestor,descendant){
	const item=node.parentNode.closest(ancestor);
if(item){
	return item.querySelector(descendant);
}return null;
};
function getResponseCount(item){
	return item.querySelectorAll(RESPONSE_COUNTER).length;
}function closeShareReport(onDone){
	const nodes=document.querySelectorAll(".sx_1ea4e0,.sx_ecfa40,.sx_1564cf,.sx_4564fd,.sx_4cbb0f");
if(nodes.length===1){
	const close=nodes[0].closest(".thwo4zme[role=\"button\"]");
if(close){
	close.click();
}}if(onDone)onDone();
}function ensureCommentsShowing(onDone){
	if(Global.root.isSearchResults()){
	Global.log("You must manually drill down into a search result.");
if(onDone)onDone();
return;
}let filter=[];
const n=Global.root.countPosts();
if(n>1){
	Global.log("Examining "+n+" posts");
}Global.root.queryAll(POST_ROOT).forEach(item=>{
	if(!item.querySelector(POST_ROOT)){
	const link=item.querySelector(SHOW_COMMENTS);
if(link&&!item.querySelector(SINGLE_COMMENT_AREA)){
	filter.push(link);
}}});
if(filter.length>0){
	Global.log("Showing comment area for "+filter.length+" post(s)");
clickAndWait(_NONE,onDone,filter,0);
}else{
	if(onDone)onDone();
}}function ensureCommentsShowingNew(onDone){
	let filter=[];
let selector=".tvmbv18p";
if(Global.root.isFullBrowserNew()){
	selector="[class=\"cwj9ozl2\"]";
}Global.root.queryAll(POST_ROOT).forEach(item=>{
	if(!item.querySelector(selector)){
	const link=item.querySelector(".gtad4xkn:first-child .auili1gw[role=\"button\"]");
if(link&&link.textContent.indexOf(" Share")<0){
	filter.push(link);
}}});
if(filter.length>0){
	Global.log("Showing comment area for "+filter.length+" post(s)");
clickAndWait(_NONE,onDone,filter,0);
}else{
	if(onDone)onDone();
}}function isNewWindow(link){
	return!!link.querySelector("a[target][href]");
}function newWindowNow(link){
	const anchor=link.querySelector("a[target][href]");
Global.log("New window: "+anchor.textContent);
if(!window.open(anchor.getAttribute("href"),anchor.getAttribute("target"))){
	Global.log("New window was blocked!");
}}function clickClass(value,onDone){
	if(Global.escHandler.shouldAbort()){
	if(onDone)onDone();
return;
}let filter=Array.from(Global.root.queryAll(value)).filter(item=>{
	if(value===BASE_SEE_MORE){
	if(item.parentNode.closest(".groupsSideMargin")){
	return false;
}if(Dom.isHidden(item)){
	return false;
}return true;
}if(value===SEE_MORE_NEW){
	if(!!item.childElementCount){
	return false;
}let full=item.parentNode.textContent;
let link=item.textContent;
return(full.charAt(full.length-link.length-2)=="\u2026");
}if(value===EXPOSE_CONTENT){
	if(isNewWindow(item)){
	newWindowNow(item);
}return false;
}return true;
});
if(filter.length>0){
	clickAndWait(value,onDone,filter,0);
}else{
	if(onDone)onDone();
}return filter.length;
}function doNotWait(value){
	return[CSS_SEE_MORE,SEE_MORE_NEW,BASE_SEE_MORE,EXPOSE_CONTENT].indexOf(value)>=0;
}function commentsOrReplies(comments,onDone){
	if(Global.escHandler.shouldAbort()){
	if(onDone)onDone();
return;
}let filter=Array.from(Global.root.queryAll(CLASSIC_GET_CONTENT));
if(filter.length>0){
	if(comments){
	filter=filter.filter(item=>!item.querySelector(CLASSIC_GET_REPLIES));
}else{
	filter=Array.from(Global.root.queryAll(CLASSIC_GET_REPLIES));
}}if(filter.length==0){
	filter=Array.from(Global.root.queryAll(NEW_GET_CONTENT));
if(filter.length>0){
	if(comments){
	filter=Array.from(Global.root.queryAll(NEW_GET_COMMENTS));
}else{
	filter=filter.filter(item=>!item.querySelector(NEW_GET_COMMENTS));
}filter=filter.filter(item=>!item.parentNode.parentNode.querySelector("img"));
filter=filter.filter(item=>!item.querySelector("[role=\"img\"]"));
}}if(filter.length>0){
	clickAndWait(comments?_COMMENTS:_REPLIES,onDone,filter,0);
}else{
	if(onDone)onDone();
}}function getBestLabel(link){
	let label=link.getAttribute("aria-label");
if(!label&&link.querySelector("._3eol")){
	label=link.querySelector("._3eol").textContent;
}if(!label){
	label=link.textContent;
}label=label.split("\u00a0\u0020\u00b7")[0];
const time=link.querySelector("._3eom");
if(time&&label.endsWith(time.textContent)){
	label=label.substring(0,label.length-time.textContent.length);
}return label;
}function clickAndWait(value,onDone,links,i){
	if(Global.escHandler.shouldAbort()){
	if(onDone)onDone();
return;
}let n=Global.root.getContentSize();
Global.log("click ("+(links.length-i-1)+" left): "+getBestLabel(links[i]));
links[i].click();
if(value==_NONE){
	n=Global.root.getContentSize();
}let wait=MAX_WAIT;
let time=WAIT_TIME;
if(doNotWait(value)){
	wait=-1;
time=0;
}window.setTimeout(()=>waitHelper(value,onDone,links,i,n,wait),time);
}function waitHelper(value,onDone,links,i,n,wait){
	if(wait===-1){
	if(++i<links.length){
	clickAndWait(value,onDone,links,i);
}else{
	if(onDone)onDone();
}return;
}if(Global.root.getContentSize()-n!=0){
	if(++i<links.length){
	clickAndWait(value,onDone,links,i);
}else{
	if(value==_COMMENTS||value==_REPLIES){
	commentsOrReplies(value==_COMMENTS,onDone);
}else{
	if(onDone)onDone();
}}return;
}if(window.doPhantomCheck&&!Global.root.getRoot().contains(links[i])){
	Global.logger.phantom();
wait=-1;
}if(wait>0){
	window.setTimeout(()=>waitHelper(value,onDone,links,i,n,--wait),WAIT_TIME);
return;
}if(wait==0){
	Global.logger.timeout();
}if(++i<links.length){
	clickAndWait(value,onDone,links,i);
}else{
	if(onDone)onDone();
}}function pumpOnce(onDone){
	window.responseCount=Global.root.getResponseCount();
window.doPhantomCheck=true;
if((todo&EXPAND_COMMENTS)!=0){
	commentsOrReplies(true,()=>pumpOnce2(onDone));
}else{
	pumpOnce2(onDone);
}}function pumpOnce2(onDone){
	if((todo&EXPAND_REPLIES)!=0){
	commentsOrReplies(false,()=>pumpOnce3(onDone));
}else{
	pumpOnce3(onDone);
}}function pumpOnce3(onDone){
	if(Global.root.getResponseCount()>window.responseCount){
	window.setTimeout(()=>pumpOnce(onDone),500);
}else{
	delete window.doPhantomCheck;
if(onDone)onDone();
}}function setFilter(onDone){
	window.filters=Array.from(Global.root.queryAll("["+FILTER_ATTR+"]")).filter(item=>item.getAttribute(FILTER_ATTR)!=FILTER_VALUE);
window.filters_i=0;
window.filters_onDone=onDone;
if(window.filters.length>0){
	Global.log("Changing "+window.filters.length+" Classic filter(s)");
}filterOne();
}function filterOne(){
	if(window.filters_i<window.filters.length){
	const link=window.filters[window.filters_i++];
link.click();
window.setTimeout(()=>setFilter2(link),100);
}else{
	if(window.filters_onDone)window.filters_onDone();
}}function setFilter2(link){
	const menu=document.querySelector("[data-ownerid=\""+link.id+"\"]");
if(menu){
	const item=menu.querySelector("["+FILTER_ATTR+"=\""+FILTER_VALUE+"\"]");
if(item){
	const post=link.closest(FILTER_ROOT);
window.setTimeout(()=>setFilter3(post,50));
item.closest("a").click();
return;
}}link.click();
filterOne();
}function setFilter3(post){
	if(!post.querySelector(FILTER_DONE)){
	window.setTimeout(()=>setFilter3(post),200);
}else{
	filterOne();
}}function setFilterNew(onDone){
	window.filters=Array.from(Global.root.queryAll(FILTER_NEW));
window.filters=window.filters.filter(item=>!item.closest(".sq6gx45u"));
window.filters=window.filters.filter(item=>!item.querySelector("h1,svg"));
if(window.filters>Global.root.countPosts()){
	Global.log("Something went wrong");
Global.log("Not checking "+window.filters.length+" New filter(s)");
if(onDone)onDone;
return;
}window.filters_i=0;
window.filters_onDone=onDone;
if(window.filters.length>0){
	Global.log("Checking "+window.filters.length+" New filter(s)");
}filterOneNew();
}function filterOneNew(){
	if(window.filters_i<window.filters.length){
	const link=window.filters[window.filters_i++];
link.click();
window.setTimeout(()=>setFilterNew2(link),100);
}else{
	if(window.filters_onDone)window.filters_onDone();
}}function setFilterNew2(link){
	let filter=Array.from(document.querySelectorAll(".ama3r5zh[role=\"menu\"],.swg4t2nn[role=\"menu\"]"));
filter=filter.filter(item=>item.querySelectorAll("[role=\"menuitem\"]").length>=3);
if(filter.length==1){
	const menus=filter[0].querySelectorAll("[role=\"menuitem\"]");
const span=menus[2].querySelector("span");
let text="";
if(!!span){
	text=span.textContent;
}if(text!=link.textContent){
	menus[2].click();
const post=link.closest(NEW_ARTICLE);
window.setTimeout(()=>setFilterNew3(post),100);
return;
}menus[0].closest("[role=\"menu\"]").outerHTML="";
}filterOneNew();
}function setFilterNew3(post){
	if(!!post.querySelector(FILTER_NEW)){
	filterOneNew();
}else{
	window.setTimeout(()=>setFilterNew3(post),100);
}}function Actions(){
	this.i=0;
	this.setUpActions();
}Actions.prototype.setUpActions=function(){
	this.actions=[];
this.actions.push(onDone=>Root.prepIfClassicVideo(onDone));
this.actions.push(onDone=>ensureCommentsShowing(onDone));
this.actions.push(onDone=>ensureCommentsShowingNew(onDone));
this.actions.push(onDone=>closeShareReport(onDone));
if((todo&EXPAND_FILTER)==0){
	this.actions.push(onDone=>setFilter(onDone));
this.actions.push(onDone=>setFilterNew(onDone));
}this.actions.push(onDone=>clickClass(BASE_SEE_MORE,onDone));
if((todo&EXPAND_POST)!=0){
	this.actions.push(onDone=>clickClass(EXPOSE_CONTENT,onDone));
}this.actions.push(onDone=>pumpOnce(onDone));
this.actions.push(onDone=>clickClass(CSS_SEE_MORE,onDone));
this.actions.push(onDone=>clickClass(SEE_MORE_NEW,onDone));
this.actions.push(Session.endSession);
this.actions.push(null);
};
Actions.prototype.doAction=function(){
	if(this.actions[this.i]!==null){
		this.actions[this.i](()=>window.setTimeout(bind(this,this.doAction),50));
		this.i++;
	}
};
Actions.prototype.kickOff=function(){
	this.i=0;
	this.doAction();
};
function Session(){
}
Session.init=function(){
	if(window.Global){
		Global=window.Global;
		Global.escHandler.abort(true);
	}
	else{
		Session.kickOff();
	}
};
Session.kickOff=function(){
	Global={
		escHandler:new EscHandler(),
		cfgHandler:new CfgHandler(),
		logger:new LogWindow(),
		root:new Root()
	};
	Global.log=function(s){
		Global.logger.log(s);
	};
	window.Global=Global;
	Session.main();
};
Session.main=function(){
	todo=Settings.getInt(SETTINGS_KEY,todo);
	Global.logger.show();
	Global.escHandler.on();
	Global.cfgHandler.on();
	Root.removeOverlay();
	Global.root.determine();
	Global.actions=new Actions();
	Global.actions.kickOff();
};
Session.endSession=function(){
	Global.logger.counts();
	if(Global.cfgHandler.shouldConfig()){
		CfgWindow.showIt();
	return;
	}
	Global.ending=true;
	Global.log("[Press \u0027s\u0027 now for Settings]");
	window.setTimeout(Session.maybeEnd,END_DELAY*1000);
};
Session.maybeEnd=function(){
	delete Global.ending;
	if(!Global.cfgHandler.shouldConfig()){
		Session.trulyEnd();
	}
};
Session.trulyEnd=function(){
	if(Global.cfg){
		Global.cfg.hide();
		delete Global.cfg;
	}
	Global.escHandler.off();
	Global.cfgHandler.off();
	Global.logger.hide();
	delete window.Global;
	Global=null;
	
	var para = document.createElement("p");
	para.name="Hello"
	var node = document.createTextNode("T'is done my dudes!");
	para.appendChild(node);
	var element = document.getElementById("facebook");
	element.appendChild(para);
};
Session.init();