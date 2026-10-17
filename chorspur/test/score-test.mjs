// Test Notenanzeige + visueller Taktgeber. Aufruf: node score-test.mjs <url> <pfad-zu-opensheetmusicdisplay.min.js> <png-ausgabe>
import {chromium} from 'playwright';
import path from 'node:path';
const [url,osmdJs,png,xml='testsatz.musicxml']=process.argv.slice(2);
const b=await chromium.launch({executablePath:process.env.CHROME,args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage({viewport:{width:390,height:900}});
const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.route('https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.9.9/**',r=>r.fulfill({path:osmdJs,contentType:'text/javascript'}));
await p.goto(url+'?test');
await p.click('#count [data-c="still"]');await p.click('#rhythm [data-r="off"]');
const [fc]=await Promise.all([p.waitForEvent('filechooser'),p.click('#scoreLoad')]);
await fc.setFiles(path.resolve(xml));
await p.waitForFunction(()=>__chorspur.S.steps.length>0,null,{timeout:20000});
const R={steps:await p.evaluate(()=>__chorspur.S.steps),msg:await p.textContent('#scoreMsg'),parts:await p.$$eval('#parts input',a=>a.length)};
R.visibleBefore=await p.evaluate(()=>__chorspur.S.osmd.Sheet.Instruments.map(i=>i.Name+':'+i.Visible));
// Stimme ausblenden
await p.click('#parts label:nth-child(2) input');
R.visibleAfterToggle=await p.evaluate(()=>__chorspur.S.osmd.Sheet.Instruments.map(i=>i.Visible));
// Abspielen: braucht eine Spur oder läuft bis Stopp; Cursor-Index gegen Zeit protokollieren
await p.click('#play');
const samples=[];
for(let i=0;i<12;i++){await p.waitForTimeout(400);samples.push(await p.evaluate(()=>{const c=__chorspur.ctx(),T=__chorspur.T;return {pos:+(c.currentTime-T.T0).toFixed(2),idx:__chorspur.S.idx,dots:[...document.querySelectorAll('#dots i')].map(d=>d.className).join('|')}}))}
R.frame=await p.evaluate(()=>[document.querySelector('#frame').className,getComputedStyle(document.querySelector('#bar')).display]);
await p.screenshot({path:png.replace('.png','-viewport.png')});
await p.evaluate(()=>window.scrollTo(0,500));await p.waitForTimeout(150);
await p.screenshot({path:png.replace('.png','-scrolled.png')});
await p.click('#play');
R.idxAfterStop=await p.evaluate(()=>__chorspur.S.idx);
R.samples=samples;R.errors=errs;
console.log(JSON.stringify(R));
await b.close();
