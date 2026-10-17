// Automatischer Test für chorspur.html. Aufruf: node test.mjs <http-basis-url> <ausgabeordner>
// Voraussetzung: playwright (global oder lokal), Chromium, ffprobe.
import {chromium} from 'playwright';
import {execFileSync} from 'node:child_process';
import fs from 'node:fs';
const base=process.argv[2]||'http://localhost:8765/chorspur.html', outDir=process.argv[3]||'.';
const url=base+'?test';
const R={};
const exe=process.env.CHROME||undefined;

/* ---- 1. Aufnahmepfad mit Chromium-Fake-Mikrofon ---- */
{
  const b=await chromium.launch({executablePath:exe,args:['--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream','--autoplay-policy=no-user-gesture-required']});
  const c=await b.newContext({permissions:['microphone']}),p=await c.newPage();
  const errs=[];p.on('pageerror',e=>errs.push(String(e)));
  await p.goto(url);
  await p.click('.trk[data-i="0"] [data-a="rec"]');
  await p.waitForFunction(()=>__chorspur.T.rec===0);
  await p.waitForFunction(()=>{const T=__chorspur.T;return __chorspur.ctx().currentTime>T.T0+3.2});
  const stopAt=await p.evaluate(()=>__chorspur.ctx().currentTime);
  const T0=await p.evaluate(()=>__chorspur.T.T0);
  await p.click('.trk[data-i="0"] [data-a="rec"]');
  await p.waitForFunction(()=>__chorspur.tracks[0].buf);
  R.fake=await p.evaluate(()=>{const b=__chorspur.tracks[0].buf,d=b.getChannelData(0);let pk=0,s=0;for(const v of d){pk=Math.max(pk,Math.abs(v));s+=v*v}
    return {dur:b.duration,ch:b.numberOfChannels,sr:b.sampleRate,peak:pk,rms:Math.sqrt(s/d.length)}});
  R.fake.expectedDur=stopAt-T0; R.fake.errors=errs;
  await b.close();
}

/* ---- 2./3. Simulierte Schleife (Mikrofon = eigener Ausgang, 80 ms verzögert), Overdub, Export ---- */
{
  const SIM=80;
  const b=await chromium.launch({executablePath:exe,args:['--autoplay-policy=no-user-gesture-required']});
  const c=await b.newContext({acceptDownloads:true}),p=await c.newPage();
  const errs=[];p.on('pageerror',e=>errs.push(String(e)));
  await p.goto(url);
  await p.evaluate(sim=>{navigator.mediaDevices.getUserMedia=async()=>{const x=__chorspur.ctx(),m=__chorspur.master(),d=x.createDelay(1);d.delayTime.value=sim/1000;const o=x.createMediaStreamDestination();m.connect(d);d.connect(o);return o.stream}},SIM);
  await p.click('#rhythm [data-r="click"]');
  // Messfunktion im Browser: Abweichung der Klicks einer Aufnahme von der Taktposition
  await p.evaluate(()=>{window.dev=(i,beats)=>{
    const buf=__chorspur.tracks[i].buf,d=buf.getChannelData(0),sr=buf.sampleRate,spb=60/90,out=[];
    for(let k=0;k<beats;k++){
      const f=k%4===0?1500:1000,n=Math.round(.05*sr),tpl=new Float32Array(n);
      for(let j=0;j<n;j++){const t=j/sr;tpl[j]=Math.sin(2*Math.PI*f*t)*Math.pow(.001/.35,t/.05)}
      const c0=Math.round(k*spb*sr);let best=0,bl=0;
      for(let l=-Math.round(.12*sr);l<=Math.round(.12*sr);l++){let s=0;for(let j=0;j<n;j++){const q=c0+l+j;if(q>=0&&q<d.length)s+=d[q]*tpl[j]}if(Math.abs(s)>best){best=Math.abs(s);bl=l}}
      out.push(bl/sr*1000);
    }return out}});
  const rec=async(i,secAfter)=>{
    await p.click(`.trk[data-i="${i}"] [data-a="rec"]`);
    await p.waitForFunction(k=>__chorspur.T.rec===k,i);
    await p.waitForFunction(s=>__chorspur.ctx().currentTime>__chorspur.T.T0+s,secAfter);
    await p.click(`.trk[data-i="${i}"] [data-a="rec"]`);
    await p.waitForFunction(k=>__chorspur.tracks[k].buf,i);
  };
  // A: ohne Korrektur
  await rec(0,5.4);
  R.devNoCorr=await p.evaluate(()=>dev(0,7));
  await p.click('.trk[data-i="0"] [data-a="clear"]');
  // B: Kalibrierung, Wert übernehmen
  await p.click('#cal');
  await p.waitForFunction(()=>/Gemessen|Keine Klicks/.test(document.querySelector('#calMsg').textContent),null,{timeout:20000});
  R.calMsg=await p.textContent('#calMsg'); R.latency=await p.evaluate(()=>__chorspur.latency());
  // C: Spur 1 mit Korrektur, Spur 2 darüber
  await rec(0,5.4);
  R.devCorr1=await p.evaluate(()=>dev(0,7));
  await rec(1,5.4);
  R.devCorr2=await p.evaluate(()=>dev(1,7));
  R.errors=errs;
  // Export
  R.expectedDur=await p.evaluate(()=>{const t=__chorspur.tracks;return Math.max(...t.map(x=>x.buf?x.buf.duration:0))+.3});
  const [dl]=await Promise.all([p.waitForEvent('download',{timeout:30000}),p.click('#export')]);
  R.dlName=dl.suggestedFilename();
  const wav=outDir+'/'+R.dlName;await dl.saveAs(wav);
  R.ffprobe=JSON.parse(execFileSync('ffprobe',['-v','error','-show_entries','stream=codec_name,channels,sample_rate,bits_per_sample:format=duration,format_name','-of','json',wav]).toString());
  R.wavBytes=fs.statSync(wav).size;
  await b.close();
}
console.log(JSON.stringify(R,null,1));
