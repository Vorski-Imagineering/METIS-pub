# Brand pages

Every brand METIS carries — The Gathering, Coherence, Audax, METIS itself,
Outreach and Invitations — has a public reference page, plus two files you can
download and use somewhere else. No sign-in is needed for any of them. The idea
is that you can hand one link to a designer, a contractor or an AI assistant
and they have what they need to work in that brand.

Everything on these pages is generated from the stylesheets the product runs
on, at the moment you open them. When a brand's colours change in the product,
its page, its stylesheet and its brief change with it. There is no second copy
to update.

## Where they are

All paths are under the site's `/view/` area.

| Path | What it is |
|---|---|
| `/view/brands/` | The list of every brand, each with a strip of its colours and its three links |
| `/view/brand/<brand>/` | One brand's reference page — for example `/view/brand/coherence/` |
| `/view/brand/<brand>/style.css` | A stylesheet that works on its own: the brand's colours, type and spacing as CSS custom properties |
| `/view/brand/<brand>/style.md` | The same brand as a plain-text brief: the rules, every colour with its name and value, the fonts, and absolute links to every logo and image |
| `/view/brand/` | The Gathering's page. This path was there before the others, and it still shows The Gathering |
| `/view/brand.json` | The Gathering's page as structured data, with the same keys it has always had |

`<brand>` is one of `gathering`, `coherence`, `audax`, `metis`, `outreach`,
`invitations`. A brand added to the product later shows up in the list and gets
its own three links automatically.

## What is on a page

Sections only appear when the brand has something to put in them:

- **Colour.** Each colour is shown as a swatch, painted with the real CSS
  variable, with its value printed beside it. The notes next to each group of
  colours are the brand's own notes, taken word for word from its stylesheet.
- **Type.** The typefaces with the weights the product actually loads, and the
  exact `<link>` tags that load them. If a brand's design system gives a
  different size or spacing from the one the product uses, the page marks that
  step itself.
- **Shape.** Radii, spacing, shadows and any shape constants the brand has.
- **Logo, rules, voice and asset galleries.** At the moment only The Gathering
  has these, because only The Gathering has written them. Other brands' pages
  are shorter, and that is expected.

## Using the stylesheet

`style.css` includes the shared palette and scales as well as the brand's own
values, so nothing is missing when you use it. Link it before any of your own
stylesheets, because it declares the cascade layers everything else uses. Fonts
are not part of it: copy the `<link>` lines from the comment at the top of the
file into your page's `<head>`.

Most brands scope their own values to an attribute: set `data-app="<brand>"`
on `<html>` or `<body>` (for example `<body data-app="coherence">`). Without it
the stylesheet still loads, but you get the shared platform palette and fonts,
not the brand's. Images the theme refers to (icon masks, backdrops) are linked
by absolute URL, so they load from your own site too.

It contains design tokens only (CSS custom properties). It does not include
METIS's own components such as buttons, chips or cards. Build those in your own
CSS using the tokens.

## Using the brief

`style.md` is written to be read, by a person or by an AI assistant. It puts
the rules first because they are the part you have to follow. After that come
the colours in tables with their token names and values, then the fonts, then
absolute links to every mark and image. Asset links point at unhashed file
names, so a link you copy keeps working after the next release.
