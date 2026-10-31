// node --test tests/js/paths_glow.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';

const glow = createRequire(import.meta.url)('../../src/metaphysica/website/js/pm-paths-glow.js');
const opt = (attrs) => ({ type: 'option', label: 'b', attrs: { fork: 'a', ...attrs } });

test('a reasonable alternative gets the glow class, the gold path does not', () => {
  assert.equal(glow.glowClass(opt({ reasonable: true, rank: 2 })), ' pp-reasonable');
  assert.equal(glow.glowClass(opt({ reasonable: true, on_active_path: true })), '');
  assert.equal(glow.glowClass(opt({})), '');
});

test('the inspector rows give rank, delta chi2 and the rule', () => {
  const rows = glow.inspectorRows(opt({ reasonable: true, rank: 2, delta_chi2: 1.234 }), { reasonable_rule: 'rule x' });
  assert.deepEqual(rows.map((r) => r[1]), ['2', '1.23', 'rule x']);
  assert.deepEqual(glow.inspectorRows(opt({}), null), []);
});

test('path-list keys name the reasonable options', () => {
  assert.deepEqual(glow.reasonableOptionKeys([opt({ reasonable: true })]), { 'a--b': true });
});
