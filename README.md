# davidparkphd.com

The website for David Park PhD and the Evidence-Based Entrepreneurship series. Plain HTML and CSS, hosted on GitHub Pages at https://www.davidparkphd.com.

- `index.html` the homepage (layout modeled on hubermanlab.com, look from the YouTube branding)
- `about.html` the full bio
- `episodes/` the episode list and one page per episode, built by `../build.py`
- `resources/` the worksheet library (`index.html`, built by `../build.py`) and the PDFs
- `styles.css` the shared styles for every page

Episode and resource pages, the sitemap and the shared nav and footer come from `website/build.py`. Edit its data and run `python3 website/build.py`, never the generated pages by hand.
- `images/` photos, thumbnails and icons
