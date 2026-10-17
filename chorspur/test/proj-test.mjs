// Test Projekt speichern/öffnen. Aufruf: node proj-test.mjs <url> <opensheetmusicdisplay.min.js> <ausgabeordner>
import {chromium} from 'playwright';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const [url,osmdJs,outDir]=process.argv.slice(2);
const b=await chromium.launch({executablePath:process.env.CHROME,args:['--autoplay-policy=no-user-gesture-required']});
const c=await b.newContext({acceptDownloads:true});
const R={};const errs=[];
async function page(){
  const p=await c.newPage();p.on('pageerror',e=>errs.push(String(e)));
  await p.route('https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.9.9/**',r=>r.fulfill({path:osmdJs,contentType:'text/javascript'}));
  await p.goto(url+'?test');
  await p.evaluate(()=>{navigator.mediaDevices.getUserMedia=async()=>{const x=__chorspur.ctx(),m=__chorspur.master(),d=x.createDelay(1);d.delayTime.value=.08;const o=x.createMediaStreamDestination();m.connect(d);d.connect(o);return o.stream}});
  return p;
}
const snap=p=>p.evaluate(()=>({tracks:__chorspur.tracks.map(t=>({len:t.buf?t.buf.length:0,loop:t.loop,vol:t.vol,mute:t.mute,off:t.off,speed:t.speed,semi:t.semi,part:t.part,
  sum:t.buf?Array.from(t.buf.getChannelData(0)).reduce((a,x)=>a+Math.abs(x),0):0})),bpm:document.querySelector('#bpm').value,
  parts:__chorspur.S.parts,views:__chorspur.S.views.map(v=>v?v.o.Sheet.Instruments.map(i=>i.Visible?1:0).join(''):null)}));
const p1=await page();
const [fc]=await Promise.all([p1.waitForEvent('filechooser'),p1.click('#scoreLoad')]);
await fc.setFiles(path.resolve('../noten/alle-meine-entchen-8stimmen.musicxml'));
await p1.waitForFunction(()=>__chorspur.S.views.filter(Boolean).length===8,null,{timeout:30000});
await p1.selectOption('.trk[data-i="5"] select[data-i]','-1');
await p1.$eval('#bpm',el=>{el.value=100;el.dispatchEvent(new Event('input',{bubbles:true}))});
for(const i of [0,1]){
  await p1.click(`.trk[data-i="${i}"] [data-a="rec"]`);await p1.waitForFunction(k=>__chorspur.T.rec===k,i);
  await p1.waitForFunction(()=>__chorspur.ctx().currentTime>__chorspur.T.T0+3);
  await p1.click(`.trk[data-i="${i}"] [data-a="rec"]`);await p1.waitForFunction(k=>__chorspur.tracks[k].buf,i);
}
await p1.$eval('.trk[data-i="1"] input[data-k="vol"]',el=>{el.value=.5;el.dispatchEvent(new Event('input',{bubbles:true}))});
await p1.$eval('.trk[data-i="1"] input[data-k="off"]',el=>{el.value=-.1;el.dispatchEvent(new Event('input',{bubbles:true}))});
await p1.click('.trk[data-i="1"] [data-a="mute"]');
await p1.selectOption('.trk[data-i="1"] [data-loop]','2');
R.before=await snap(p1);
const [dl]=await Promise.all([p1.waitForEvent('download'),p1.click('#projSave')]);
const zip=path.join(outDir,dl.suggestedFilename());await dl.saveAs(zip);R.zipName=dl.suggestedFilename();
R.unzip=execFileSync('unzip',['-l',zip]).toString().trim().split('\n').slice(-12).join('\n');
execFileSync('unzip',['-o','-q',zip,'-d',path.join(outDir,'proj')]);
R.spur1=JSON.parse(execFileSync('ffprobe',['-v','error','-show_entries','stream=codec_name,channels,sample_rate:format=duration','-of','json',path.join(outDir,'proj','spur1.wav')]).toString());
await p1.close();
const p2=await page();
const [fc2]=await Promise.all([p2.waitForEvent('filechooser'),p2.click('#projOpen')]);
await fc2.setFiles(zip);
await p2.waitForFunction(()=>!__chorspur.T.busy&&__chorspur.tracks[1].buf,null,{timeout:30000});
await p2.waitForFunction(()=>__chorspur.S.views.filter(Boolean).length===7,null,{timeout:30000});
R.after=await snap(p2);
R.note=await p2.textContent('#note');
// Weiterarbeiten: Spur 3 über die geladenen Spuren aufnehmen, dann Mix exportieren
await p2.click('.trk[data-i="2"] [data-a="rec"]');await p2.waitForFunction(()=>__chorspur.T.rec===2);
await p2.waitForFunction(()=>__chorspur.ctx().currentTime>__chorspur.T.T0+3);
await p2.click('.trk[data-i="2"] [data-a="rec"]');await p2.waitForFunction(()=>__chorspur.tracks[2].buf);
R.track3=await p2.evaluate(()=>__chorspur.tracks[2].buf.duration);
p2.on('dialog',d=>{R.dialog=d.defaultValue();d.accept(d.defaultValue())});
const [dl2]=await Promise.all([p2.waitForEvent('download'),p2.click('#export')]);
const mix=path.join(outDir,'mix-nach-projekt.wav');await dl2.saveAs(mix);
R.mix=JSON.parse(execFileSync('ffprobe',['-v','error','-show_entries','stream=channels:format=duration','-of','json',mix]).toString());
R.errors=errs;
const cmp=R.before.tracks.map((t,i)=>{const a=R.after.tracks[i];return {len:t.len===a.len,loop:t.loop===a.loop,vol:t.vol===a.vol,mute:t.mute===a.mute,off:t.off===a.off,part:t.part===a.part,sumRel:t.sum?Math.abs(t.sum-a.sum)/t.sum:0}});
console.log(JSON.stringify({zip:R.zipName,unzip:R.unzip,spur1:R.spur1,bpm:[R.before.bpm,R.after.bpm],views:[R.before.views,R.after.views],cmp,afterTracks:R.after.tracks.map(t=>[t.len,t.loop,t.vol,t.mute,t.off,t.part]),dialog:R.dialog,note:R.note,track3:R.track3,mix:R.mix,errors:R.errors},null,1));
await b.close();
