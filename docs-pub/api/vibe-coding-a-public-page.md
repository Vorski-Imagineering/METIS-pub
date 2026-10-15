# Build your own page from the public data

**TL;DR for humans.** Your website can show a gathering's camps, programme and team,
pulled live from METIS and drawn in your own design. You don't need a login or a key,
and we don't need to change anything. Give this page to your coding agent ("read this
and build me a camps section for gathering X"). It has everything the agent needs.

**One thing only you can fix:** a camp shows up only once it is **published** in
METIS, which means it rests on a journey step that publishes (marked with the globe
chip). A camp that hasn't been moved onto a publishing step doesn't appear in the
data at all. If your list is empty or missing a camp, that is the cause. Ask the
gathering's METIS team to move the camp to a publishing step. Nothing on your side
will make it appear. See [Publication: what the public site shows](../core/PUBLICATION.md).

---

## For the coding agent

You are building part of an external website that shows data from METIS's public JSON
API. Follow this page. Where it disagrees with the live schema, the live schema wins.

### The facts you need

| | |
|---|---|
| Base URL | `https://view.the-gathering.earth/public/` |
| Live schema (authoritative) | `https://view.the-gathering.earth/public/openapi.json` |
| Interactive docs | `https://view.the-gathering.earth/public/docs` |
| Auth | None. Send no token, key or cookie. |
| Methods | `GET` only |
| CORS | `Access-Control-Allow-Origin: *`, so call it straight from browser JavaScript |
| Errors | JSON `{"code": "not_found" \| "server_error", "message": "…"}` with the HTTP status |
| Relative URLs | `photo_url`, `public_url` and similar fields are paths. Prefix them with `https://view.the-gathering.earth` |

**Read `openapi.json` before writing code.** It lists every endpoint and every field.
Fields get added over time, but none are renamed or removed without notice.

### Endpoints

| Endpoint | Use it for |
|---|---|
| `GET /public/domain/` | Every gathering with its camps, dates, status, place, tagline, ticket link and each camp's `video`. Find the gathering's `slug` here. |
| `GET /public/gatherings/{lg_slug}/` | One gathering: `camps` (each with links, team and orgs), team, links, `info_field_groups` and a programme teaser |
| `GET /public/gatherings/{lg_slug}/camps/{camp_slug}/` | One camp in full: `camp_info_fields` (video, "why" text, buttons …), team, links, programme preview |
| `GET /public/gatherings/{lg_slug}/programme/` | The whole programme across the gathering and its camps, as `cards`. Optional `q` (search) and `owner` filters. |
| `GET /public/gatherings/{lg_slug}/camps/{camp_slug}/programme/` | One camp's programme |
| `GET /public/gatherings/{lg_slug}/camps/{camp_slug}/experiences/{experience_slug}/` | One experience (an item in the programme) |
| `GET /public/orgs/{org_slug}/` | An organisation |
| `GET /public/people/{person_id}/` | A person's public profile |

To find a gathering's slug, call `/public/domain/` and look through `local_gatherings`
for its `name`. For example, Gathering of Tribes Portugal 2027 is
`gathering-of-tribes-portugal-2027`.

### Shapes you will meet

A camp in a gathering's `camps` list:

```json
{
  "id": 1946, "name": "Camp Regenaissance", "slug": "camp-regenaissance", "class_slug": "camp",
  "links": [{"key": "website", "url": "https://…", "icon": "globe", "label": "Website"}],
  "spheres": [{"name": "…", "slug": "…"}],
  "team_members": [{"id": 1960, "name": "…", "photo_url": "/media/people/photos/….jpg",
                    "socials": [{"key": "linkedin", "value": "https://…", "icon": "linkedin", "label": "LinkedIn"}]}],
  "orgs": [{"id": 1, "name": "…", "slug": "…", "class_slug": "…"}]
}
```

The info fields on a camp detail (`camp_info_fields`, also grouped in
`camp_info_field_groups`):

```json
[
  {"key": "latest-video", "label": "Video", "type": "video",
   "value": "https://www.youtube-nocookie.com/embed/UxLXggp1MD4", "value_items": []},
  {"key": "why", "label": "Why", "type": "text-area", "value": "…", "value_items": []},
  {"key": "purchase_link", "label": "Purchase", "type": "button", "value": "https://…", "value_items": []}
]
```

**Render info fields by `type`, never by `key`.** Each gathering configures its own
keys and labels, so `key` differs between gatherings. Use `label` as the heading.

| `type` | `value` is | Render as |
|---|---|---|
| `text-line` | one line of text | text |
| `text-area` | text with line breaks | text, keeping line breaks (`white-space: pre-line`) |
| `video` | a ready-made YouTube embed URL | `<iframe src="{value}" allowfullscreen>` |
| `playlist` | a YouTube playlist | link or embed |
| `button` | a URL | a button labelled with `label` |
| `link` | a URL | a link |
| `date` | normally `YYYY-MM-DD` | format it yourself. Parse defensively. |
| `time` | `HH:MM`, 24-hour, may be blank | text |
| `duration` | minutes | text |
| `select` | the chosen value. `value_items` holds the chosen options when there are several | text or chips |
| `slideshow` | image URLs | gallery |
| `timezone` | a timezone name | usually not shown |

An unknown `type` may be added later. Fall back to showing `value` as plain text.

A programme card (from `…/programme/` → `cards`, or `programme_preview`):

```json
{
  "id": 2201, "name": "Botanical Elixir Bar", "slug": "botanical-elixir-bar",
  "description": "<p>Come unwind…</p>",
  "owner": {"id": 1946, "name": "Camp Regenaissance", "slug": "camp-regenaissance", "class_slug": "camp"},
  "public_url": "/2026-usa-california/camp-regenaissance/experiences/botanical-elixir-bar/",
  "artwork": {"url": "", "css_fallback": true},
  "select_items": []
}
```

`description` is **HTML**. Either sanitise it (for example with DOMPurify) before you
insert it, or strip the tags and show plain text. Never insert it raw.

### Rules

- **Escape everything you put into HTML.** Names and text come from many editors.
  Build elements with `textContent`, or escape them, rather than pasting strings into
  `innerHTML`.
- **Fetch once when the page loads.** Don't poll. The data changes a few times a day
  at most.
- **Empty is normal.** A list can be `[]` and a field can be `null` or `""`. Show a
  friendly placeholder (such as "More camps coming soon") instead of breaking.
- **Missing camps are a publishing matter, not a bug in your code.** The API returns
  only published camps. An unpublished camp's own URL answers `404`, the same as one
  that doesn't exist. Don't try to work around it. Tell the human to have the camp
  moved onto a publishing step in METIS.
- **Link back.** Each camp has a page on the public site at
  `https://view.the-gathering.earth/{lg_slug}/{camp_slug}/`. Programme cards carry
  `public_url`.
- Keep the site owner's own fonts, colours and layout. The data has no styling
  attached, apart from an optional `palette` on gatherings.

### Sample: a camps section in plain HTML and JavaScript

Drop this into any static page and change `GATHERING`. It lists the published camps
with their video, "why" text, links and team, and links each camp to its page.

```html
<section id="camps"><p>Loading camps…</p></section>

<script>
const METIS = "https://view.the-gathering.earth";
const GATHERING = "gathering-of-tribes-portugal-2027";

function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  for (const c of children) if (c) node.append(c);
  return node;
}

function absolute(url) {
  return url && url.startsWith("/") ? METIS + url : url;
}

function renderField(field) {
  if (!field.value) return null;
  switch (field.type) {
    case "video":
      return el("iframe", { src: field.value, allowfullscreen: "", loading: "lazy",
                            width: "560", height: "315", title: field.label });
    case "button":
    case "link":
      return el("a", { href: field.value, class: "btn", target: "_blank", rel: "noopener" },
                field.label);
    case "text-area":
      return el("p", { style: "white-space: pre-line" }, field.value);
    default:
      return el("p", {}, field.value);
  }
}

async function loadCamps() {
  const box = document.getElementById("camps");
  try {
    const res = await fetch(`${METIS}/public/gatherings/${GATHERING}/`);
    if (!res.ok) throw new Error(res.status);
    const gathering = await res.json();

    if (!gathering.camps.length) {
      box.replaceChildren(el("p", {}, "More camps coming soon."));
      return;
    }

    // The gathering list is a summary; each camp's detail carries its info fields.
    const details = await Promise.all(gathering.camps.map(c =>
      fetch(`${METIS}/public/gatherings/${GATHERING}/camps/${c.slug}/`).then(r => r.json())
    ));

    box.replaceChildren(...gathering.camps.map((camp, i) => {
      const detail = details[i];
      return el("article", { class: "card" },
        el("h3", {}, el("a", { href: `${METIS}/${GATHERING}/${camp.slug}/` }, camp.name)),
        ...detail.camp_info_fields.map(renderField),
        ...camp.links.map(l => el("a", { href: l.url, target: "_blank", rel: "noopener" }, l.label)),
        camp.team_members.length
          ? el("p", {}, "Team: " + camp.team_members.map(p => p.name).join(", "))
          : null,
      );
    }));
  } catch (err) {
    box.replaceChildren(el("p", {}, "Camps could not be loaded right now."));
  }
}

loadCamps();
</script>
```

### Sample: the programme

```js
const res = await fetch(`${METIS}/public/gatherings/${GATHERING}/programme/`);
const { cards } = await res.json();
// Each card: name, owner.name (the camp), description (HTML: sanitise it), public_url.
```

### Sample: gathering headline facts

`/public/domain/` already has the dates, place, tagline and ticket link worked out for
each gathering, so you don't need to read info fields for these:

```js
const res = await fetch(`${METIS}/public/domain/`);
const { local_gatherings } = await res.json();
const g = local_gatherings.find(x => x.slug === GATHERING);
// g.start_date, g.end_date, g.place, g.tagline, g.tickets_url, g.status,
// g.camps[i].video (a YouTube embed URL or null)
```

### When something looks wrong

- **A camp is missing, or the list is empty:** it isn't published yet. A human must
  move it onto a publishing journey step in METIS.
- **A field is missing:** the gathering hasn't marked that field public, or nobody has
  filled it in. This is also fixed in METIS, not in your code.
- **Something on the public site is missing from the JSON:** that is a bug in our API.
  Report it to the METIS team.

More detail on every endpoint: [Public API playbook](public-PLAYBOOK.md).
