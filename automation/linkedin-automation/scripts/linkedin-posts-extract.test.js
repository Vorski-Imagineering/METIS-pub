'use strict';

/**
 * Tests for linkedin-posts-extract.js against mocked activity-feed DOMs.
 *
 * Same harness as linkedin-profile-extract.test.js (jsdom on NODE_PATH):
 *
 *   mkdir -p /tmp/li && cd /tmp/li && npm init -y && npm i jsdom
 *   NODE_PATH=/tmp/li/node_modules node --test \
 *     automation/linkedin-automation/scripts/linkedin-posts-extract.test.js
 */

const test = require('node:test');
const assert = require('node:assert');
const { JSDOM } = require('jsdom');
const P = require('./linkedin-posts-extract.js');

const BLOCK = new Set(['DIV', 'P', 'LI', 'UL', 'OL', 'SECTION', 'ARTICLE', 'H1', 'H2', 'H3', 'H4', 'BR', 'TR', 'SPAN']);

function installInnerText(win) {
  Object.defineProperty(win.HTMLElement.prototype, 'innerText', {
    configurable: true,
    get() {
      const parts = [];
      const walk = node => {
        for (const child of node.childNodes) {
          if (child.nodeType === 3) parts.push(child.textContent.replace(/\s+/g, ' '));
          else if (child.nodeType === 1) {
            const block = BLOCK.has(child.tagName);
            if (block) parts.push('\n');
            walk(child);
            if (block) parts.push('\n');
          }
        }
      };
      walk(this);
      return parts.join('').replace(/[ \t]*\n[ \t]*/g, '\n').replace(/\n{2,}/g, '\n').trim();
    },
  });
}

function dom(html) {
  const d = new JSDOM('<!doctype html><html><body>' + html + '</body></html>');
  installInnerText(d.window);
  return d.window.document;
}

const NOW = Date.UTC(2026, 10, 25); // 2026-11-25
const urnFor = (isoDate, kind) =>
  'urn:li:' + (kind || 'activity') + ':' + (BigInt(Date.parse(isoDate + 'T12:00:00Z')) << 22n).toString();

function card({ urn, actor, age, text, repost, reactions, comments, nested }) {
  return `
  <div data-urn="${urn}">
    ${repost ? '<span>Ada Lovelace reposted this</span>' : ''}
    <div class="update-components-actor__title"><span>${actor}</span></div>
    <span>Founder at Example Co.</span>
    <span>${age} • Edited •</span>
    ${nested ? `<div data-urn="${nested}"><span>inner</span></div>` : ''}
    <div class="update-components-text"><span>${text}</span></div>
    <button>…more</button>
    <span>${reactions || 0} reactions</span><span>${comments || 0} comments</span>
  </div>`;
}

test('activityUrl builds person and company feed URLs and strips query strings', () => {
  assert.strictEqual(P.activityUrl('https://www.linkedin.com/in/ada/?trk=x'),
    'https://www.linkedin.com/in/ada/recent-activity/all/');
  assert.strictEqual(P.activityUrl('https://www.linkedin.com/company/example-co/about/'),
    'https://www.linkedin.com/company/example-co/posts/?feedView=all');
  assert.strictEqual(P.activityUrl('https://example.com/in/ada'), null);
});

test('dateFromUrn decodes the snowflake timestamp', () => {
  assert.strictEqual(P.isoDay(P.dateFromUrn(urnFor('2026-03-14'))), '2026-03-14');
  assert.strictEqual(P.isoDay(P.dateFromUrn(urnFor('2025-12-01', 'ugcPost'))), '2025-12-01');
  assert.strictEqual(P.dateFromUrn('urn:li:activity:123'), null);
  assert.strictEqual(P.dateFromUrn(''), null);
});

test('age labels parse in short and long form', () => {
  assert.strictEqual(P.ageToDays('3mo'), 90);
  assert.strictEqual(P.ageToDays('1yr'), 365);
  assert.strictEqual(P.ageToDays('2w'), 14);
  assert.strictEqual(P.ageToDays('5 days'), 5);
  assert.strictEqual(P.ageToDays('soon'), null);
  assert.strictEqual(P.findAgeLabel('Founder\n3mo • Edited •\nHello'), '3mo');
});

test('parseContainer reads a post card', () => {
  const doc = dom(card({ urn: urnFor('2026-10-01'), actor: 'Ada Lovelace', age: '1mo',
    text: 'We shipped the engine.', reactions: 42, comments: 7 }));
  const p = P.parseContainer(doc.querySelector('[data-urn]'));
  assert.strictEqual(p.date, '2026-10-01');
  assert.strictEqual(p.date_source, 'urn');
  assert.strictEqual(p.kind, 'post');
  assert.strictEqual(p.author, 'Ada Lovelace');
  assert.strictEqual(p.text, 'We shipped the engine.');
  assert.strictEqual(p.reactions, '42');
  assert.strictEqual(p.comments, '7');
  assert.match(p.url, /^https:\/\/www\.linkedin\.com\/feed\/update\/urn:li:activity:\d+\/$/);
});

test('reposts are marked and nested urns are not counted as separate posts', () => {
  const doc = dom(card({ urn: urnFor('2026-09-01'), actor: 'Charles Babbage', age: '2mo',
    text: 'Original thoughts.', repost: true, nested: urnFor('2026-08-30') }));
  const cs = P.postContainers(doc);
  assert.strictEqual(cs.length, 1);
  assert.strictEqual(P.parseContainer(cs[0]).kind, 'repost');
});

test('text fallback splits on "Feed post number N"', () => {
  const doc = dom(`<main>
    <div>Feed post number 1</div><div>Ada Lovelace</div><div>Founder</div><div>2w • </div><div>x</div><div>First post body</div>
    <div>Feed post number 2</div><div>Ada Lovelace</div><div>Founder</div><div>1yr • </div><div>x</div><div>Old post body</div>
  </main>`);
  const posts = P.parseFromText(doc.body.innerText);
  assert.strictEqual(posts.length, 2);
  assert.strictEqual(posts[0].age, '2w');
  assert.strictEqual(posts[0].text, 'First post body');
  assert.strictEqual(posts[1].age, '1yr');
});

test('cutoff is 12 months back by default, or an explicit date', () => {
  assert.strictEqual(P.isoDay(P.cutoffDate({}, NOW)), '2025-11-25');
  assert.strictEqual(P.isoDay(P.cutoffDate({ months: 6 }, NOW)), '2026-05-25');
  assert.strictEqual(P.isoDay(P.cutoffDate({ since: '2026-01-01' }, NOW)), '2026-01-01');
});

test('collect stops once an own post is older than the cutoff, and keeps only posts within it', async () => {
  const doc = dom(`<main id="workspace">
    ${card({ urn: urnFor('2026-11-01'), actor: 'Ada', age: '3w', text: 'Recent' })}
    ${card({ urn: urnFor('2026-02-10'), actor: 'Ada', age: '9mo', text: 'Middle' })}
    ${card({ urn: urnFor('2025-06-01'), actor: 'Ada', age: '1yr', text: 'Too old' })}
  </main>`);
  const r = await P.collect(doc, { reset: true, now: NOW, stepMs: 1, maxMs: 2000 });
  assert.strictEqual(r.mode, 'dom');
  assert.strictEqual(r.found, 3);
  assert.strictEqual(r.reachedCutoff, true);
  assert.strictEqual(r.done, true);
  const kept = P.keptPosts(globalThis.__posts, NOW).map(p => p.text);
  assert.deepStrictEqual(kept, ['Recent', 'Middle']);
});

test('collect gives up after the feed stops growing', async () => {
  const doc = dom(`<main id="workspace">${card({ urn: urnFor('2026-11-01'), actor: 'Ada', age: '3w', text: 'Only one' })}</main>`);
  const r = await P.collect(doc, { reset: true, now: NOW, stepMs: 1, maxMs: 2000, maxStalls: 2 });
  assert.strictEqual(r.found, 1);
  assert.strictEqual(r.reachedCutoff, false);
  assert.strictEqual(r.done, true);
});

test('collect is resumable and does not double-count', async () => {
  const doc = dom(`<main id="workspace">${card({ urn: urnFor('2026-11-01'), actor: 'Ada', age: '3w', text: 'A' })}</main>`);
  await P.collect(doc, { reset: true, now: NOW, stepMs: 1, maxMs: 0 });
  doc.getElementById('workspace').insertAdjacentHTML('beforeend',
    card({ urn: urnFor('2026-10-01'), actor: 'Ada', age: '1mo', text: 'B' }));
  const r = await P.collect(doc, { now: NOW, stepMs: 1, maxMs: 2000, maxStalls: 1 });
  assert.strictEqual(r.found, 2);
});

test('only the per-post "…more" is clicked, never a page-wide one', async () => {
  const doc = dom(`<main id="workspace">
    ${card({ urn: urnFor('2026-11-01'), actor: 'Ada', age: '3w', text: 'A' })}
    <aside><button id="outside">…more</button></aside>
  </main>`);
  let outside = 0;
  doc.getElementById('outside').addEventListener('click', () => outside++);
  await P.collect(doc, { reset: true, now: NOW, stepMs: 1, maxMs: 500, maxStalls: 1 });
  assert.strictEqual(outside, 0);
});

test('payload round-trips and detects truncation', async () => {
  const doc = dom(`<main id="workspace">
    ${card({ urn: urnFor('2026-11-01'), actor: 'Ada', age: '3w', text: 'Line one\nLine two', reactions: 5 })}
    ${card({ urn: urnFor('2026-10-01'), actor: 'Ada', age: '1mo', text: 'Second' })}
  </main>`);
  await P.collect(doc, { reset: true, now: NOW, stepMs: 1, maxMs: 500, maxStalls: 1 });
  const info = P.writePayloadToDom(doc, { now: NOW });
  assert.strictEqual(info.posts, 2);
  const payload = doc.querySelector('article').textContent;
  const posts = P.parsePayload(payload);
  assert.strictEqual(posts.length, 2);
  assert.strictEqual(posts[0].date, '2026-11-01');
  assert.strictEqual(posts[1].text, 'Second');
  assert.throws(() => P.parsePayload(payload.slice(0, -10)), /incomplete/);
});
