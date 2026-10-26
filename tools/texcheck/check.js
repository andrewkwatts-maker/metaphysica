'use strict';
// LaTeX render gate. Usage: node check.js <inputs...>   (files or directories)
// Prints {checked, errors:[{surface,where,id,latex,error}]}; exit 1 on any error.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const {mathjax} = require('mathjax-full/js/mathjax.js');
const {TeX} = require('mathjax-full/js/input/tex.js');
const {liteAdaptor} = require('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler} = require('mathjax-full/js/handlers/html.js');
const {SerializedMmlVisitor} = require('mathjax-full/js/core/MmlTree/SerializedMmlVisitor.js');

const CONFIG_FILE = path.resolve(__dirname, '../../src/metaphysica/website/js/mathjax-config.js');
// tex-mml-chtml's TeX package set. The autoload extensions are loaded statically
// (the real page loads each on first use). bussproofs is left out: it needs a
// browser-side document and no published formula uses prooftree.
const BASE_PACKAGES = ['base', 'ams', 'newcommand', 'noundefined', 'require', 'autoload', 'configmacros'];
const AUTOLOAD_PACKAGES = ['action', 'amscd', 'bbox', 'boldsymbol', 'braket', 'cancel', 'color',
  'enclose', 'extpfeil', 'html', 'mhchem', 'unicode', 'verb'];
const PACKAGE_MODULES = {
  base: 'base/BaseConfiguration', ams: 'ams/AmsConfiguration',
  newcommand: 'newcommand/NewcommandConfiguration', noundefined: 'noundefined/NoUndefinedConfiguration',
  require: 'require/RequireConfiguration', autoload: 'autoload/AutoloadConfiguration',
  configmacros: 'configmacros/ConfigMacrosConfiguration', action: 'action/ActionConfiguration',
  amscd: 'amscd/AmsCdConfiguration', bbox: 'bbox/BboxConfiguration',
  boldsymbol: 'boldsymbol/BoldsymbolConfiguration', braket: 'braket/BraketConfiguration',
  cancel: 'cancel/CancelConfiguration', color: 'color/ColorConfiguration',
  enclose: 'enclose/EncloseConfiguration', extpfeil: 'extpfeil/ExtpfeilConfiguration',
  html: 'html/HtmlConfiguration', mhchem: 'mhchem/MhchemConfiguration',
  unicode: 'unicode/UnicodeConfiguration', verb: 'verb/VerbConfiguration',
  physics: 'physics/PhysicsConfiguration',
};
const MATH_RX = new RegExp(
  String.raw`\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]|\\\(([\s\S]+?)\\\)|(?<![\\$])\$([^$\n]+?)\$`, 'g');
const ENTITIES = {amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' '};

function loadSiteConfig(file = CONFIG_FILE) {
  const win = {};
  vm.runInNewContext(fs.readFileSync(file, 'utf8'), {window: win}, {filename: file});
  if (!win.MathJax || !win.MathJax.tex) throw new Error('config defines no MathJax.tex: ' + file);
  return win.MathJax;
}

function extraPackages(cfg) {
  const load = (cfg.loader && cfg.loader.load) || [];
  return load.map(n => n.replace(/^\[tex\]\//, ''));
}

function requirePackages(pkgs) {
  for (const p of pkgs) {
    if (!PACKAGE_MODULES[p]) throw new Error('unknown TeX package in config: ' + p);
    require('mathjax-full/js/input/tex/' + PACKAGE_MODULES[p] + '.js');
  }
}

// MathJax's base \text keeps `_` and `^` literal, so they print as stray characters.
const TEXT_CMD_RX = /\\(?:text|textrm|textit|textbf|mbox)\{/g;

// The first \text{...} argument (balanced braces) holding an unescaped `_` or `^`, else null.
function strayScript(latex) {
  for (const m of latex.matchAll(TEXT_CMD_RX)) {
    let depth = 1;
    let i = m.index + m[0].length;
    for (; i < latex.length && depth > 0; i++) {
      const c = latex[i];
      if (c === '\\') { i++; continue; }
      if (c === '{') depth++;
      else if (c === '}') depth--;
      else if ((c === '_' || c === '^') && depth > 0) return latex.slice(m.index, i + 8);
    }
  }
  return null;
}

// Returns null when the string renders, else a short error message.
function convertOne(doc, vis, latex) {
  const stray = strayScript(latex);
  if (stray) return 'script character inside text: ' + stray.slice(0, 80);
  let mml;
  try {
    mml = vis.visitTree(doc.convert(latex, {display: true}));
  } catch (e) {
    return String((e && e.message) || e).slice(0, 160);
  }
  if (mml.includes('<merror')) return 'merror ' + ((mml.match(/data-mjx-error="([^"]*)"/) || [, ''])[1]);
  const red = mml.match(/mathcolor="red"[^>]*>([^<]*)/);
  return red ? 'undefined macro ' + red[1] : null;
}

function makeConverter(cfg = loadSiteConfig()) {
  RegisterHTMLHandler(liteAdaptor());
  const pkgs = [...BASE_PACKAGES, ...AUTOLOAD_PACKAGES, ...extraPackages(cfg)];
  requirePackages(pkgs);
  const opts = Object.assign({}, cfg.tex, {packages: pkgs, formatError: (jax, err) => { throw err; }});
  const doc = mathjax.document('', {InputJax: new TeX(opts)});
  const vis = new SerializedMmlVisitor();
  return latex => convertOne(doc, vis, latex);
}

function decodeEntities(s) {
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
    if (e[0] === '#') {
      const hex = e[1].toLowerCase() === 'x';
      return String.fromCodePoint(hex ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10));
    }
    const key = e.toLowerCase();
    return Object.prototype.hasOwnProperty.call(ENTITIES, key) ? ENTITIES[key] : m;
  });
}

function* delimitedMath(text) {
  for (const m of text.matchAll(MATH_RX)) yield m[1] || m[2] || m[3] || m[4];
}

function* formulaStrings(file) {
  const data = JSON.parse(fs.readFileSync(file, 'utf8')).formulas || {};
  for (const [id, f] of Object.entries(data))
    for (const key of ['latex', 'eml_latex', 'arithma_latex'])
      if (f && f[key]) yield {where: id + ':' + key, id, latex: f[key]};
}

// pm-paper-renderer.js treats a block's `content` as raw TeX only when it contains one of
// these commands; anything else goes through its Unicode-to-LaTeX converter and is skipped.
const RAW_TEX_RX = /\\(frac|alpha|beta|gamma|text|left|right|sum|int|sqrt|quad|begin|end|partial|nabla|infty|times|pm|cdot|leq|geq|neq|approx)\b/;
const CAPTION_RX = /(?:\n|^)\s*[\u2014\u2013-]\s*[^\n]+$/;

// The TeX string the paper renderer would hand to MathJax for a block, or null.
function blockTeX(node) {
  if (typeof node.latex === 'string' && node.latex) return node.latex;
  if (typeof node.content !== 'string') return null;
  const body = node.content.replace(CAPTION_RX, '');
  return RAW_TEX_RX.test(body) ? body : null;
}

// Depth-first over a section; `contentBlocks` duplicates `content_blocks`, so skip it.
function* mathBlocks(node, trail) {
  if (Array.isArray(node)) {
    for (const [i, v] of node.entries()) yield* mathBlocks(v, trail + '[' + i + ']');
  } else if (node && typeof node === 'object') {
    const tex = ['formula', 'equation'].includes(node.type) ? blockTeX(node) : null;
    if (tex) yield {trail, latex: tex};
    for (const [k, v] of Object.entries(node))
      if (k !== 'contentBlocks' && v && typeof v === 'object') yield* mathBlocks(v, trail + '.' + k);
  }
}

function* sectionStrings(file) {
  const secs = JSON.parse(fs.readFileSync(file, 'utf8')).sections || {};
  for (const [sid, sec] of Object.entries(secs))
    for (const b of mathBlocks(sec, ''))
      yield {where: sid + b.trail, id: sid, latex: b.latex};
}

function* htmlStrings(file) {
  const raw = fs.readFileSync(file, 'utf8').replace(/<script[\s\S]*?<\/script>/g, '');
  let i = 0;
  for (const tex of delimitedMath(decodeEntities(raw)))
    yield {where: path.basename(file) + '#' + (i++), id: '', latex: tex};
}

function surfaceOf(file) {
  const b = path.basename(file);
  if (b === 'formulas.json') return 'formulas';
  if (b === 'sections.json') return 'sections';
  return b.endsWith('.html') ? 'html' : 'unknown';
}

function* stringsOf(file) {
  const kind = surfaceOf(file);
  if (kind === 'formulas') yield* formulaStrings(file);
  else if (kind === 'sections') yield* sectionStrings(file);
  else if (kind === 'html') yield* htmlStrings(file);
  else throw new Error('unsupported input: ' + file);
}

function expand(inputs) {
  const out = [];
  const walk = d => fs.readdirSync(d, {withFileTypes: true}).forEach(e => {
    const q = path.join(d, e.name);
    if (e.isDirectory()) walk(q); else if (e.name.endsWith('.html')) out.push(q);
  });
  for (const p of inputs) {
    if (!fs.existsSync(p)) throw new Error('no such input: ' + p);
    if (fs.statSync(p).isDirectory()) walk(p); else out.push(p);
  }
  return out;
}

function run(inputs, convert) {
  const errors = [];
  let checked = 0;
  for (const file of expand(inputs)) {
    for (const item of stringsOf(file)) {
      checked++;
      const error = convert(item.latex);
      if (error) errors.push({surface: surfaceOf(file), where: item.where, id: item.id, latex: item.latex, error});
    }
  }
  errors.sort((a, b) => (a.surface + a.where).localeCompare(b.surface + b.where));
  return {checked, errors};
}

function main(argv) {
  if (argv.length === 0) {
    console.error('usage: node check.js <formulas.json|sections.json|html|dir>...');
    return 2;
  }
  const result = run(argv, makeConverter());
  console.log(JSON.stringify(result, null, 1));
  return result.errors.length ? 1 : 0;
}

if (require.main === module) process.exitCode = main(process.argv.slice(2));
module.exports = {makeConverter, run, loadSiteConfig};
