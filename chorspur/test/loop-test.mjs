// Test Loop pro Spur, Rahmen nur beim Einzählen, Export mit Taktzahl. Aufruf: node loop-test.mjs <url> <ausgabeordner>
import {chromium} from 'playwright';
import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
const [url,outDir]=process.argv.slice(2);
const b=await chromium.launch({executablePath:process.env.CHROME,args:['--autoplay-policy=no-user-gesture-required']});
const c=await b.newContext({acceptDownloads:true}),p=await c.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.goto(url+'?test');
await p.evaluate(()=>{navigator.mediaDevices.getUserMedia=async()=>{const x=__chorspur.ctx(),o=x.createMediaStreamDestination();return o.stream}});
const R={ui:{rhythm:await p.$$eval('#rhythm',a=>a.length),count:await p.$$eval('#count button',a=>a.map(x=>x.textContent)),loopOpts:await p.$$eval('.trk[data-i="0"] [data-loop] option',a=>a.map(x=>x.textContent))}};
// 1 Takt bei 90 BPM = 2,667 s, Klick nur am Taktanfang, danach 1 s Überhang (soll abgeschnitten werden)
const sr=44100,len=Math.round(sr*3.667),pcm=new Int16Array(len);
for(let k=0;k<Math.round(.05*sr);k++)pcm[k]=Math.round(20000*Math.sin(2*Math.PI*1000*k/sr)*Math.exp(-k/sr/.012));
for(let k=Math.round(2.9*sr);k<Math.round(2.95*sr);k++)pcm[k]=12000; // Störimpuls nach Takt 1: darf im Loop nicht auftauchen
const h=Buffer.alloc(44);h.write('RIFF',0);h.writeUInt32LE(36+len*2,4);h.write('WAVEfmt ',8);h.writeUInt32LE(16,16);h.writeUInt16LE(1,20);h.writeUInt16LE(1,22);h.writeUInt32LE(sr,24);h.writeUInt32LE(sr*2,28);h.writeUInt16LE(2,32);h.writeUInt16LE(16,34);h.write('data',36);h.writeUInt32LE(len*2,40);
const wav=outDir+'/loop-takt.wav';fs.writeFileSync(wav,Buffer.concat([h,Buffer.from(pcm.buffer)]));
const [fc]=await Promise.all([p.waitForEvent('filechooser'),p.click('.trk[data-i="4"] [data-a="file"]')]);await fc.setFiles(wav);
await p.waitForFunction(()=>__chorspur.tracks[4].buf);
await p.selectOption('.trk[data-i="4"] [data-loop]','1');
R.len=await p.textContent('.trk[data-i="4"] .len');
// Abspielen: läuft über das Spurende hinaus weiter, Rahmen bleibt aus
await p.click('#play');const frames=new Set();
for(let i=0;i<25;i++){await p.waitForTimeout(200);frames.add(await p.$eval('#frame',e=>e.className))}
R.playingAfter5s=await p.evaluate(()=>__chorspur.T.playing);R.framesWhilePlaying=[...frames];
await p.click('#play');
// Aufnahme auf Spur 1: Rahmen blinkt im Einzählen, danach nicht
await p.click('.trk[data-i="0"] [data-a="rec"]');await p.waitForFunction(()=>__chorspur.T.rec===0);
const fc1=new Set(),fc2=new Set();
for(let i=0;i<40;i++){await p.waitForTimeout(100);const [pos,f]=await p.evaluate(()=>[__chorspur.ctx().currentTime-__chorspur.T.T0,document.querySelector('#frame').className]);(pos<0?fc1:fc2).add(f)}
R.framesCountIn=[...fc1];R.framesAfter=[...fc2];
await p.click('.trk[data-i="0"] [data-a="rec"]');await p.waitForFunction(()=>!__chorspur.T.playing);
await p.click('.trk[data-i="0"] [data-a="clear"]');
// Export mit 3 Takten
p.on('dialog',d=>{R.dialog=d.message()+' | Vorgabe '+d.defaultValue();d.accept('3')});
const [dl]=await Promise.all([p.waitForEvent('download'),p.click('#export')]);
const mix=outDir+'/loop-mix.wav';await dl.saveAs(mix);
R.ffprobe=JSON.parse(execFileSync('ffprobe',['-v','error','-show_entries','stream=channels:format=duration','-of','json',mix]).toString());
// Spitzen im Mix finden (Schwelle 0,1), zu Gruppen zusammenfassen
const raw=fs.readFileSync(mix),d=new Int16Array(raw.buffer,raw.byteOffset+44,(raw.length-44)/2),hits=[];let last=-1;
for(let k=0;k<d.length;k+=2){if(Math.abs(d[k])>3000){const t=k/2/sr;if(last<0||t-last>.2)hits.push(+t.toFixed(3));last=t}}
R.hits=hits;R.errors=errs;console.log(JSON.stringify(R,null,1));await b.close();
