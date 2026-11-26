from pathlib import Path

from ebooklib import epub, ITEM_DOCUMENT, ITEM_IMAGE
from bs4 import BeautifulSoup

#==================================================
#               REDO ME
#==================================================
class EpubBook:
    """
    Simple wrapper around an EPUB file.

    Provides:
        - Book metadata
        - Authors
        - Series information
        - Cover image
        - Chapters in reading order
        - Chapter HTML
        - Chapter plain text
    """

    def __init__(self, path):
        self.path = Path(path)

        if not self.path.exists():
            raise FileNotFoundError(f"EPUB not found: {self.path}")

        if self.path.suffix.lower() != ".epub":
            raise ValueError(f"Not an EPUB file: {self.path}")

        self.book = epub.read_epub(str(self.path))

        self._chapters = None
        self._cover = None

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def _metadata(self, name, default=None):
        """
        Get the first value for a Dublin Core metadata field.
        """
        values = self.book.get_metadata("DC", name)

        if not values:
            return default

        return values[0][0]

    @property
    def title(self):
        """Book title."""
        return self._metadata("title", self.path.stem)

    @property
    def authors(self):
        """List of authors."""
        return [
            value[0]
            for value in self.book.get_metadata("DC", "creator")
        ]

    @property
    def language(self):
        """Book language, such as 'en'."""
        return self._metadata("language")

    @property
    def identifier(self):
        """Book's EPUB identifier."""
        return self._metadata("identifier")

    @property
    def publisher(self):
        """Publisher."""
        return self._metadata("publisher")

    @property
    def description(self):
        """Book description."""
        return self._metadata("description")

    @property
    def date(self):
        """Publication date."""
        return self._metadata("date")

    # ------------------------------------------------------------------
    # Series
    # ------------------------------------------------------------------

    @property
    def series(self):
        """
        Try to get the series name.

        EPUBs are inconsistent about how series information is stored,
        so this checks several common metadata formats.
        """

        # Calibre-style metadata
        calibre_series = self.book.get_metadata(
            "OPF", "meta"
        )

        for value, attributes in calibre_series:
            if attributes.get("name") == "calibre:series":
                return value

        # EPUB 3 belongs-to-series metadata
        for value, attributes in calibre_series:
            if attributes.get("property") == "belongs-to":
                return value

        return None

    @property
    def series_index(self):
        """Try to get the book's position in its series."""

        calibre_series = self.book.get_metadata(
            "OPF", "meta"
        )

        for value, attributes in calibre_series:
            if attributes.get("name") == "calibre:series_index":
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return value

        return None

    # ------------------------------------------------------------------
    # Cover
    # ------------------------------------------------------------------

    @property
    def cover(self):
        """
        Return the cover image as bytes.

        Returns None if the EPUB doesn't contain a detectable cover.
        """

        if self._cover is not None:
            return self._cover

        # Try EPUB/Calibre cover metadata first
        cover_id = None

        for value, attributes in self.book.get_metadata("OPF", "meta"):
            if attributes.get("name") == "cover":
                cover_id = attributes.get("content")
                break

        if cover_id:
            item = self.book.get_item_with_id(cover_id)

            if item:
                self._cover = item.get_content()
                return self._cover

        # Try to find an image called "cover"
        for item in self.book.get_items_of_type(ITEM_IMAGE):
            name = item.get_name().lower()

            if "cover" in name:
                self._cover = item.get_content()
                return self._cover

        return None

    # ------------------------------------------------------------------
    # Chapters
    # ------------------------------------------------------------------

    @property
    def chapters(self):
        """
        Return chapters in EPUB reading/spine order.

        Each chapter is a dictionary containing:

            id
            file
            title
            html
            text
            item
        """

        if self._chapters is not None:
            return self._chapters

        chapters = []

        # EPUB spine defines the correct reading order.
        for spine_entry in self.book.spine:
            item_id = spine_entry[0]

            item = self.book.get_item_with_id(item_id)

            if item is None:
                continue

            if item.get_type() != ITEM_DOCUMENT:
                continue

            html = item.get_content()

            soup = BeautifulSoup(html, "html.parser")

            # Try to determine a useful chapter title.
            title = self._get_chapter_title(soup)

            # Plain text version
            text = soup.get_text("\n", strip=True)

            chapters.append({
                "id": item.get_id(),
                "file": item.get_name(),
                "title": title,
                "html": html,
                "text": text,
                "item": item,
            })

        self._chapters = chapters

        return chapters

    def _get_chapter_title(self, soup):
        """
        Try several methods of finding a chapter title.
        """

        # <h1>
        heading = soup.find("h1")

        if heading:
            text = heading.get_text(" ", strip=True)

            if text:
                return text

        # <h2>
        heading = soup.find("h2")

        if heading:
            text = heading.get_text(" ", strip=True)

            if text:
                return text

        # <title>
        if soup.title:
            text = soup.title.get_text(" ", strip=True)

            if text:
                return text

        return None

    @property
    def chapter_count(self):
        """Number of chapters/documents in the reading order."""
        return len(self.chapters)

    def get_chapter(self, index):
        """
        Get a chapter by zero-based index.

        Example:
            book.get_chapter(0)
        """

        return self.chapters[index]

    # ------------------------------------------------------------------
    # Table of contents
    # ------------------------------------------------------------------

    @property
    def table_of_contents(self):
        """
        Return the EPUB's table of contents.

        This is returned as a list of dictionaries:

            {
                "title": ...,
                "href": ...,
                "children": [...]
            }
        """

        return self._parse_toc(self.book.toc)

    def _parse_toc(self, entries):
        result = []

        for entry in entries:

            # Link
            if isinstance(entry, epub.Link):
                result.append({
                    "title": entry.title,
                    "href": entry.href,
                    "children": [],
                })

            # Section with children
            elif isinstance(entry, epub.Section):
                result.append({
                    "title": entry.title,
                    "href": entry.href,
                    "children": self._parse_toc(entry.subitems),
                })

            # Sometimes nested tuples/lists appear
            elif isinstance(entry, (list, tuple)):
                result.extend(self._parse_toc(entry))

        return result

    # ------------------------------------------------------------------
    # Resources
    # ------------------------------------------------------------------

    def get_images(self):
        """
        Return all images in the EPUB.

        Each result contains:

            {
                "id": ...,
                "file": ...,
                "media_type": ...,
                "data": ...
            }
        """

        images = []

        for item in self.book.get_items_of_type(ITEM_IMAGE):
            images.append({
                "id": item.get_id(),
                "file": item.get_name(),
                "media_type": item.media_type,
                "data": item.get_content(),
            })

        return images

    def get_item(self, item_id):
        """Get an EPUB item by its ID."""

        return self.book.get_item_with_id(item_id)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"EpubBook("
            f"title={self.title!r}, "
            f"authors={self.authors!r}, "
            f"chapters={self.chapter_count})"
        )