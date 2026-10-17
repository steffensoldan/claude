// Test Notenanzeige pro Spur + Taktsignal. Aufruf: node score-test.mjs <url> <opensheetmusicdisplay.min.js> <png> [musicxml]
import {chromium} from 'playwright';
import path from 'node:path';
const [url,osmdJs,png,xml='../noten/alle-meine-entchen.musicxml']=process.argv.slice(2);
const b=await chromium.launch({executablePath:process.env.CHROME,args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage({viewport:{width:390,height:900}});
const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.route('https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.9.9/**',r=>r.fulfill({path:osmdJs,contentType:'text/javascript'}));
await p.goto(url+'?test');
const R={tracks:await p.$$eval('.trk',a=>a.length),rhythmBtns:await p.$$eval('#rhythm button',a=>a.map(x=>x.textContent)),
  panSliders:await p.$$eval('[data-k="pan"]',a=>a.length),latencyUI:await p.$$eval('#lat,#cal',a=>a.length)};
const [fc]=await Promise.all([p.waitForEvent('filechooser'),p.click('#scoreLoad')]);
await fc.setFiles(path.resolve(xml));
await p.waitForFunction(()=>__chorspur.S.parts.length>0&&__chorspur.S.views.filter(Boolean).length>=Math.min(4,__chorspur.S.parts.length),null,{timeout:30000});
R.parts=await p.evaluate(()=>__chorspur.S.parts);R.steps=await p.evaluate(()=>__chorspur.S.views.map(v=>v?v.steps.join(' '):null));
R.assign=await p.evaluate(()=>__chorspur.tracks.map(t=>t.part));
R.visiblePerView=await p.evaluate(()=>__chorspur.S.views.map(v=>v?v.o.Sheet.Instruments.map(x=>x.Visible?1:0).join(''):null));
R.boxesShown=await p.$$eval('.trk',a=>a.map(c=>!c.querySelector('.sheetBox').hidden));
R.headers=await p.$$eval('.trk h3',a=>a.map(x=>x.textContent));
// Spur 5 auf Notenstimme 2 umstellen
await p.selectOption('.trk[data-i="4"] select[data-i]','1');
await p.waitForFunction(()=>__chorspur.S.views[4]);
R.view5=await p.evaluate(()=>__chorspur.S.views[4].o.Sheet.Instruments.map(x=>x.Visible?1:0).join(''));
await p.selectOption('.trk[data-i="4"] select[data-i]','-1');
await p.click('#play');
const samples=[];
for(let i=0;i<10;i++){await p.waitForTimeout(400);samples.push(await p.evaluate(()=>{const c=__chorspur.ctx(),T=__chorspur.T;return {pos:+(c.currentTime-T.T0).toFixed(2),t:__chorspur.S.views.filter(Boolean).map(v=>v.steps[v.idx]).join(',')}}))}
R.samples=samples;
await p.evaluate(()=>document.querySelector('.trk[data-i="1"]').scrollIntoView());await p.waitForTimeout(100);
await p.screenshot({path:png});
await p.click('#play');
R.errors=errs;
console.log(JSON.stringify(R,null,0));
await b.close();
