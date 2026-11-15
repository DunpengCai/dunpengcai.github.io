# Cai Lab website

A complete English website for the Cai Lab at the University of Missouri. Designed for free GitHub Pages hosting, with seven separate pages: Home, Research, People, Publications, News, Join Us, and Contact.

**Live website: [https://dunpengcai.github.io/](https://dunpengcai.github.io/)**

## What is included

- A warm gold and parchment design, responsive desktop and mobile layouts, accessible navigation, and a print stylesheet.
- Four research priorities: Marfan syndrome, RNA therapeutics, aortic valve calcification (AVC), and thoracic aortic aneurysm (TAA), plus a verified PI profile, eight selected publications, and three university news stories.
- Publication search, year/topic filters, citation copying, and RIS/BibTeX downloads.
- Direct institutional email links. There is no contact-form server or visitor database.
- A complete GitHub Actions deployment workflow and a first-publication helper.
- An original conceptual aortic/RNA illustration and the PI portrait from his university profile.
- No JavaScript packages, paid APIs, tracking scripts, font services, or runtime server dependencies.

## Preview locally

The generated `dist/` folder is excluded from Git. Create or refresh it from the source using Python 3.12 or newer:

```bash
python build.py
```

Open the generated `dist/index.html` to browse all seven pages locally. No Python packages are required. Clipboard access may be restricted when browsing a local file.

On Windows, `py -3 build.py` also works if the Python launcher is installed. For an HTTP preview on your own computer:

```bash
python -m http.server 8000 --directory dist
```

Then open http://localhost:8000 in your own browser. This local preview is not public hosting.

## Deployment and creating a separate copy

The live website is already configured. Commit updates to `main`; GitHub Actions builds and publishes them automatically. Check the repository's **Actions** tab for deployment progress.

Use the first-publication helper **only to publish a separate new copy**, with Python, Git, and GitHub CLI installed. See **DEPLOY_GITHUB.md** for the full instructions:

```bash
python publish_github.py --login
```

The helper creates a new public repository and leaves existing repositories unchanged. Authentication is handled by GitHub CLI; keep passwords and tokens out of this project.

## Update the content

Edit **content/site.json**. The most useful sections are:

| Section | Content |
| --- | --- |
| `lab` | Lab name, affiliation, institutional contact, and PI biography |
| `research` | Four research areas and their supporting links |
| `publications` | Publication metadata, DOI/PubMed links, filter topics, and homepage highlights |
| `news` | Dated university news items |
| `source_notes` | Editorial provenance, excluded from the public HTML |

On GitHub, open the file, click the pencil icon, edit it, and commit the changes to `main`. GitHub Actions automatically rebuilds and publishes the website. Keep JSON syntax valid: double quotes, commas between entries, and no trailing commas.

For a new paper, copy an existing publication object, replace the metadata, choose a unique `id`, and set `featured` to `true` only if it should appear on the home page. The website shows a **selected bibliography**, including papers from prior training and collaborations; it does not claim that every paper originated in the independent lab.

The current People page lists the verified PI. Add additional members after confirming their names, roles, bios, and consent to use their photos. The Join Us page invites inquiries; it does not advertise a verified vacant position.

## Change the design

- **build.py**: shared layout and page structure.
- **assets/site.css**: colors, typography, and responsive layout.
- **assets/site.js**: mobile menu, publication filtering, and copy buttons.
- **assets/**: portrait and original vector artwork.

The site uses relative links, so it works at either a root `github.io` address or a project subdirectory. The deployment workflow supplies the live URL to generate canonical links and a sitemap. To build locally with this website's published address:

```bash
python build.py --site-url https://dunpengcai.github.io/
```

## Content and image sources

See **SOURCE_NOTES.md** and **ASSET_CREDITS.md**. No unpublished project ideas, unverified team members, invented employment openings, or fabricated laboratory photographs are included. The aortic/RNA artwork is explicitly labeled as a conceptual illustration.

## Current publication status

Published at [https://dunpengcai.github.io/](https://dunpengcai.github.io/). GitHub Actions automatically builds and deploys commits to `main`. The site uses HTTPS and GitHub's free `github.io` address; no domain purchase is required.
