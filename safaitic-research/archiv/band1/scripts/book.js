const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel,
        PageBreak, BorderStyle } = require("docx");

const SERIF = "Georgia";
const GREY = "8C8C8C";

// ---------- helpers ----------
function line(t, opts={}) {
  return new Paragraph({
    spacing: { line: 288, lineRule: "auto", before: opts.before||0, after: opts.after||0 },
    indent: { left: 480 },
    alignment: AlignmentType.LEFT,
    children: [new TextRun({ text: t, size: opts.size||25, font: SERIF })]
  });
}
function poem(lines, attr) {
  const out = [];
  lines.forEach((l, i) => out.push(line(l, { before: i===0?160:0 })));
  out.push(new Paragraph({
    spacing: { before: 60, after: 360 },
    indent: { left: 480 },
    children: [new TextRun({ text: attr, italics: true, size: 16, color: GREY, font: SERIF })]
  }));
  return out;
}
function heading(roman, title) {
  return [
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      pageBreakBefore: true,
      spacing: { before: 240, after: 80 },
      children: [new TextRun({ text: roman, size: 26, color: GREY, font: SERIF })]
    }),
    new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { before: 0, after: 220 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "B0A48C", space: 8 } },
      children: [new TextRun({ text: title, size: 34, font: SERIF })]
    }),
  ];
}
function epigraph(t) {
  return new Paragraph({
    spacing: { before: 0, after: 420 }, indent: { left: 480 },
    children: [new TextRun({ text: t, italics: true, size: 22, color: "5A5A5A", font: SERIF })]
  });
}
function refrainPage(lines, attr) {
  const out = [ new Paragraph({ pageBreakBefore: true, spacing: { before: 2600 } }) ];
  lines.forEach(l => out.push(new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { line: 360, lineRule: "auto" },
    children: [new TextRun({ text: l, italics: true, size: 30, font: SERIF })]
  })));
  out.push(new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 260 },
    children: [new TextRun({ text: attr, size: 16, color: GREY, font: SERIF })]
  }));
  return out;
}

// ---------- front matter ----------
const children = [];

children.push(new Paragraph({ spacing: { before: 3200 } }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: "Wer dies liest, lebe lang", size: 56, font: SERIF })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 280 },
  children: [new TextRun({ text: "Safaitische Inschriften, nachgedichtet", size: 26, italics: true, color: "5A5A5A", font: SERIF })] }));
children.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 160 },
  children: [new TextRun({ text: "Aus der nordarabischen Steppe · 1. Jh. v. – 4. Jh. n. Chr.", size: 20, color: GREY, font: SERIF })] }));

// Vorwort
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, spacing: { after: 200 },
  children: [new TextRun({ text: "Vorwort", size: 34, font: SERIF })] }));
const vor = [
"Vor zweitausend Jahren ritzten Hirten der syro-arabischen Steppe kurze Sätze in den schwarzen Basalt: wer sie waren, wen sie liebten, wen sie verloren, in welchem Jahr es schneite. Kein Werk war beabsichtigt, nur ein Innehalten am Wegrand. Aus rund 38.000 erhaltenen Inschriften wurden hier wenige Dutzend ausgewählt und ins Deutsche nachgedichtet.",
"Jede Zeile hat einen weiten Weg hinter sich: beschädigter Stein, philologische Lesung, englische Übersetzung, und nun deutsche Nachdichtung. Das ist kein Mangel, sondern der eigentliche Gegenstand dieses Bandes. Was hier berührt, berührt uns — die Auswahl folgt unserem Ohr, nicht dem ihren. Sie sagt darum mehr über die Lesenden als über die Zeit, aus der sie stammt.",
"Geordnet ist der Band nach dem Jahr der Steppe: Dürre und Lager, Wege und Wasser, Spähen, Weide, Raub, Krankheit, Tod, Klage, Angst, Sehnsucht, die Zeichen am Himmel — und zuletzt das Jahr selbst, an dem alles gemessen wurde. Dazwischen kehrt, wie ein Rad, die Formel wieder, mit der so viele Steine schließen: ein Fluch gegen das Auslöschen, ein Segen für den, der liest. Wir sind der, den sie meinten.",
];
vor.forEach(p => children.push(new Paragraph({ spacing: { after: 200, line: 312, lineRule: "auto" },
  alignment: AlignmentType.JUSTIFIED, children: [new TextRun({ text: p, size: 23, font: SERIF })] })));

// ---------- sections ----------
function section(roman, title, epi, poems, refrainBefore) {
  if (refrainBefore) refrainBefore.forEach(p => children.push(p));
  heading(roman, title).forEach(p => children.push(p));
  children.push(epigraph(epi));
  poems.forEach(pm => poem(pm[0], pm[1]).forEach(p => children.push(p)));
}

section("I", "Dürre & Lager", "Die Zeit der späten Regen — und wenn sie ausbleibt.", [
 [["Ich blieb das Tal hindurch,","durch die Zeit der späten Regen,","und weinte um den,","den ich liebte."], "Quellsigle SSWS 6"],
 [["Ich trieb die Herde.","Es regnete.","Ich blieb, bis die späten Regen gingen."], "Quellsigle NSR 64.2"],
 [["Der Winter brachte keinen Regen","in dem Jahr, als Wdn floh.","Baalschamin —","nimm mir die Angst und das Nichtwissen."], "Quellsigle Is.Mu 88"],
 [["Ich lagerte am Wasser,","trug Trauer,","und brauchte Hilfe."], "Quellsigle RWQ 117"],
 [["Der Kummer um S²r","nahm mir den Verstand.","Hier, am bleibenden Wasser,","schlug ich mein Lager."], "Quellsigle C 3962"],
 [["Mit ein paar Ziegen","in die innere Wüste,","dann, als die späten Regen kamen,","die Hänge dieses Tals."], "Quellsigle C 4772"],
]);

section("II", "Wege & Wasser", "Heimkehr zur Tränke, quer durch die Wüste.", [
 [["Zurück zum Wasser.","Der Weg reichte bis in den Hauran.","Und ich sehnte mich","nach einem, den ich liebte."], "Quellsigle C 99"],
 [["Ich kam zurück zur Tränke","im Jahr des Wassers,","räumte den Teich von Stein und Erde,","sammelte das Wasser im Nisan.","Der Regen füllte den Teich.","Ringsum war alles kahl."], "Quellsigle ASWS 202"],
 [["Ich trieb die Kamele durchs Tal","und kam ans Wasser,","an ein Becken."], "Quellsigle KRS 3288"],
 [["Ich trauerte um Mʿn.","Der Kummer machte mich wahnsinnig.","Dann begrub ich ihn."], "Quellsigle AMSI 26"],
 [["Die Reiter fanden sich wieder,","als der Steinbock aufging —","er war heimgekehrt,","quer durch die Wüste."], "Quellsigle C 4276"],
 [["Allat, Baalschamin, Schaihaqaum —","bringt mir den Geliebten zurück."], "Quellsigle BS 209"],
]);

section("III", "Spähen & Warten", "Vom Aussichtspunkt aus: nach der Weide, nach den Brüdern.", [
 [["Am Späherplatz.","Ein Wolf trug den Hund davon."], "Quellsigle WH 1516"],
 [["Ich hielt Wache dies Jahr","und sehnte mich nach Ṣḥ, nach Ms¹kt.","Baalschamin —","schick die Winde mit Regen."], "Quellsigle RSIS 204"],
 [["Ich war an diesem Ort","und hielt Ausschau nach den Brüdern.","Sie fehlten mir."], "Quellsigle RSIS 110"],
 [["Zwei junge Kamelstuten.","Ich spähte nach der Frühjahrsweide","und trauerte um den Großvater."], "Quellsigle WH 402"],
 [["Ich weidete die Kamele","auf dem Frühjahrsgras,","im Jahr, als Rhy gegen die Nabatäer stritt,","und hielt Ausschau nach den Hwlt."], "Quellsigle C 2670"],
 [["Ich hielt Ausschau","nach der Geliebten.","Jaʾlat — gib Sicherheit."], "Quellsigle Is.Mu 255"],
]);

section("IV", "Weide & Herde", "Nach dem Regen das satte Gras — und doch der Verlust.", [
 [["Ich trug Trauer um den Bruder,","den das Schicksal fällte.","Zurück zum Wasser, die Schafe nur noch Knochen —","das Jahr, als die Karawane des Königs verhungerte."], "Quellsigle C 3064"],
 [["Ich schlug die stinkende Stute","und hielt ein —","sie zitterte vor Angst."], "Quellsigle WH 1234"],
 [["Die junge Kamelstute.","Ich ließ die Herde frei","über die offene Wüste,","ins satte Gras nach dem Regen."], "Quellsigle C 2363"],
 [["Ich kam ans Wasser","und weidete die Schafe,","als die Sonne im Widder stand."], "Quellsigle AAEK 244"],
 [["Ich weidete die Schafe","und trauerte um die Mutter."], "Quellsigle WH 2036"],
 [["Die junge Kamelstute.","Und ich weinte vor Kummer."], "Quellsigle AbaNS 679"],
], refrainPage(["Wer die Schrift achtet —","dem Sicherheit und Fülle."], "wiederkehrende Schlussformel · nach RSIS 110"));

section("V", "Raub & Krieg", "Pferde aus dem Hauran, und die Furcht vor dem Feind.", [
 [["Ich trieb die Pferde fort,","aus dem Hauran, im Überfall,","und nahm die Kamelstute mit zum Wasser."], "Quellsigle TaSTF 5"],
 [["Ich hütete die Kamele","und fürchtete den Feind.","Gad-ʿAud — gib Sicherheit."], "Quellsigle RR 21"],
 [["Ich kam ans Brunnenwasser","in dem Jahr,","als die Palmyrener Krieg führten."], "Quellsigle Al-Namārah.H 61"],
 [["Ich trauerte um den Bruder,","den das Schicksal beugte,","und sah die Verwüstung","im Jahr, als ʿwḏs Sippe Krieg gegen sie führte."], "Quellsigle NST 3"],
 [["Ich weidete das Tal","auf einem Raubzug,","im Jahr, als Mʿn erschlagen wurde."], "Quellsigle LP 297"],
]);

section("VI", "Krankheit & Versehrung", "Der Schmerz, gezählt nach den Sternbildern.", [
 [["Zum Wasser, scheu vor der Dürre.","Dann der Wassermann, der Widder,","die Waage, die Waage noch einmal.","Zwei Jahre lang Schmerz —","um einen, den ich liebte,","um die Kamele, die ich trieb,","fort aus der inneren Wüste.","Das Jahr, in dem Bnt starb."], "Quellsigle ASWS 73"],
 [["Ich fand die Inschrift des ʾnʿm","und der Schmerz fiel über mich.","Das Jahr, als die Nabatäer","an dieser Tränke vorüberzogen."], "Quellsigle LP 4"],
 [["Ich fand die Schrift eines Geliebten","und trug den Schmerz um ʿwḏ."], "Quellsigle KRS 1828"],
 [["Maʾrat.","Sie trug den Schmerz.","Sie weinte."], "Quellsigle C 5142 · eine der wenigen Frauenstimmen"],
 [["Ich trug den Schmerz um meine Söhne","und kam ans Wasser dieses Tals,","als der Skorpion aufging."], "Quellsigle AWS 82"],
 [["Ich suchte Weide","auf steinigem Grund."], "Quellsigle KRS 775"],
]);

section("VII", "Tod & Gewalt", "Zu früh dahin, vom Schicksal gebeugt.", [
 [["Ich trauerte um ʿqrb,","und diese Trauer hört nicht auf,","und denen, die bleiben:","Verzweiflung."], "Quellsigle KRS 7"],
 [["Der Kummer zerbrach mich —","um Whbʾl, um den Geliebten,","gesund noch eben,","zu früh dahin,","vom Schicksal gebeugt."], "Quellsigle RM.A 7"],
 [["Ich baute das Mal","und trauerte um Hnʾ, zu früh dahin,","um Gls¹,","um den Vater."], "Quellsigle HCH 12"],
 [["Ich trauerte um einen, den ich liebte,","im Jahr, als Mʿz erschlagen wurde."], "Quellsigle HaNSB 335"],
 [["Ich trauerte um den Vater,","den sie erschlugen,","und sehnte mich nach dem Oheim."], "Quellsigle LP 235"],
 [["Ich trauerte um die Gefährten","im Jahr, als Kmn fiel.","Dann weidete ich die innere Wüste","und hütete die Kamele."], "Quellsigle WH 1198"],
], refrainPage(["Wer dies liest und laut spricht —","dem Beute.","Wer dies verdunkelt —","den werfe ein Geliebter aus dem Grab."], "wiederkehrende Schlussformel · nach Al-Namārah.H 61"));

section("VIII", "Klage", "Eine Spur, eine alte Schrift — und das Weinen.", [
 [["Ich fand den Geliebten —","und weinte."], "Quellsigle C 2036"],
 [["Ich fand die Spur des Großvaters","und weinte","am Steinmal."], "Quellsigle C 3140"],
 [["Ich weinte, ich trauerte","um den Vater, den sie ermordeten.","Ich sehnte mich nach dem Oheim","und allen Gefährten.","Wer dies austilgt: erblinde."], "Quellsigle LP 243"],
 [["Ich fand die Schrift des Ms¹k","und weinte,","und die Trauer legte sich über mich.","Ich dachte an den Bruder, den sie fortführten,","und wurde schwer."], "Quellsigle KRS 17"],
 [["Ich weinte","vor Kummer um den Bruder."], "Quellsigle CSNS 618"],
 [["Ḥlb.","Und er weinte vor Kummer."], "Quellsigle WH 1501.2 · fragmentarisch"],
]);

section("IX", "Angst", "In Not, und in Sorge um einen, den man liebt.", [
 [["Ich war in Sorge","um einen, den ich liebte."], "Quellsigle WH 636"],
 [["Ich weidete am Wasserlauf,","zog mit dem Stamm","und hatte Angst.","Lass mich sicher sein."], "Quellsigle KRS 1949"],
 [["Ich hatte Angst","vor meinem eigenen Wahn."], "Quellsigle WH 2294"],
 [["Nasr —","hilf dem, der liebt,","und nimm die Not."], "Quellsigle MKJS 80"],
 [["Ich bin in Not."], "Quellsigle WH 3810"],
 [["Ohne Krankheit,","ohne Ohnmacht,","ohne Not —","sie hat ihn um den Verstand gebracht."], "Quellsigle KJB 138"],
]);

section("X", "Sehnsucht & Heimweh", "Der Himmel regnet — nach langer Zeit.", [
 [["Hier.","Und der Himmel regnete,","nach langer Zeit ohne Regen."], "Quellsigle RWQ 342"],
 [["Ich sehnte mich nach S¹mʿt.","Allat —","gib Sicherheit, gib Annahme."], "Quellsigle WH 2339"],
 [["Ich dachte an mein Lamm,","das der Wolf geraubt hat.","Baalschamin — mach das Lagern leicht.","Wer dies austilgt: erblinde.","Wer dies liest: lebe lang."], "Quellsigle C 4803"],
 [["Allat —","schenk langes Leben","dem Bruder Kʿmh."], "Quellsigle LP 1267"],
], refrainPage(["Wer dies unversehrt lässt —","dem sei Sicherheit."], "wiederkehrende Schlussformel · nach C 2770"));

section("XI", "Zeichen & Seltsames", "Schnee, Sturzflut, der Löwe an der Nordseite.", [
 [["Hier fiel Schnee,","als der Skorpion aufging."], "Quellsigle C 3818"],
 [["Ich weidete das Tal,","und Schnee fiel","im Untergang des Wassermanns."], "Quellsigle KRS 2851"],
 [["Ich wartete auf die Regen","und auf den Abendstern."], "Quellsigle KnGQ 1"],
 [["Die Sturzflut","ging über alles hin."], "Quellsigle HaNSB 334"],
 [["Ich bezwang den Löwen,","dann kehrte ich zurück","zum bleibenden Wasser."], "Quellsigle HaNSB 333"],
 [["Ich war hier","und sah den Löwen","an der Nordseite."], "Quellsigle RWQ 187"],
]);

section("XII", "Das Jahr, in dem", "Alles wird an einem Jahr gemessen: dem Schnee, der Dürre, dem König.", [
 [["Ich weidete das Tal,","mit dem Stamm unterwegs,","im Jahr des Schnees."], "Quellsigle RWQ 341"],
 [["Ich kam heil ans Wasser,","mit den Ziegen,","im Jahr des Aufstands."], "Quellsigle ASWS 59"],
 [["Ich weidete","im Jahr der Dürre.","Schaqim — halte das Unglück fern."], "Quellsigle KRS 1009"],
 [["Ich trauerte um den Vater","und um die kleine Schwester","im Jahr des Tigers."], "Quellsigle AWS 81"],
 [["Ich trauerte um die Schwester","und ritt zur Verfolgung aus,","im Jahr des Königs Rabbel."], "Quellsigle ISB 57"],
 [["Ich weidete","im Jahr der Fluten."], "Quellsigle KRS 2916"],
]);

// envoi
refrainPage(["Wer dies austilgt: erblinde.","Wer dies liest: lebe lang."], "Schlussformel · nach C 4803").forEach(p => children.push(p));

// colophon
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, spacing: { after: 160 },
  children: [new TextRun({ text: "Zu den Quellen", size: 30, font: SERIF })] }));
const col = [
"Grundlage sind die englischen Editionen des OCIANA-Korpus (Online Corpus of the Inscriptions of Ancient North Arabia). Jede Nachdichtung trägt die Quellsigle der zugrunde liegenden Inschrift; darüber ist der Originaleintrag mit Transliteration, Übersetzung und Fundort auffindbar.",
"Die Auswahl entstand aus 2.487 erzählenden (nicht bloß anrufenden) Inschriften, verdichtet nach literarischen Kriterien: Bild, Affekt, Knappheit, Seltenheit, Lesbarkeit. Sie ist bewusst kuratiert und nicht repräsentativ.",
"Eigennamen folgen, wo sie stehen blieben, der wissenschaftlichen Umschrift. Lücken im Stein sind in den Nachdichtungen geglättet; die Originale zeigen sie offen.",
];
col.forEach(p => children.push(new Paragraph({ spacing: { after: 160, line: 300, lineRule: "auto" },
  alignment: AlignmentType.JUSTIFIED, children: [new TextRun({ text: p, size: 20, color: "404040", font: SERIF })] })));

// ---------- document ----------
const doc = new Document({
  styles: { default: { document: { run: { font: SERIF, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: SERIF, bold: false }, paragraph: { outlineLevel: 0 } } ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 1700, bottom: 1700, left: 2100, right: 2100 } } },
    children
  }]
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync("/mnt/user-data/outputs/safaitic_gedichtband.docx", b); console.log("written", b.length, "bytes"); });
