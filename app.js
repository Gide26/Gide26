const sampleAssets = [
  {ticker:'NVDA',name:'NVIDIA',asset:'stock',price:187.62,change:2.84,volume:42.1,rsi:67,macd:1,trend20:1,trend50:1,volumeRatio:1.42},
  {ticker:'MSFT',name:'Microsoft',asset:'stock',price:521.38,change:0.92,volume:18.7,rsi:59,macd:1,trend20:1,trend50:1,volumeRatio:1.08},
  {ticker:'AAPL',name:'Apple',asset:'stock',price:238.15,change:-0.43,volume:31.2,rsi:48,macd:0,trend20:1,trend50:1,volumeRatio:.91},
  {ticker:'AMZN',name:'Amazon',asset:'stock',price:226.49,change:1.72,volume:26.4,rsi:63,macd:1,trend20:1,trend50:1,volumeRatio:1.26},
  {ticker:'GOOGL',name:'Alphabet',asset:'stock',price:184.21,change:.38,volume:14.5,rsi:54,macd:1,trend20:1,trend50:1,volumeRatio:.96},
  {ticker:'META',name:'Meta Platforms',asset:'stock',price:741.85,change:2.15,volume:11.9,rsi:72,macd:1,trend20:1,trend50:1,volumeRatio:1.31},
  {ticker:'TSLA',name:'Tesla',asset:'stock',price:338.76,change:-2.76,volume:85.3,rsi:38,macd:0,trend20:0,trend50:0,volumeRatio:1.55},
  {ticker:'AVGO',name:'Broadcom',asset:'stock',price:348.22,change:1.18,volume:7.8,rsi:61,macd:1,trend20:1,trend50:1,volumeRatio:1.14},
  {ticker:'JPM',name:'JPMorgan Chase',asset:'stock',price:302.45,change:.64,volume:8.6,rsi:57,macd:1,trend20:1,trend50:1,volumeRatio:1.02},
  {ticker:'LLY',name:'Eli Lilly',asset:'stock',price:891.30,change:-1.08,volume:2.7,rsi:44,macd:0,trend20:1,trend50:0,volumeRatio:.88},
  {ticker:'WMT',name:'Walmart',asset:'stock',price:104.88,change:.27,volume:9.1,rsi:53,macd:1,trend20:1,trend50:1,volumeRatio:.94},
  {ticker:'ORCL',name:'Oracle',asset:'stock',price:244.12,change:1.92,volume:6.2,rsi:66,macd:1,trend20:1,trend50:1,volumeRatio:1.37},
  {ticker:'COST',name:'Costco',asset:'stock',price:967.45,change:-.26,volume:1.4,rsi:49,macd:0,trend20:1,trend50:1,volumeRatio:.82},
  {ticker:'NFLX',name:'Netflix',asset:'stock',price:1194.80,change:1.36,volume:1.8,rsi:64,macd:1,trend20:1,trend50:1,volumeRatio:1.12},
  {ticker:'AMD',name:'Advanced Micro Devices',asset:'stock',price:172.93,change:-1.84,volume:24.6,rsi:41,macd:0,trend20:0,trend50:0,volumeRatio:1.23},
  {ticker:'CRM',name:'Salesforce',asset:'stock',price:289.71,change:.73,volume:4.9,rsi:56,macd:1,trend20:1,trend50:1,volumeRatio:1.01},
  {ticker:'UBER',name:'Uber Technologies',asset:'stock',price:96.44,change:2.38,volume:13.7,rsi:68,macd:1,trend20:1,trend50:1,volumeRatio:1.44},
  {ticker:'ADBE',name:'Adobe',asset:'stock',price:412.66,change:-1.45,volume:3.3,rsi:39,macd:0,trend20:0,trend50:0,volumeRatio:.97},
  {ticker:'CSCO',name:'Cisco Systems',asset:'stock',price:71.24,change:.51,volume:12.8,rsi:55,macd:1,trend20:1,trend50:1,volumeRatio:1.06},
  {ticker:'KO',name:'Coca-Cola',asset:'stock',price:70.38,change:.11,volume:10.4,rsi:52,macd:0,trend20:1,trend50:1,volumeRatio:.79},
  {ticker:'V',name:'Visa',asset:'stock',price:352.16,change:.86,volume:3.1,rsi:58,macd:1,trend20:1,trend50:1,volumeRatio:1.05},
  {ticker:'XOM',name:'Exxon Mobil',asset:'stock',price:117.50,change:-.66,volume:12.3,rsi:46,macd:0,trend20:0,trend50:1,volumeRatio:.91},
  {ticker:'PLTR',name:'Palantir',asset:'stock',price:181.74,change:4.62,volume:53.2,rsi:78,macd:1,trend20:1,trend50:1,volumeRatio:2.08},
  {ticker:'BA',name:'Boeing',asset:'stock',price:221.06,change:-2.15,volume:5.5,rsi:34,macd:0,trend20:0,trend50:0,volumeRatio:1.18},
  {ticker:'QQQ',name:'Invesco QQQ Trust',asset:'stock',price:586.17,change:1.23,volume:32.8,rsi:62,macd:1,trend20:1,trend50:1,volumeRatio:1.09},
  {ticker:'SPY',name:'SPDR S&P 500 ETF',asset:'stock',price:674.08,change:.58,volume:41.6,rsi:57,macd:1,trend20:1,trend50:1,volumeRatio:1.02},
  {ticker:'IWM',name:'iShares Russell 2000 ETF',asset:'stock',price:241.86,change:-.72,volume:21.3,rsi:45,macd:0,trend20:0,trend50:1,volumeRatio:.96},
  {ticker:'GLD',name:'SPDR Gold Shares',asset:'stock',price:298.52,change:.94,volume:8.2,rsi:65,macd:1,trend20:1,trend50:1,volumeRatio:1.17},
  {ticker:'BAC',name:'Bank of America',asset:'stock',price:48.16,change:-.39,volume:27.1,rsi:47,macd:0,trend20:1,trend50:0,volumeRatio:1.03},
  {ticker:'DIS',name:'Walt Disney',asset:'stock',price:113.74,change:-1.12,volume:6.8,rsi:42,macd:0,trend20:0,trend50:0,volumeRatio:.92},
  {ticker:'BTC',name:'Bitcoin',asset:'crypto',price:110842.50,change:2.16,volume:48.2,rsi:64,macd:1,trend20:1,trend50:1,volumeRatio:1.34},
  {ticker:'ETH',name:'Ethereum',asset:'crypto',price:4021.80,change:1.48,volume:22.1,rsi:61,macd:1,trend20:1,trend50:1,volumeRatio:1.21},
  {ticker:'BNB',name:'BNB',asset:'crypto',price:1028.60,change:.83,volume:1.4,rsi:57,macd:1,trend20:1,trend50:1,volumeRatio:1.04},
  {ticker:'XRP',name:'XRP',asset:'crypto',price:2.48,change:-1.73,volume:3.9,rsi:40,macd:0,trend20:0,trend50:0,volumeRatio:1.12},
  {ticker:'SOL',name:'Solana',asset:'crypto',price:186.35,change:3.15,volume:6.8,rsi:69,macd:1,trend20:1,trend50:1,volumeRatio:1.53},
  {ticker:'DOGE',name:'Dogecoin',asset:'crypto',price:.194,change:-3.42,volume:1.3,rsi:33,macd:0,trend20:0,trend50:0,volumeRatio:1.39},
  {ticker:'ADA',name:'Cardano',asset:'crypto',price:.842,change:-.88,volume:.42,rsi:46,macd:0,trend20:0,trend50:1,volumeRatio:.89},
  {ticker:'LINK',name:'Chainlink',asset:'crypto',price:18.73,change:1.06,volume:.36,rsi:55,macd:1,trend20:1,trend50:1,volumeRatio:1.08},
  {ticker:'AVAX',name:'Avalanche',asset:'crypto',price:27.42,change:-2.38,volume:.28,rsi:37,macd:0,trend20:0,trend50:0,volumeRatio:1.18},
  {ticker:'SUI',name:'Sui',asset:'crypto',price:3.64,change:4.12,volume:1.1,rsi:74,macd:1,trend20:1,trend50:1,volumeRatio:1.87},
  {ticker:'LTC',name:'Litecoin',asset:'crypto',price:103.27,change:.22,volume:.51,rsi:51,macd:0,trend20:1,trend50:1,volumeRatio:.92},
  {ticker:'DOT',name:'Polkadot',asset:'crypto',price:4.82,change:-1.26,volume:.19,rsi:43,macd:0,trend20:0,trend50:0,volumeRatio:.86},
  {ticker:'EUR/USD',name:'Euro / US Dollar',asset:'forex',currency:'USD',price:1.1542,change:.24,volume:0,rsi:58,macd:1,trend20:1,trend50:1,volumeRatio:1.02},
  {ticker:'GBP/USD',name:'British Pound / US Dollar',asset:'forex',currency:'USD',price:1.3174,change:-.12,volume:0,rsi:49,macd:0,trend20:1,trend50:1,volumeRatio:.94},
  {ticker:'USD/JPY',name:'US Dollar / Japanese Yen',asset:'forex',currency:'JPY',price:153.86,change:.18,volume:0,rsi:61,macd:1,trend20:1,trend50:1,volumeRatio:1.04},
  {ticker:'USD/CHF',name:'US Dollar / Swiss Franc',asset:'forex',currency:'CHF',price:.8032,change:-.21,volume:0,rsi:43,macd:0,trend20:0,trend50:1,volumeRatio:.89},
  {ticker:'AUD/USD',name:'Australian Dollar / US Dollar',asset:'forex',currency:'USD',price:.6521,change:.07,volume:0,rsi:52,macd:1,trend20:1,trend50:0,volumeRatio:1.01},
  {ticker:'XAU/USD',name:'Gold / US Dollar',asset:'commodity',currency:'USD',price:3986.3,change:.42,volume:0,rsi:64,macd:1,trend20:1,trend50:1,volumeRatio:1.11},
  {ticker:'XAG/USD',name:'Silver / US Dollar',asset:'commodity',currency:'USD',price:48.7,change:-.32,volume:0,rsi:47,macd:0,trend20:1,trend50:1,volumeRatio:.98},
  {ticker:'WTI',name:'WTI Crude Oil',asset:'commodity',currency:'USD',price:61.8,change:1.15,volume:0,rsi:59,macd:1,trend20:1,trend50:0,volumeRatio:1.2},
  {ticker:'BRENT',name:'Brent Crude Oil',asset:'commodity',currency:'USD',price:65.2,change:.38,volume:0,rsi:54,macd:0,trend20:1,trend50:0,volumeRatio:1.05},
  {ticker:'SPX',name:'S&P 500 Index',asset:'index',currency:'USD',price:6821.4,change:.31,volume:0,rsi:57,macd:1,trend20:1,trend50:1,volumeRatio:1.0},
  {ticker:'NDX',name:'Nasdaq 100 Index',asset:'index',currency:'USD',price:25176.2,change:.74,volume:0,rsi:65,macd:1,trend20:1,trend50:1,volumeRatio:1.1},
  {ticker:'DJI',name:'Dow Jones Industrial Average',asset:'index',currency:'USD',price:47156.8,change:.12,volume:0,rsi:53,macd:1,trend20:1,trend50:1,volumeRatio:1.0},
  {ticker:'DAX',name:'DAX Index',asset:'index',currency:'EUR',price:23842.7,change:-.16,volume:0,rsi:48,macd:0,trend20:1,trend50:1,volumeRatio:.98},
  {ticker:'N225',name:'Nikkei 225 Index',asset:'index',currency:'JPY',price:52362.1,change:.56,volume:0,rsi:62,macd:1,trend20:1,trend50:1,volumeRatio:1.08},
  {ticker:'TSM',name:'Taiwan Semiconductor ADR',asset:'stock',currency:'USD',price:301.4,change:1.42,volume:12.4,rsi:67,macd:1,trend20:1,trend50:1,volumeRatio:1.22},
  {ticker:'SAP',name:'SAP ADR',asset:'stock',currency:'USD',price:283.6,change:.29,volume:1.5,rsi:55,macd:1,trend20:1,trend50:1,volumeRatio:.97},
  {ticker:'BABA',name:'Alibaba ADR',asset:'stock',currency:'USD',price:164.3,change:-.64,volume:9.8,rsi:46,macd:0,trend20:1,trend50:0,volumeRatio:1.02},
  {ticker:'TM',name:'Toyota Motor ADR',asset:'stock',currency:'USD',price:190.2,change:.17,volume:1.2,rsi:51,macd:0,trend20:1,trend50:1,volumeRatio:.9}
];

let assets = sampleAssets.map(a => ({...a}));
let activeUniverse = 'all';
let activeSignal = 'all';
let watchOnly = false;
let watchlist = new Set();
let sortAscending = false;
let chartPeriod = '1W';
let toastTimer;
const $ = (selector, root=document) => root.querySelector(selector);
const $$ = (selector, root=document) => [...root.querySelectorAll(selector)];
const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const clamp = (n,min,max) => Math.max(min,Math.min(max,n));

function scoreAsset(a){
  const trend = (a.trend20 ? 17.5 : 0) + (a.trend50 ? 17.5 : 0);
  const rsi = Number(a.rsi);
  const rsiScore = rsi >= 48 && rsi <= 68 ? 20 : rsi >= 40 && rsi < 48 ? 14 : rsi > 68 && rsi <= 75 ? 13 : rsi > 75 ? 4 : 7;
  const momentum = (a.macd ? 10 : 0) + rsiScore;
  const participation = Number(a.volumeRatio) >= 1.15 ? 20 : Number(a.volumeRatio) >= .9 ? 14 : 8;
  const priceAction = clamp(7.5 + Number(a.change) * 2.5,0,15);
  return Math.round(clamp(trend + momentum + participation + priceAction,0,100));
}
function signalFor(a){const score=scoreAsset(a);if(score>=67)return 'Bullish';if(score>=40)return 'Watch';return 'Bearish'}
function formatPrice(n,currency='USD'){n=Number(n);if(!Number.isFinite(n))return '—';const value=n>=1000?n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2}):n>=1?n.toFixed(2):n.toPrecision(4);const code=String(currency||'USD').toUpperCase();return code==='USD'?'$'+value:`${value} ${esc(code)}`}
function formatVolume(n){n=Number(n);if(!Number.isFinite(n)||n<=0)return '—';return n>=1000?(n/1000).toFixed(1)+'B':n>=1?n.toFixed(1)+'M':(n*1000).toFixed(0)+'K'}
function assetLabel(type){return ({stock:'EQUITY',crypto:'CRYPTO',forex:'FOREX',commodity:'COMMODITY',index:'INDEX'})[type]||String(type||'ASSET').toUpperCase()}
function trendInfo(a){if(a.trend20&&a.trend50)return {text:'Uptrend',cls:'trend-up',icon:'↗'};if(!a.trend20&&!a.trend50)return {text:'Downtrend',cls:'trend-down',icon:'↘'};return {text:'Mixed',cls:'trend-flat',icon:'→'}}
function visibleAssets(){const q=$('#search-input').value.trim().toLowerCase();return assets.filter(a=>(activeUniverse==='all'||a.asset===activeUniverse)&&(!q||`${a.ticker} ${a.name}`.toLowerCase().includes(q))&&(activeSignal==='all'||signalFor(a).toLowerCase()===activeSignal)&&(!watchOnly||watchlist.has(a.ticker))).sort((a,b)=>sortAscending?scoreAsset(a)-scoreAsset(b):scoreAsset(b)-scoreAsset(a))}
function render(){
  const counts={all:assets.length,stock:assets.filter(a=>a.asset==='stock').length,crypto:assets.filter(a=>a.asset==='crypto').length,forex:assets.filter(a=>a.asset==='forex').length,commodity:assets.filter(a=>a.asset==='commodity').length,index:assets.filter(a=>a.asset==='index').length};
  Object.entries(counts).forEach(([type,count])=>{const node=$(`#count-${type}`);if(node)node.textContent=count});$('#nav-count').textContent=counts.all;$('#metric-universe').innerHTML=`${counts.all} <small>assets</small>`;
  const bullish=assets.filter(a=>signalFor(a)==='Bullish').length,watch=assets.filter(a=>signalFor(a)==='Watch').length,bearish=assets.length-bullish-watch;
  const breadth=assets.length?Math.round(100*assets.filter(a=>a.trend50).length/assets.length):0;
  const avg=assets.length?assets.reduce((s,a)=>s+Math.abs(Number(a.change)||0),0)/assets.length:0;
  $('#metric-bullish').textContent=`${bullish} / ${assets.length}`;$('#metric-breadth').textContent=`${breadth}%`;$('#metric-move').textContent=`${avg.toFixed(2)}%`;
  $('#donut-total').textContent=assets.length;$('#signal-legend').innerHTML=[['Bullish',bullish,'#55d6a2'],['Watch',watch,'#e5b96d'],['Bearish',bearish,'#ef777d']].map(([name,n,color])=>`<div class="legend-row"><span class="legend-name"><i class="legend-bullet" style="background:${color}"></i>${name}</span><span class="legend-count">${n}</span></div>`).join('');
  const denominator=assets.length||1,bdeg=360*bullish/denominator,wdeg=360*watch/denominator;
  $('#signal-donut').style.background=`conic-gradient(#55d6a2 0deg ${bdeg}deg,#e5b96d ${bdeg}deg ${bdeg+wdeg}deg,#ef777d ${bdeg+wdeg}deg 360deg)`;
  const top=[...assets].sort((a,b)=>scoreAsset(b)-scoreAsset(a))[0];$('#top-name').textContent=top?`${top.ticker} · ${top.name}`:'No assets';$('#top-score').textContent=top?`${scoreAsset(top)} / 100`:'—';
  $('#watch-count').textContent=watchlist.size;
  const rows=visibleAssets();$('#scan-count').textContent=`${rows.length} asset${rows.length===1?'':'s'}`;$('#results-label').textContent=`Showing ${rows.length} of ${counts[activeUniverse]??counts.all} assets`;$('#page-end').textContent=rows.length;
  if(!rows.length){$('#asset-rows').innerHTML='<tr><td colspan="9" class="empty-state">No assets match these filters. Try another search or import a CSV.</td></tr>'}
  else $('#asset-rows').innerHTML=rows.map(a=>{
    const score=scoreAsset(a),signal=signalFor(a),trend=trendInfo(a),change=Number(a.change)||0;
    const fill=score>=67?'':' '+(score>=40?'mid':'low');
    const rsiClass=Number(a.rsi)>=70?'rsi-hot':Number(a.rsi)<=35?'rsi-cold':'';
    const icon=(a.ticker||'?').slice(0,1);
    return `<tr data-ticker="${esc(a.ticker)}"><td><div class="asset-cell"><span class="coin-icon ${a.asset==='crypto'?'crypto':''}">${esc(icon)}</span><span class="asset-main"><b>${esc(a.name)}</b><span>${esc(a.ticker)} · ${assetLabel(a.asset)}</span></span></div></td><td class="price-cell">${formatPrice(a.price,a.currency)}</td><td class="${change>0?'positive':change<0?'negative':'neutral-change'}">${change>0?'+':''}${change.toFixed(2)}%</td><td class="volume-cell">${formatVolume(a.volume)}</td><td class="rsi-cell ${rsiClass}">${Number(a.rsi).toFixed(0)}</td><td class="trend-cell ${trend.cls}">${trend.icon} ${trend.text}</td><td class="score-cell"><div class="score-flex"><span class="score-track"><i class="score-fill${fill}" style="width:${score}%"></i></span><b class="score-number">${score}</b></div></td><td><span class="signal-badge badge-${signal.toLowerCase()}">${signal}</span></td><td><button class="star-button ${watchlist.has(a.ticker)?'saved':''}" data-star="${esc(a.ticker)}" aria-label="${watchlist.has(a.ticker)?'Remove from':'Add to'} watchlist">${watchlist.has(a.ticker)?'★':'☆'}</button></td></tr>`;
  }).join('');
  $('#watch-filter').classList.toggle('active',watchOnly);$('#watch-filter').style.borderColor=watchOnly?'#4d8a70':'';
  drawChart();
}
function drawChart(){
  const canvas=$('#breadth-chart');if(!canvas)return;const rect=canvas.getBoundingClientRect();if(!rect.width||!rect.height)return;
  const dpr=window.devicePixelRatio||1;canvas.width=Math.round(rect.width*dpr);canvas.height=Math.round(rect.height*dpr);const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);const w=rect.width,h=rect.height;
  ctx.clearRect(0,0,w,h);ctx.strokeStyle='#27323e';ctx.lineWidth=1;ctx.setLineDash([3,4]);for(let i=0;i<4;i++){const y=6+i*(h-15)/3;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke()}ctx.setLineDash([]);
  const current=assets.length?Math.round(100*assets.filter(a=>a.trend50).length/assets.length):0;$('#chart-current').textContent=`${current}%`;
  let values=[];
  if(liveMode){$('#chart-subtitle').textContent='Live session breadth · history builds as scans run';$('#period-switch').style.visibility='hidden';values=liveBreadthHistory.slice(-48).map(point=>point.value);if(!values.length)values=[current];if(values.length===1){ctx.fillStyle='#91a0ad';ctx.font='10px DM Sans, sans-serif';ctx.textAlign='center';ctx.fillText('Collecting live breadth history…',w/2,h/2);ctx.beginPath();ctx.arc(w-3,h-((current-10)/80)*(h-8)-4,3,0,Math.PI*2);ctx.fillStyle='#79e7b8';ctx.fill();return}}
  else{$('#chart-subtitle').textContent='Share above 50-day trend · illustrative sample history';$('#period-switch').style.visibility='visible';const n=chartPeriod==='1W'?24:chartPeriod==='1M'?32:42;const seed=assets.reduce((sum,a)=>sum+(a.ticker.charCodeAt(0)||0),0);for(let i=0;i<n;i++){const progress=i/(n-1);const wave=Math.sin((i+seed%13)*.61)*9+Math.cos((i+seed%7)*.31)*5;values.push(clamp(current+(progress-.86)*12+wave*(.55+progress*.18),9,87))}values[n-1]=current}
  const n=values.length;const px=i=>n===1?w:i/(n-1)*w;const py=v=>h-((v-10)/80)*(h-8)-4;
  const gradient=ctx.createLinearGradient(0,0,0,h);gradient.addColorStop(0,'rgba(85,214,162,.24)');gradient.addColorStop(1,'rgba(85,214,162,0)');ctx.beginPath();values.forEach((v,i)=>i?ctx.lineTo(px(i),py(v)):ctx.moveTo(px(i),py(v)));if(!liveMode){ctx.lineTo(w,h);ctx.lineTo(0,h);ctx.closePath();ctx.fillStyle=gradient;ctx.fill()}
  ctx.beginPath();values.forEach((v,i)=>i?ctx.lineTo(px(i),py(v)):ctx.moveTo(px(i),py(v)));ctx.strokeStyle='#5bd4a2';ctx.lineWidth=2;ctx.lineJoin='round';if(n>1)ctx.stroke();ctx.beginPath();ctx.arc(px(n-1),py(values[n-1]),3,0,Math.PI*2);ctx.fillStyle='#79e7b8';ctx.fill();
}
function toast(message){const node=$('#toast');node.textContent=message;node.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>node.classList.remove('show'),4500)}
function setFeedState(mode,detail=''){
  const live=mode==='live',paused=mode==='paused',ready=mode==='ready';liveMode=live||paused;const connected=live||paused;const pill=$('#feed-pill'),sidebar=$('.data-status');
  pill.classList.toggle('connected',connected);pill.textContent=live?'● LIVE DATA':paused?'● LIVE PAUSED':ready?'● FEED READY':'● DEMO DATA';
  $('#sidebar-status-title').textContent=live?'Live feed active':paused?'Live feed paused':ready?'Live feed ready':mode==='csv'?'CSV dataset':'Demo workspace';
  $('#sidebar-status-detail').textContent=connected?detail:ready?'Twelve Data configured':mode==='csv'?'Local file only':'Live feed not connected';
  sidebar.classList.toggle('connected',connected);$('#live-button').classList.toggle('running',live);$('#live-button').innerHTML=live?'<span>◉</span> Stop live scan':paused?'<span>◉</span> Resume live scan':'<span>◉</span> Start live scan';
  if(mode==='live'){$('#notice-title').textContent='Live data · Twelve Data.';$('#notice-detail').textContent=detail+' Signals refresh automatically while this page is open. Provider latency and coverage vary by market and plan.'}
  else if(mode==='paused'){$('#notice-title').textContent='Live scan paused.';$('#notice-detail').textContent='Showing the last fetched live data snapshot. Resume live scan to continue checking for signal changes.'}
  else if(mode==='ready'){$('#notice-title').textContent='Live feed ready.';$('#notice-detail').textContent='Select Start live scan to fetch configured instruments. The universe is edited in universe.json; provider coverage and usage limits apply.'}
  else if(mode==='demo'){$('#notice-title').textContent='Demo data.';$('#notice-detail').textContent=detail||'Add a Twelve Data API key to the local server configuration to enable live scans. Until connected, prices and signal examples are illustrative.'}
  else if(mode==='csv'){$('#notice-title').textContent='Imported CSV.';$('#notice-detail').textContent=detail||'This file is analyzed locally in your browser. It is not a live feed.'}
}
async function checkFeedStatus(){try{const response=await fetch('/api/status');if(!response.ok)throw new Error('Local API server not detected. Start Northstar with python server.py.');const status=await response.json();if(status.connected){setFeedState('ready');$('#sidebar-status-detail').textContent=`${status.universeSize} configured instruments`}else setFeedState('demo','Copy .env.example to .env, add your Twelve Data API key, then restart the local server.')}catch(error){setFeedState('demo',error.message||'Start Northstar with python server.py to enable the live-data connection.')}}
let liveMode=false,liveBreadthHistory=[],liveTimer=null,liveLoading=false,lastLiveSignals=null,liveRefreshSeconds=300;
async function loadLiveScan(isFirst=false){if(liveLoading)return;liveLoading=true;$('#refresh-button').style.opacity='.5';try{const response=await fetch('/api/scan');const payload=await response.json();if(!response.ok)throw new Error(payload.error||'Live scan failed.');const previous=lastLiveSignals;assets=payload.assets;lastLiveSignals=new Map(assets.map(a=>[a.ticker,signalFor(a)]));const breadth=assets.length?Math.round(100*assets.filter(a=>a.trend50).length/assets.length):0;liveBreadthHistory.push({value:breadth,at:payload.updatedAt});if(liveBreadthHistory.length>100)liveBreadthHistory=liveBreadthHistory.slice(-100);const when=new Date(payload.updatedAt).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});const missing=payload.errors?.length||0,warningCount=payload.warnings?.length||0;setFeedState('live',`${assets.length} assets · ${when}${missing?` · ${missing} skipped`:''}${warningCount?` · ${warningCount} warnings`:''}`);render();if(previous&&!isFirst){const changed=assets.filter(a=>previous.has(a.ticker)&&previous.get(a.ticker)!==signalFor(a));if(changed.length){const labels=changed.slice(0,4).map(a=>`${a.ticker} → ${signalFor(a)}`).join(', ');toast(`Signal update: ${labels}${changed.length>4?` +${changed.length-4} more`:''}`)}}if(isFirst)toast(`Live scan loaded ${assets.length} instruments.`);if(missing||warningCount)$('#notice-detail').textContent=missing?`${missing} configured symbols were not returned. Verify symbol formats and market access in universe.json / your Twelve Data plan. Last successful scan: ${when}.`:payload.warnings[0];return true}catch(error){toast(error.message||'Could not fetch live data.');if(!assets.length)setFeedState('demo',error.message);if(liveTimer){clearInterval(liveTimer);liveTimer=null;setFeedState('ready',error.message)}return false}finally{liveLoading=false;$('#refresh-button').style.opacity=''}}
async function toggleLiveScan(){if(liveTimer){clearInterval(liveTimer);liveTimer=null;setFeedState('paused','Auto-refresh stopped');render();toast('Live signal monitoring stopped.');return}try{const response=await fetch('/api/status');if(!response.ok)throw new Error('Use the local server command `python server.py` to enable live data.');const status=await response.json();if(!status.connected)throw new Error('Add your Twelve Data API key to .env on your PC, then restart server.py. Never paste your key into chat.');liveRefreshSeconds=Math.max(60,Number(status.cacheSeconds)||300);const ok=await loadLiveScan(true);if(ok)liveTimer=setInterval(()=>loadLiveScan(false),(liveRefreshSeconds+3)*1000)}catch(error){toast(error.message||'Could not connect to the live feed.')}}
function showDetails(ticker){const a=assets.find(item=>item.ticker===ticker);if(!a)return;const score=scoreAsset(a),signal=signalFor(a),trend=trendInfo(a);$('#detail-content').innerHTML=`<div class="section-kicker">ASSET SNAPSHOT · ${assetLabel(a.asset)}</div><div class="detail-title"><span class="coin-icon ${a.asset==='crypto'?'crypto':''}">${esc(a.ticker.slice(0,1))}</span><div><h2>${esc(a.name)}</h2><p>${esc(a.ticker)} · ${signal} signal</p></div><span class="opportunity-score" style="margin-left:auto">${score}/100</span></div><div class="detail-price">${formatPrice(a.price,a.currency)} <small class="${a.change>=0?'positive':'negative'}">${a.change>0?'+':''}${Number(a.change).toFixed(2)}%</small></div><div class="detail-grid"><div class="detail-stat"><span>RSI (14)</span><b>${Number(a.rsi).toFixed(0)} ${Number(a.rsi)>=70?'· elevated':Number(a.rsi)<=30?'· oversold':''}</b></div><div class="detail-stat"><span>Trend</span><b class="${trend.cls}">${trend.icon} ${trend.text}</b></div><div class="detail-stat"><span>MACD direction</span><b>${a.macd?'Positive':'Negative / flat'}</b></div><div class="detail-stat"><span>Volume vs avg.</span><b>${Number(a.volumeRatio).toFixed(2)}×</b></div></div><div class="detail-note">${score>=67?'Positive trend and momentum indicators align. Check valuation, event risk, and position sizing before acting.':score>=40?'Signals are mixed. Consider waiting for trend or momentum confirmation and reviewing downside risk.':'Weak trend or momentum readings are present. This is not a short recommendation; review risk and context.'}</div><p class="dialog-disclaimer">${liveMode?`Provider bar: ${esc(a.asOf||'unknown')}. Latency depends on your Twelve Data plan.`:'Sample snapshot only; not a live quote.'} Not an investment recommendation.</p>`;$('#detail-dialog').showModal()}
function parseCSV(text){
  const lines=text.replace(/^\uFEFF/,'').split(/\r?\n/).filter(line=>line.trim());if(lines.length<2)throw new Error('CSV needs a header row and at least one data row.');
  const parseLine=line=>{const out=[];let current='',quoted=false;for(let i=0;i<line.length;i++){const ch=line[i];if(ch==='"'&&line[i+1]==='"'&&quoted){current+='"';i++}else if(ch==='"')quoted=!quoted;else if(ch===','&&!quoted){out.push(current.trim());current=''}else current+=ch}out.push(current.trim());return out};
  const headers=parseLine(lines[0]).map(h=>h.toLowerCase().replace(/[^a-z0-9]/g,''));const aliases={symbol:'ticker',ticker:'ticker',assetname:'name',name:'name',type:'asset',asset:'asset',price:'price',lastprice:'price',change:'change',changepercent:'change',dailychange:'change',volume:'volume',volumeinmillions:'volume',rsi:'rsi',rsi14:'rsi',macd:'macd',macddirection:'macd',trend20:'trend20',above20day:'trend20',trend50:'trend50',above50day:'trend50',volumeratio:'volumeRatio',relativevolume:'volumeRatio'};
  const fields=headers.map(h=>aliases[h]||h);const required=['ticker','name','price','change','volume','rsi','macd','trend20','trend50'];const missing=required.filter(f=>!fields.includes(f));if(missing.length)throw new Error(`Missing CSV columns: ${missing.join(', ')}.`);
  const val=(row,key)=>row[fields.indexOf(key)]??'';const bool=v=>['1','true','yes','positive','up','above'].includes(String(v).toLowerCase());
  const parsed=lines.slice(1).map((line,i)=>{const row=parseLine(line);const rawAsset=String(val(row,'asset')||'stock').toLowerCase();const asset=({equity:'stock',stocks:'stock',stock:'stock',crypto:'crypto',forex:'forex',fx:'forex',commodity:'commodity',commodities:'commodity',index:'index',indices:'index'})[rawAsset]||'stock';const a={ticker:String(val(row,'ticker')).toUpperCase(),name:String(val(row,'name')),asset,price:Number(String(val(row,'price')).replace(/[$,]/g,'')),change:Number(String(val(row,'change')).replace(/[%+,]/g,'')),volume:Number(String(val(row,'volume')).replace(/[,]/g,'')),rsi:Number(val(row,'rsi')),macd:bool(val(row,'macd')),trend20:bool(val(row,'trend20')),trend50:bool(val(row,'trend50')),volumeRatio:Number(val(row,'volumeRatio')||1)};if(!a.ticker||!a.name||['price','change','volume','rsi'].some(key=>String(val(row,key)).trim()==='')||![a.price,a.change,a.volume,a.rsi,a.volumeRatio].every(Number.isFinite)||a.price<=0||a.volume<0||a.rsi<0||a.rsi>100)throw new Error(`Invalid data on CSV row ${i+2}; check numeric values and RSI (0–100).`);return a});
  if(!parsed.length)throw new Error('No asset rows found in CSV.');return parsed;
}
function exportCSV(){const rows=visibleAssets();if(!rows.length){toast('No rows to export for the current filters.');return}const headers=['ticker','name','asset','price','change','volume','rsi','macd','trend20','trend50','volumeRatio','score','signal'];const csv=[headers.join(','),...rows.map(a=>[a.ticker,`"${a.name.replaceAll('"','""')}"`,a.asset,a.price,a.change,a.volume,a.rsi,a.macd,a.trend20,a.trend50,a.volumeRatio,scoreAsset(a),signalFor(a)].join(','))].join('\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));const link=document.createElement('a');link.href=url;link.download='northstar-market-scan.csv';link.click();URL.revokeObjectURL(url);toast(`Exported ${rows.length} scan rows.`)}

function init(){
  const now=new Date();$('#current-date').textContent=new Intl.DateTimeFormat('en-US',{weekday:'short',month:'short',day:'2-digit',timeZone:'UTC'}).format(now).toUpperCase();
  $$('.universe-row').forEach(btn=>btn.addEventListener('click',()=>{$$('.universe-row').forEach(x=>x.classList.remove('selected'));btn.classList.add('selected');activeUniverse=btn.dataset.universe;render()}));
  $$('.filter-chip').forEach(btn=>btn.addEventListener('click',()=>{$$('.filter-chip').forEach(x=>x.classList.remove('active'));btn.classList.add('active');activeSignal=btn.dataset.filter;watchOnly=false;render()}));
  $('#search-input').addEventListener('input',render);
  $('#watch-filter').addEventListener('click',()=>{watchOnly=!watchOnly;if(watchOnly){activeSignal='all';$$('.filter-chip').forEach(x=>x.classList.toggle('active',x.dataset.filter==='all'))}render()});
  $('#signal-filter').addEventListener('click',()=>{const order=['all','bullish','watch','bearish'];const next=order[(order.indexOf(activeSignal)+1)%order.length];activeSignal=next;watchOnly=false;$$('.filter-chip').forEach(x=>x.classList.toggle('active',x.dataset.filter===next));render();toast(`Showing ${next==='all'?'all signals':next+' signals'}.`)});
  $('#sort-button').addEventListener('click',()=>{sortAscending=!sortAscending;$('#sort-button').innerHTML=`Sort: <b>Score ${sortAscending?'↑':'↓'}</b> <span>⌄</span>`;render()});
  $('#asset-rows').addEventListener('click',event=>{const star=event.target.closest('[data-star]');if(star){event.stopPropagation();const ticker=star.dataset.star;watchlist.has(ticker)?watchlist.delete(ticker):watchlist.add(ticker);render();toast(`${ticker} ${watchlist.has(ticker)?'added to':'removed from'} watchlist.`);return}const row=event.target.closest('tr[data-ticker]');if(row)showDetails(row.dataset.ticker)});
  $('#see-signals').addEventListener('click',()=>$('#scanner').scrollIntoView({behavior:'smooth'}));
  $('#refresh-button').addEventListener('click',()=>liveMode?loadLiveScan(false):(render(),toast('Signals recalculated from the current dataset.')));$('#live-button').addEventListener('click',toggleLiveScan);$('#download-button').addEventListener('click',exportCSV);
  $('#csv-upload').addEventListener('change',async event=>{const file=event.target.files[0];if(!file)return;try{if(liveTimer){clearInterval(liveTimer);liveTimer=null}lastLiveSignals=null;assets=parseCSV(await file.text());setFeedState('csv',`${assets.length} imported assets`);watchlist.clear();activeUniverse='all';activeSignal='all';watchOnly=false;$('#search-input').value='';$$('.universe-row').forEach(x=>x.classList.toggle('selected',x.dataset.universe==='all'));$$('.filter-chip').forEach(x=>x.classList.toggle('active',x.dataset.filter==='all'));$('#notice-title').textContent='Imported dataset.';$('#notice-detail').textContent='Your uploaded CSV is analyzed in this browser only. No data is sent to a server. Signals are educational analysis, not investment advice.';render();toast(`Scanned ${assets.length} assets from ${file.name}.`)}catch(error){toast(error.message||'Could not read that CSV file.')}finally{event.target.value=''}});
  $('#dismiss-notice').addEventListener('click',()=>$('#dismiss-notice').closest('.data-notice').remove());
  $('#about-button').addEventListener('click',()=>$('#info-dialog').showModal());$$('.dialog-close').forEach(btn=>btn.addEventListener('click',()=>btn.closest('dialog').close()));$$('dialog').forEach(dialog=>dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close()}));
  $$('.period-button').forEach(btn=>btn.addEventListener('click',()=>{$$('.period-button').forEach(x=>x.classList.remove('active'));btn.classList.add('active');chartPeriod=btn.dataset.period;drawChart()}));
  window.addEventListener('resize',drawChart);document.addEventListener('keydown',event=>{if((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==='k'){event.preventDefault();$('#search-input').focus()}if(event.key==='Escape')$$('dialog[open]').forEach(d=>d.close())});
  render();checkFeedStatus();
}
init();
