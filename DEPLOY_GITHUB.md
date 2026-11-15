# Publish the Cai Lab website on GitHub Pages

The package contains the complete source and a Python standard-library builder. GitHub Actions builds `dist/` and publishes it after each change to `main`.

## First publication from your computer

1. Install [Python 3](https://www.python.org/downloads/), [Git](https://git-scm.com/downloads), and [GitHub CLI](https://cli.github.com/). Reopen your terminal after installation.
2. Extract the complete package into a new folder. Open a terminal in the folder containing `build.py` and `publish_github.py`.
3. Run:

   **Windows PowerShell**

   ```powershell
   py -3 publish_github.py --login
   ```

   **macOS / Linux**

   ```bash
   python3 publish_github.py --login
   ```

4. If prompted by GitHub CLI, finish signing in through GitHub's browser flow using your own account. Do not send passwords, tokens, or authentication codes to anyone.
5. The helper creates a **new public repository**, enables GitHub Pages, pushes the source, and watches the deployment. It prints **Published and verified** only after the matching workflow succeeds and the website responds with the expected page title. A pending or failed deployment is reported as such.

The default repository name is `<your-github-login>.github.io` when available. If that already exists, the helper tries the new project repository `cai-lab-website`. It never modifies either name if it already exists. To select another **new** repository name:

```bash
python3 publish_github.py --repo my-cai-lab-site --login
```

Use `py -3` instead of `python3` on Windows. The helper publishes under your authenticated personal account. For a lab organization, use the manual route below and select the organization as repository owner.

## Publication through GitHub's website

1. Sign in at [GitHub](https://github.com/).
2. Create a **new public repository**. Name it `<owner>.github.io` for an account/organization homepage, or choose a new project repository name. Do not reuse a repository that contains an existing website.
3. Upload the source files and directories, including `build.py`, `content/`, `assets/`, any `templates/`, and `.github/workflows/pages.yml`. Keep their directory structure. A ZIP file alone is not a deployable website; extract it before uploading. The generated `dist/` folder is not required for this route.
4. In the repository, open **Settings → Pages**. Set **Build and deployment → Source** to **GitHub Actions**.
5. Open **Actions → Publish Cai Lab website → Run workflow** and select `main`. If the first run started before Pages was enabled, rerun it after step 4.
6. When the workflow succeeds, open the deployment URL shown in the workflow or **Settings → Pages**. Visit it to check the homepage and navigation.

If you upload through a web file chooser, your operating system may hide `.github`. Ensure that the workflow file is included. Alternatively, create `.github/workflows/pages.yml` using GitHub's **Add file → Create new file** control and copy the supplied file's contents.

## Update the site after publication

- **Text, people, research, papers and news:** edit `content/site.json` on GitHub and click **Commit changes**. Keep valid JSON syntax.
- **Layout and appearance:** edit `build.py`, template files if present, or files under `assets/`.
- Changes pushed or committed to `main` automatically publish. Check the **Actions** tab if an update does not appear.
- To preview locally, run `python3 build.py` and open `dist/index.html`, or serve that folder with `python3 -m http.server 8000 --directory dist`.

For subsequent local changes in the already published checkout:

```bash
python3 build.py
git add build.py content assets README.md
git commit -m "Update lab website"
git push
```

Stage any other source files you intentionally changed as needed. Do not run the first-publication helper again on an existing checkout.

## If the first attempt stops partway through

The helper preserves any repository it already created and reports its repository URL. It writes nonsecret local progress to `.github-pages-publish.json`, which is excluded from Git. It never reports a working website merely because a repository or workflow exists.

- **Authentication or network failure before repository creation:** resolve the reported problem. If the helper already initialized local Git, use a fresh extraction for another first-publication attempt.
- **Repository created, but upload or Pages setup failed:** use the same repository. In the extracted checkout, finish a normal `git push --set-upstream origin main` after checking Git authentication. Then enable **Settings → Pages → GitHub Actions** in GitHub.
- **Workflow was not uploaded:** commit and push `.github/workflows/pages.yml` after enabling Pages:

  ```bash
  git add .github/workflows/pages.yml
  git commit -m "Enable GitHub Pages publication"
  git push
  ```

- **Workflow exists but failed or is pending:** inspect **Actions → Publish Cai Lab website**. Resolve the displayed error and rerun that workflow; do not create a duplicate repository.
- **Insufficient permission to push workflow files:** use GitHub CLI's normal authentication flow to grant the required GitHub repository/workflow permission. Keep credentials in GitHub CLI, never in this source folder.

## Hosting and source visibility

GitHub Pages is available with GitHub Free for public repositories. Your site source, uploaded assets, and content files are public when you use this route. Domain registration is unnecessary when using the included `github.io` address. This website has no paid API dependency or server-side application.

## Official references

- [Create a GitHub Pages site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [Configure the publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Use custom GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Edit files directly on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)
- Action versions checked against their official releases on November 15, 2026: [checkout](https://github.com/actions/checkout/releases/tag/v7.0.1), [configure-pages](https://github.com/actions/configure-pages/releases/tag/v6.0.0), [upload-pages-artifact](https://github.com/actions/upload-pages-artifact/releases/tag/v5.0.0), [deploy-pages](https://github.com/actions/deploy-pages/releases/tag/v5.0.1).
