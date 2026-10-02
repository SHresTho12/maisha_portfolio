# Dental Professional Portfolio

A GitHub Pages version of the dental portfolio, with a consultation calendar, appointment request form, PDF CV and file-based blog. No npm packages or paid services are required.

## Publish on GitHub Pages

1. Create a new GitHub repository, such as `dental-portfolio`, with `main` as its default branch. A public repository works with GitHub Free.
2. Extract the ZIP and upload **the contents of the dental-portfolio folder** into the repository root. Include `.github/workflows/pages.yml` (the `.github` folder may be hidden in your file manager). Do not upload the ZIP itself.
3. Go to **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
4. Open the **Actions** tab. Run **Deploy portfolio to GitHub Pages**, or commit a change to trigger it automatically.
5. Open the URL shown by the deployment, normally `https://YOUR-USERNAME.github.io/dental-portfolio/`.

The workflow builds with Python and deploys only `dist/`. Later commits to `main` automatically rebuild and publish the website. Relative links support project repositories and custom domains.

Official instructions: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## Update information

Edit `site.json` in GitHub and commit the change. It controls the name, location, short introduction, email, WhatsApp contact, profile photograph, schedule and reviews.

- `contact.email`: real email address, e.g. `doctor@example.com`.
- `contact.whatsapp`: international number with country code, e.g. `8801XXXXXXXXX`. Enter the real number, not this example.
- `schedule.days`: `0` Sunday, `1` Monday, `2` Tuesday, `3` Wednesday, `4` Thursday, `5` Friday, `6` Saturday.
- `schedule.start` and `schedule.end`: 24-hour times, e.g. `17:00` and `20:00`.
- `schedule.durationMinutes`: positive appointment length, currently `30`.
- `schedule.timezone`: currently `Asia/Dhaka`.
- Detailed education, clinical experience and other text: edit `templates/index.html`.
- Design: edit `assets/styles.css`.

Keep valid JSON syntax: quote text, separate entries with commas, and do not add a trailing comma. The Actions log identifies build errors.

## Add or replace the profile photo

1. Upload your photo to `assets/profile.jpg` in GitHub.
2. Set `profileImage` in `site.json` to `assets/profile.jpg`.
3. Update `profileImageAlt` and commit. Use a portrait photo and avoid large files.

Leave `profileImage` empty to retain the BDS placeholder.

## Add a patient review

Use only genuine reviews you have permission to publish. Replace the empty `reviews` array in `site.json` with entries in this format:

```json
"reviews": [
  {"name": "Patient display name", "text": "The patient’s actual feedback."}
]
```

Names and review text are displayed publicly. Leave the array empty to show the current empty state.

## Write and publish a blog article

1. In GitHub, choose **Add file → Create new file**.
2. Name the file `articles/my-article-title.md` (lowercase letters, numbers and hyphens).
3. Use this format:

```markdown
---
title: Your article title
summary: A short introduction shown on the Blogs page.
date: 2026-10-02
published: true
---

## First heading

Write your first paragraph here.

Write another paragraph after a blank line.

- First point
- Second point
```

4. Commit the file. It appears on the Blogs page after the workflow finishes.
5. Edit the same file to update the article. Set `published: false` to remove it from the deployed site.

Supported article formatting includes paragraphs, headings, bullet lists, images, emphasis, links and fenced code blocks. Raw HTML is escaped; advanced Markdown such as tables is not implemented. Do not put `---` inside the front-matter fields.

`articles/first-article.md` is an unpublished writing template, not a real article. Existing articles stored in the hosted site’s database are not automatically included in this export; copy any you have written into Markdown files before migration.

**A draft in a public GitHub repository is visible in the repository, even when `published: false`.** Keep genuinely private drafts outside a public repository.

## Update the CV

Replace `assets/professional-cv.pdf` with your updated PDF. The source is included at `assets/professional-cv.tex`; compile it in Overleaf and download the PDF. Website text and the PDF are separate files; editing `site.json` does not update the PDF.

The current CV still has name, contact and referee placeholders.

## Appointment requests and limitations

The calendar shows the configured consultation schedule, currently Sunday–Thursday, 5–8 pm, with 30-minute online slots in Bangladesh time. It excludes past dates and times.

A selected time is an **appointment request**, not a reservation. The patient form prepares a message; when the WhatsApp number is configured, the patient can open WhatsApp, review it and send it. Blank WhatsApp details leave a copyable request but cannot send anything. The email button similarly needs a real address.

GitHub Pages has no application server or database. This version does not reserve slots, track existing bookings, send email itself, or provide the hosted owner-only article editor. Manage published articles through GitHub files. Add an external booking service if you need live occupied-slot tracking and confirmed appointments.

Private checkup availability is not configured; that consultation type shows an unavailable state.

## Preview locally

With Python 3.9+ installed:

```bash
python build.py
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. Windows users may use `py` instead of `python`. A Python installation needs an IANA timezone database; on systems without one, install it with `python -m pip install tzdata`.

## File map

| File | Purpose |
| --- | --- |
| `site.json` | Personal information, contact details, photograph, schedule, reviews |
| `templates/index.html` | Full homepage content and structure |
| `assets/styles.css` | Visual styling and mobile layout |
| `assets/main.js` | Calendar and appointment form behavior |
| `articles/*.md` | Blog article source files |
| `assets/professional-cv.pdf` | CV opened by the website button |
| `assets/professional-cv.tex` | Editable LaTeX CV source |
| `build.py` | Static website generator |
| `.github/workflows/pages.yml` | Automatic build and GitHub Pages publishing |

No credentials, database identifiers or authentication tokens are included.

## Blog photos and enhanced Markdown

Store article images in `assets/blogs/`. Use lowercase filenames without spaces, for example `toothbrush.jpg`.

Embed an image inside the article:

```markdown
![Description shown below the photo](assets/blogs/toothbrush.jpg)
```

The image stays in the repository and is deployed with the site. Local image paths must start with `assets/`; the builder fixes paths for each article and GitHub Pages repository subdirectory. Supported images: JPG, PNG, GIF, WebP and AVIF. Missing image files produce a build error rather than a broken image.

To show a cover photo at the top of an article, add these lines to its front matter:

```text
image: assets/blogs/toothbrush.jpg
imageAlt: A descriptive explanation of the image
```

Article formatting also supports `**bold**`, `*italic*`, inline backticks, safe links and fenced code blocks. Raw HTML is escaped. This is a supported Markdown subset, not every GitHub-flavored Markdown feature.

## Activate likes, dislikes and comments

Shared reactions and comments are stored in GitHub Discussions through **giscus**. They are not fake browser-local counters. Visitors sign in with GitHub to react or comment. The same discussion is used for each article even when its title changes.

One-time setup:

1. In your **public** repository, go to **Settings → General → Features** and enable **Discussions**.
2. Install the giscus GitHub App on that repository: https://github.com/apps/giscus
3. Open https://giscus.app and enter `YOUR-USERNAME/YOUR-REPOSITORY`.
4. Select a discussion category, preferably **Announcements**. Enable **reactions for the main post**.
5. Copy the configuration values shown by giscus into `comments` in `site.json`:

```json
"comments": {
  "enabled": true,
  "repo": "YOUR-USERNAME/YOUR-REPOSITORY",
  "repoId": "COPY data-repo-id FROM GISCUS",
  "category": "Announcements",
  "categoryId": "COPY data-category-id FROM GISCUS",
  "language": "en"
}
```

6. Commit the change. Every published article will show the reactions and comments widget after deployment. Use thumbs-up for like and thumbs-down for dislike; giscus also offers other GitHub reactions. These are GitHub reactions, not an exclusive like-or-dislike voting system.

No GitHub password or personal access token belongs in the files. The repository and category identifiers are public widget settings.

The provided configuration leaves comments disabled because your GitHub repository details have not been supplied. This state displays an honest “not connected yet” message on each article. A live connection has not been tested against your repository.

### Photo comments

For photo attachments, use the link below the comments section to open your repository’s GitHub Discussions. Choose the discussion named `dental-blog/ARTICLE-FILENAME`, then drag a photo into GitHub’s comment box and post it. giscus displays discussion comments back on the article. A discussion is created when someone first comments or reacts; if it does not exist yet, leave the first comment on the article first.

Photo uploads happen on GitHub, not through a custom upload form on the static site. Article photos you publish are stored in `assets/blogs/`; visitor comment attachments are hosted by GitHub. You can moderate or remove comments through GitHub Discussions.

Documentation:
- https://giscus.app
- https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files
