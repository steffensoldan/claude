// Test Anfangston beim Einzählen. Aufruf: node ref-test.mjs <url>
import {chromium} from 'playwright';
const [url]=process.argv.slice(2);
const b=await chromium.launch({executablePath:process.env.CHROME,args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));
await p.goto(url+'?test');
await p.evaluate(()=>{navigator.mediaDevices.getUserMedia=async()=>{const x=__chorspur.ctx(),m=__chorspur.master(),d=x.createDelay(1);d.delayTime.value=.08;const o=x.createMediaStreamDestination();m.connect(d);d.connect(o);return o.stream}});
const R={options:await p.$$eval('#ref option',a=>a.map(o=>o.textContent))};
await p.selectOption('#ref','9'); // A4 = 440 Hz
await p.click('.trk[data-i="0"] [data-a="rec"]');await p.waitForFunction(()=>__chorspur.T.rec===0);
// Mitten im Einzählen: Spitzenfrequenz am Ausgang
await p.waitForFunction(()=>__chorspur.ctx().currentTime>__chorspur.T.T0-1.6);
R.peakHz=await p.evaluate(()=>{const a=__chorspur.an(),f=new Float32Array(a.frequencyBinCount);a.getFloatFrequencyData(f);let k=0;for(let i=1;i<f.length;i++)if(f[i]>f[k])k=i;return Math.round(k*__chorspur.ctx().sampleRate/a.fftSize)});
await p.waitForFunction(()=>__chorspur.ctx().currentTime>__chorspur.T.T0+2);
await p.click('.trk[data-i="0"] [data-a="rec"]');await p.waitForFunction(()=>__chorspur.tracks[0].buf);
// Pegel in der Aufnahme (nur Ton-Nachhall wäre hier sichtbar; Rhythmus ist aus)
R.takePeak=await p.evaluate(()=>{const d=__chorspur.tracks[0].buf.getChannelData(0);let m=0;for(const v of d)m=Math.max(m,Math.abs(v));return m});
R.binHz=await p.evaluate(()=>__chorspur.ctx().sampleRate/__chorspur.an().fftSize);
R.errors=errs;console.log(JSON.stringify(R));await b.close();
