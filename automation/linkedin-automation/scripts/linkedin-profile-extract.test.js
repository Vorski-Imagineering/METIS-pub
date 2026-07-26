'use strict';

/**
 * Tests for linkedin-profile-extract.js against a mocked profile DOM.
 *
 * Requires jsdom, which is not a dependency of this repo (there is no package.json
 * here — the scripts are browser-injected, not npm-installed). Run it with jsdom
 * available on NODE_PATH, e.g.:
 *
 *   mkdir -p /tmp/li && cd /tmp/li && npm init -y && npm i jsdom
 *   NODE_PATH=/tmp/li/node_modules node --test \
 *     automation/linkedin-automation/scripts/linkedin-profile-extract.test.js
 *
 * jsdom does not implement innerText, so the harness polyfills a block-aware
 * approximation of it — the extractor reads innerText when present (browser) and
 * falls back to textContent otherwise.
 */

const test = require('node:test');
const assert = require('node:assert');
const { JSDOM } = require('jsdom');

const BLOCK = new Set(['DIV', 'P', 'LI', 'UL', 'OL', 'SECTION', 'ARTICLE', 'H1', 'H2', 'H3', 'H4', 'BR', 'TR']);

function installInnerText(win) {
  Object.defineProperty(win.HTMLElement.prototype, 'innerText', {
    configurable: true,
    get() {
      const parts = [];
      const walk = node => {
        for (const child of node.childNodes) {
          if (child.nodeType === 3) {
            parts.push(child.textContent.replace(/\s+/g, ' '));
          } else if (child.nodeType === 1) {
            if (BLOCK.has(child.tagName)) parts.push('\n');
            walk(child);
            if (BLOCK.has(child.tagName)) parts.push('\n');
          }
        }
      };
      walk(this);
      return parts.join('').replace(/[ \t]*\n[ \t]*/g, '\n').replace(/\n{2,}/g, '\n').trim();
    },
  });
}

const ABOUT_TEXT =
  'I build systems that turn analytical engines into general-purpose computers. ' +
  'Previously at the Analytical Society, where I wrote the first algorithm intended ' +
  'to be carried out by a machine. I care about notation, correctness and teaching.';

const PROFILE_HTML = `
<main id="workspace">
  <div class="topcard-outer">
    <div class="topcard">
      <div class="ident">
        <h1>Ada Lovelace</h1>
        <div>· 1st</div>
        <p>Mathematician &amp; Software Engineer at Example Co.</p>
        <div class="loc">
          <p>London, United Kingdom</p>
          <a href="/in/adalovelace/overlay/contact-info/">Contact info</a>
        </div>
      </div>
      <div class="links">
        <div>Example Co.</div>
        <div>University of Cambridge</div>
      </div>
      <div class="counts">
        <span>1,234 followers</span>
        <span>500+ connections</span>
      </div>
      <div>Alexander, Nicolás and 407 other mutual connections</div>
    </div>
  </div>

  <img class="pv-top-card-profile-picture__image" src="https://media.licdn.com/dms/image/abc.jpg?e=123&amp;v=beta" />

  <div class="section-about">
    <h2>About</h2>
    <div><span aria-hidden="true">${ABOUT_TEXT}</span></div>
    <button>…more</button>
  </div>

  <div class="section-exp">
    <h2>Experience</h2>
    <ul>
      <li>
        <span aria-hidden="true">Principal Engineer</span>
        <span aria-hidden="true">Example Co.</span>
        <span aria-hidden="true">2019 - Present</span>
      </li>
      <li>
        <span aria-hidden="true">Engineer</span>
        <span aria-hidden="true">Analytical Society</span>
      </li>
    </ul>
  </div>

  <div class="section-edu">
    <h2>Education</h2>
    <ul>
      <li><span aria-hidden="true">University of Cambridge</span><span aria-hidden="true">MSc, Mathematics</span></li>
      <li><span aria-hidden="true">Somerville School</span></li>
    </ul>
  </div>

  <div class="section-featured">
    <h2>Featured</h2>
    <div>A talk on notation for machine instructions, given in 1843.</div>
  </div>

  <div class="section-junk">
    <h2>People you may know</h2>
    <div>Someone else entirely</div>
  </div>
</main>
`;

function makeDom(html, title) {
  const dom = new JSDOM(html || PROFILE_HTML, {
    url: 'https://www.linkedin.com/in/adalovelace/',
    pretendToBeVisual: true,
  });
  dom.window.document.title = title !== undefined ? title : '(3) Ada Lovelace | LinkedIn';
  installInnerText(dom.window);
  return dom;
}

function loadApi(dom) {
  delete require.cache[require.resolve('./linkedin-profile-extract.js')];
  const api = require('./linkedin-profile-extract.js');
  // The module attaches itself to globalThis under Node; point its scratch state
  // (__sc / __profile) at a per-test object so tests don't leak into each other.
  globalThis.__sc = dom.window.document.getElementById('workspace');
  return api;
}

test('nameFromTitle strips notification counts and the LinkedIn suffix', () => {
  const api = loadApi(makeDom());
  assert.strictEqual(api.nameFromTitle('(3) Ada Lovelace | LinkedIn'), 'Ada Lovelace');
  assert.strictEqual(api.nameFromTitle('Ada Lovelace — LinkedIn'), 'Ada Lovelace');
  assert.strictEqual(api.nameFromTitle(''), '');
});

test('classify and normalise URLs', () => {
  const api = loadApi(makeDom());
  assert.strictEqual(api.classifyLinkedInSurface('https://www.linkedin.com/in/adalovelace/'), 'person_profile');
  assert.strictEqual(api.classifyLinkedInSurface('https://example.com/'), null);
  assert.strictEqual(
    api.normaliseLinkedInUrl('https://www.linkedin.com/in/adalovelace/detail/contact-info/'),
    'https://www.linkedin.com/in/adalovelace/'
  );
});

test('extractProfile pulls the full topcard', async () => {
  const dom = makeDom();
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);

  assert.strictEqual(p.name, 'Ada Lovelace');
  assert.strictEqual(p.degree, '1st');
  assert.strictEqual(p.headline, 'Mathematician & Software Engineer at Example Co.');
  assert.strictEqual(p.location, 'London, United Kingdom');
  assert.strictEqual(p.company, 'Example Co.');
  assert.strictEqual(p.school, 'University of Cambridge');
  assert.strictEqual(p.followers, '1,234');
  assert.strictEqual(p.connections, '500+');
  assert.match(p.mutuals, /407 other mutual connections/);
  assert.strictEqual(p.slug, 'adalovelace');
  assert.strictEqual(p.profile_url, 'https://www.linkedin.com/in/adalovelace/');
});

test('topcard is found when the heading carries a nickname the title lacks', async () => {
  // Live regression: document.title was "Beatrice Ungard, Ph.D." while the page
  // heading read "Beatrice (Benne) Ungard, Ph.D.". The prefix probe missed, the
  // container was never located, and every topcard field came back empty on a
  // fully healthy profile — a silent, total loss of the topcard.
  const dom = makeDom(`
    <main id="workspace">
      <div class="topcard">
        <h2>Beatrice (Benne) Ungard, Ph.D.</h2>
        <div>· 1st</div>
        <p>Program Architect</p>
        <div class="loc"><p>Vermont, United States</p><a>Contact info</a></div>
        <div>Regenesis</div>
        <span>500+ connections</span>
      </div>
    </main>`, 'Beatrice Ungard, Ph.D. | LinkedIn');
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);

  assert.strictEqual(p.name, 'Beatrice (Benne) Ungard, Ph.D.', 'the rendered name wins over the title');
  assert.strictEqual(p.degree, '1st');
  assert.strictEqual(p.location, 'Vermont, United States');
  assert.strictEqual(p.connections, '500+');
  assert.ok(api.nameMatches('Ada (Countess) Lovelace', 'Ada Lovelace'));
  assert.ok(!api.nameMatches('Charles Babbage', 'Ada Lovelace'));
});

test('extractProfile captures the full About text', async () => {
  const dom = makeDom();
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);
  assert.strictEqual(p.about, ABOUT_TEXT);
  assert.ok(p.description.startsWith('Mathematician'));
  assert.ok(p.description.includes(ABOUT_TEXT.slice(0, 40)));
});

test('About is found via an id anchor even with no matching heading', async () => {
  const dom = makeDom(`
    <main id="workspace">
      <div id="about"></div>
      <section>
        <div id="about-anchor"></div>
        <span aria-hidden="true">${ABOUT_TEXT}</span>
      </section>
    </main>`);
  const api = loadApi(dom);
  const section = api.findAboutSection(dom.window.document);
  assert.ok(section, 'expected the id="about" anchor to resolve to a section');
});

test('About is found via aria-label when the heading text differs', () => {
  const dom = makeDom(`
    <main id="workspace">
      <section aria-label="About"><span aria-hidden="true">${ABOUT_TEXT}</span></section>
    </main>`);
  const api = loadApi(dom);
  assert.strictEqual(api.extractAboutText(dom.window.document), ABOUT_TEXT);
});

test('extended fields: photo, connection count, current position, education', async () => {
  const dom = makeDom();
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);

  assert.strictEqual(p.photo_url, 'https://media.licdn.com/dms/image/abc.jpg', 'query string must be stripped');
  assert.strictEqual(p.connection_count, 500);
  assert.deepStrictEqual(p.current_position, { title: 'Principal Engineer', company: 'Example Co.' });
  assert.deepStrictEqual(p.education, [
    { school: 'University of Cambridge', degree: 'MSc, Mathematics' },
    { school: 'Somerville School', degree: '' },
  ]);
});

test('current-layout entries parse without aria-hidden spans', async () => {
  // Live regression: a profile whose Experience and Education were fully visible
  // (and captured by the other_info text scan) still yielded current_position:
  // null and education: [] — the upstream parser read span[aria-hidden="true"]
  // inside each li, and the current markup has none. Fall back to entry lines.
  const dom = makeDom(`
    <main id="workspace">
      <div><h2>Experience</h2><ul>
        <li>
          <div>Founder</div>
          <div>Alluma - Regenerative Communities · Full-time</div>
          <div>Jan 2023 - Present · 3 yrs 7 mos</div>
        </li>
        <li><div>Interior Designer</div><div>Olive &amp; Mimosa · Self-employed</div></li>
      </ul></div>
      <div><h2>Education</h2><ul>
        <li><div>Parsons School of Design - The New School</div><div>AAS Interior Design</div><div>1996 – 1997</div></li>
        <li><div>Universidad Pontificia Comillas</div><div>1988 – 1992</div></li>
      </ul></div>
    </main>`);
  const api = loadApi(dom);
  const doc = dom.window.document;

  assert.deepStrictEqual(api.extractCurrentPosition(doc), {
    title: 'Founder',
    company: 'Alluma - Regenerative Communities',
  }, 'the employment type must be stripped off the company');
  assert.deepStrictEqual(api.extractEducation(doc), [
    { school: 'Parsons School of Design - The New School', degree: 'AAS Interior Design' },
    { school: 'Universidad Pontificia Comillas', degree: '' },
  ], 'a date line is not a degree');
});

test('entries parse when the only <li>s are nested media, not entries', async () => {
  // Live regression: this profile's Experience section contained exactly two
  // <li>s, both nested sub-items, while the real entries lived in the section's
  // own text. An li-only parser returned title "Sr Software Engineer" with the
  // company field filled by the date range "2003 - 2007 · 4 yrs".
  const dom = makeDom(`
    <main id="workspace">
      <div><h2>Experience</h2>
        <div>
          <div>Founding Member</div>
          <div>REGENiTECH LLC · Contract</div>
          <div>Sep 2019 - Present · 6 yrs 11 mos</div>
          <div>Whitefish, Montana</div>
          <div>Focused on regenerative agriculture and renewable energy production.</div>
          <div>… more</div>
          <ul><li><div>What is an EPL?</div><div>A short description of a biorefinery.</div></li></ul>
        </div>
        <div>
          <div>Chief Technology Officer</div>
          <div>Some Other Co.</div>
          <div>2003 - 2007 · 4 yrs</div>
        </div>
      </div>
    </main>`);
  const api = loadApi(dom);
  const pos = api.extractCurrentPosition(dom.window.document);

  assert.strictEqual(pos.title, 'Founding Member');
  assert.strictEqual(pos.company, 'REGENiTECH LLC', 'must not be a date range or carry "· Contract"');
});

test('education ignores activities blurbs and their bullet continuations', async () => {
  // Live regression: the "Activities and societies:" lines under an entry became
  // their own education entries, e.g. school "- Member of several sports and
  // leisure societies".
  const dom = makeDom(`
    <main id="workspace">
      <div><h2>Education</h2>
        <div>
          <div>University of Leeds</div>
          <div>International Relations, Globalisation</div>
          <div>2001 – 2004</div>
          <div>Activities and societies: - Member of the POLIS society;</div>
          <div>- Helped organise events for the Union Club;</div>
          <div>- Member of several sports and leisure societies</div>
        </div>
      </div>
    </main>`);
  const api = loadApi(dom);
  const edu = api.extractEducation(dom.window.document);

  assert.deepStrictEqual(edu, [
    { school: 'University of Leeds', degree: 'International Relations, Globalisation' },
  ]);
});

test('a long description is not mistaken for a degree', async () => {
  // Live regression: a Ph.D. entry produced a ~2,000-character "degree" holding
  // the entire dissertation abstract.
  const long = 'Ph.D Dissertation: ' + 'x'.repeat(500);
  const dom = makeDom(`
    <main id="workspace">
      <div><h2>Education</h2>
        <div><div>University of California, Berkeley</div><div>${long}</div><div>1998 – 2005</div></div>
      </div>
    </main>`);
  const api = loadApi(dom);
  assert.deepStrictEqual(api.extractEducation(dom.window.document), [
    { school: 'University of California, Berkeley', degree: '' },
  ]);
});

test('About keeps its paragraph breaks', async () => {
  // textContent welds <br>-separated paragraphs together ("…to nature.After three
  // decades…"), which is what the first live extraction produced.
  const dom = makeDom(`
    <main id="workspace">
      <div><h2>About</h2><div><span aria-hidden="true">First paragraph about homes and shelter and comfort.<br><br>Second paragraph about three decades of work across several countries.</span></div></div>
    </main>`);
  const api = loadApi(dom);
  const about = await api.extractAbout(dom.window.document);
  assert.ok(about.includes('comfort.\n'), 'expected a break between paragraphs, got: ' + JSON.stringify(about.slice(0, 90)));
  assert.ok(!about.includes('comfort.Second'), 'paragraphs must not be welded together');
});

test('other_info collects unhandled sections and skips junk headings', async () => {
  const dom = makeDom();
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);

  assert.ok(p.other_info.includes('## Featured'), 'Featured should be captured');
  assert.ok(p.other_info.includes('1843'), 'Featured content should be captured');
  assert.ok(!p.other_info.includes('People you may know'), 'junk headings must be skipped');
  assert.ok(!p.other_info.includes('## About'), 'About is handled separately');
});

test('a sparse-but-healthy profile is not reported as throttled', async () => {
  const dom = makeDom(`
    <main id="workspace">
      <div class="topcard">
        <h1>Ada Lovelace</h1>
        <p>Mathematician</p>
        <div class="loc"><p>London, United Kingdom</p><a>Contact info</a></div>
        <span>500+ connections</span>
      </div>
      <div><h2>Experience</h2><ul><li><span aria-hidden="true">Engineer</span></li></ul></div>
      <div><h2>Education</h2><ul><li><span aria-hidden="true">Cambridge</span></li></ul></div>
    </main>`);
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);

  assert.strictEqual(p.about, '', 'this fixture genuinely has no About');
  assert.strictEqual(p.connections, '500+');
  assert.strictEqual(p.throttled, false, 'a visible connection count rules out throttling');
});

test('a throttled page that still shows its counts is reported as throttled', async () => {
  // Reproduces a live run: two different profiles, minutes apart, each rendered a
  // complete topcard INCLUDING "500+ connections" and a follower count, with zero
  // About / Experience / Education and scrollHeight pinned (1270 and 1637) across
  // reloads and scroll passes. The earlier rule — missing About AND missing counts
  // — scored both as healthy, so a caller would have recorded the empty body as
  // fact. Present counts plus no body section at all is a reduced render.
  const dom = makeDom(`
    <main id="workspace">
      <div class="topcard">
        <h1>Pamela Mang</h1>
        <div>· 1st</div>
        <p>Co-Founder at the Regenesis Institute</p>
        <div class="loc"><p>Santa Fe, New Mexico, United States</p><a>Contact info</a></div>
        <div>Regenesis Institute</div>
        <span>500+ connections</span>
        <div>Alexander and 407 other mutual connections</div>
      </div>
      <div><h2>Activity</h2><div>2,325 followers</div></div>
    </main>`, 'Pamela Mang | LinkedIn');
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);

  assert.strictEqual(p.connections, '500+', 'the count is visible — that is the trap');
  assert.strictEqual(p.about, '');
  assert.strictEqual(p.body_sections, 0);
  assert.strictEqual(p.throttled, true);
});

test('a collapsed page with no counts and no About is reported as throttled', async () => {
  const dom = makeDom(`
    <main id="workspace">
      <div class="topcard"><h1>Ada Lovelace</h1><p>Mathematician</p></div>
      <div><h2>Activity</h2><div>nothing much</div></div>
    </main>`);
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);
  assert.strictEqual(p.throttled, true);
});

test('walk-up loops survive a short ancestor chain', async () => {
  const dom = makeDom('<main id="workspace"><h2>About</h2></main>');
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);   // must not throw
  assert.strictEqual(typeof p.about, 'string');
});

test('serialiseProfile emits every non-empty field and the END sentinel', async () => {
  const dom = makeDom();
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);
  const payload = api.serialiseProfile(p);

  assert.ok(payload.includes('<<<NAME>>>\nAda Lovelace\n'));
  assert.ok(payload.includes('<<<ABOUT>>>\n' + ABOUT_TEXT));
  assert.ok(payload.includes('<<<CURRENT_POSITION>>>\nPrincipal Engineer @ Example Co.'));
  assert.ok(payload.includes('University of Cambridge — MSc, Mathematics'));
  assert.ok(payload.endsWith('<<<END>>>'));
  assert.ok(!payload.includes('<<<MUTUALS>>>\n\n'), 'empty fields must be omitted, not left blank');
});

test('receipt fits well inside javascript_tool\'s 1000-character return cap', async () => {
  const dom = makeDom();
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);
  const json = JSON.stringify(api.receipt(p));
  assert.ok(json.length < 500, 'receipt was ' + json.length + ' chars');
});

test('writePayloadToDom replaces the body with one article and no markup parsing', async () => {
  const dom = makeDom();
  const api = loadApi(dom);
  const p = await api.extractProfile(dom.window.document);
  p.about = '<img src=x onerror=alert(1)>' + p.about;

  const len = api.writePayloadToDom(dom.window.document, p);
  const doc = dom.window.document;
  assert.strictEqual(doc.body.children.length, 1);
  assert.strictEqual(doc.body.children[0].tagName, 'ARTICLE');
  assert.strictEqual(doc.querySelectorAll('img').length, 0, 'payload must not be parsed as HTML');
  assert.ok(doc.body.textContent.includes('<img src=x onerror=alert(1)>'));
  assert.strictEqual(len, doc.body.textContent.length);
});
