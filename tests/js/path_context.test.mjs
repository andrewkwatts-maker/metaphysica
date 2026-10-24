// node --test tests/js/path_context.test.mjs  (plain node:test, no dependencies)
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { createHash } from 'node:crypto';

const require = createRequire(import.meta.url);
const core = require('../../src/metaphysica/website/js/pm-path-context.js');

const sha = async (buf) => createHash('sha256').update(Buffer.from(buf)).digest('hex');
const dec = (b) => Buffer.from(b).toString('utf8');

test('applyPatch: add, remove and replace', () => {
  const doc = { a: { b: 1, list: [1, 2, 3] }, keep: true };
  const out = core.applyPatch(doc, [
    { op: 'replace', path: '/a/b', value: 9 },
    { op: 'add', path: '/a/list/1', value: 7 },
    { op: 'add', path: '/a/list/-', value: 4 },
    { op: 'add', path: '/a/new', value: 'x' },
    { op: 'remove', path: '/keep' },
  ]);
  assert.deepEqual(out, { a: { b: 9, list: [1, 7, 2, 3, 4], new: 'x' } });
  assert.equal(doc.a.b, 1, 'input is not mutated');
});

test('applyPatch: pointer unescape (~1 then ~0)', () => {
  assert.equal(core.unescapePointer('a~1b~0c'), 'a/b~c');
  assert.equal(core.unescapePointer('~01'), '~1');
  const out = core.applyPatch({ 'a/b': { '~x': 1 } }, [{ op: 'replace', path: '/a~1b/~0x', value: 2 }]);
  assert.deepEqual(out, { 'a/b': { '~x': 2 } });
});

test('applyPatch: bad ops throw', () => {
  assert.throws(() => core.applyPatch({ a: 1 }, [{ op: 'replace', path: '/zzz', value: 1 }]));
  assert.throws(() => core.applyPatch({ a: 1 }, [{ op: 'move', path: '/a', from: '/b' }]));
  assert.throws(() => core.applyPatch({ l: [1] }, [{ op: 'remove', path: '/l/5' }]));
});

test('selection precedence: query, then storage, then main; unknown -> main', () => {
  const known = ['main', 'f--o', 'g--p'];
  assert.equal(core.chooseId('?path=f--o', 'g--p', known), 'f--o');
  assert.equal(core.chooseId('', 'g--p', known), 'g--p');
  assert.equal(core.chooseId('', null, known), 'main');
  assert.equal(core.chooseId('?path=nope--x', 'g--p', known), 'g--p');
  assert.equal(core.chooseId('?path=Bad Id', null, known), 'main');
  assert.equal(core.chooseId('?path=main', 'g--p', known), 'main');
});

test('selection: engine option ids may contain capitals', () => {
  const known = ['main', 'n_gen_source--b3_over_dim_O'];
  assert.equal(core.chooseId('?path=n_gen_source--b3_over_dim_O', null, known),
    'n_gen_source--b3_over_dim_O');
});

test('overlay: matching sha applies the patch', async () => {
  const bytes = Buffer.from(JSON.stringify({ v: 1 }));
  const entry = { base_sha256: await sha(bytes), ops: [{ op: 'replace', path: '/v', value: 2 }] };
  const res = await core.resolveOverlay(bytes, entry, sha, dec);
  assert.equal(res.ok, true);
  assert.deepEqual(JSON.parse(res.text), { v: 2 });
});

test('overlay: sha mismatch is refused (caller serves the base)', async () => {
  const bytes = Buffer.from(JSON.stringify({ v: 1 }));
  const entry = { base_sha256: '0'.repeat(64), ops: [{ op: 'replace', path: '/v', value: 2 }] };
  const res = await core.resolveOverlay(bytes, entry, sha, dec);
  assert.equal(res.ok, false);
});

test('overlay: no crypto.subtle (sha unavailable) counts as a mismatch', async () => {
  const bytes = Buffer.from('{"v":1}');
  const res = await core.resolveOverlay(bytes, { base_sha256: 'abc', ops: [] }, async () => null, dec);
  assert.equal(res.ok, false);
});

test('overlay: a failing op falls back instead of throwing', async () => {
  const bytes = Buffer.from('{"v":1}');
  const entry = { base_sha256: await sha(bytes), ops: [{ op: 'replace', path: '/gone', value: 1 }] };
  const res = await core.resolveOverlay(bytes, entry, sha, dec);
  assert.equal(res.ok, false);
});
