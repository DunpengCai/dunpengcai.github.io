# Cai Lab website

A complete English website for the Cai Lab at the University of Missouri. Designed for free GitHub Pages hosting, with seven separate pages: Home, Research, People, Publications, News, Join Us, and Contact.

## What is included

- Responsive desktop and mobile layouts, accessible navigation, and a print stylesheet.
- Four research areas, a verified PI profile, eight selected publications, and three university news stories.
- Publication search, year/topic filters, citation copying, and RIS/BibTeX downloads.
- Direct institutional email links. There is no contact-form server or visitor database.
- A complete GitHub Actions deployment workflow and a first-publication helper.
- An original vascular illustration and the PI portrait from his university profile.
- No JavaScript packages, paid APIs, tracking scripts, font services, or runtime server dependencies.

## Preview the finished site

The `dist/` folder contains the ready-to-publish website. Open `dist/index.html` to browse it locally. All seven pages and assets work without installing packages. Clipboard access may be restricted when browsing a local file.

To rebuild after editing content, use Python 3.12 or newer:

```bash
python build.py
```

On Windows, `py -3 build.py` also works if the Python launcher is installed. For an HTTP preview on your own computer:

```bash
python -m http.server 8000 --directory dist
```

Then open http://localhost:8000 in your own browser. This local preview is not public hosting.

## Publish to GitHub Pages

See **DEPLOY_GITHUB.md**. With Python, Git, and GitHub CLI installed, the first-publication helper can create a new public repository and configure GitHub Pages:

```bash
python publish_github.py --login
```

GitHub authentication happens through GitHub CLI; do not put passwords or tokens in this project. The helper chooses a new `USERNAME.github.io` repository if available and otherwise tries a new `cai-lab-website` project repository. It never overwrites an existing repository. Publication is only complete once the helper reports a verified public URL or GitHub reports a successful deployment.

## Update the content

Edit **content/site.json**. The most useful sections are:

| Section | Content |
| --- | --- |
| `lab` | Lab name, affiliation, institutional contact, and PI biography |
| `research` | Four research areas and their supporting links |
| `publications` | Publication metadata, DOI/PubMed links, filter topics, and homepage highlights |
| `news` | Dated university news items |
| `source_notes` | Editorial provenance, excluded from the public HTML |

On GitHub, open the file, click the pencil icon, edit it, and commit the changes to `main`. Once Pages is configured, GitHub Actions rebuilds and publishes the website. Keep JSON syntax valid: double quotes, commas between entries, and no trailing commas.

For a new paper, copy an existing publication object, replace the metadata, choose a unique `id`, and set `featured` to `true` only if it should appear on the home page. The website shows a **selected bibliography**, including papers from prior training and collaborations; it does not claim that every paper originated in the independent lab.

The current People page lists the verified PI. Add additional members after confirming their names, roles, bios, and consent to use their photos. The Join Us page invites inquiries; it does not advertise a verified vacant position.

## Change the design

- **build.py**: shared layout and page structure.
- **assets/site.css**: colors, typography, and responsive layout.
- **assets/site.js**: mobile menu, publication filtering, and copy buttons.
- **assets/**: portrait and original vector artwork.

The site uses relative links, so it works at either a root `github.io` address or a project subdirectory. The deployment workflow supplies the live URL to generate canonical links and a sitemap. For a manual build with a known URL:

```bash
python build.py --site-url https://YOUR-USERNAME.github.io
```

That address is an example; replace it with the actual Pages URL returned by GitHub.

## Content and image sources

See **SOURCE_NOTES.md** and **ASSET_CREDITS.md**. No unpublished project ideas, unverified team members, invented employment openings, or fabricated laboratory photographs are included. The vascular artwork is explicitly labeled as a conceptual illustration.

## Current publication status

This package is ready for GitHub Pages. Packaging and a local preview do not create a public `github.io` address; a connected GitHub account must complete deployment. No domain purchase is required when using GitHub's provided address.
