[Below is a ready-to-paste README.md for the add‑on.[11][12]](https://ankiweb.net/shared/info/202309288?cb=1761457955958)

# CSV Paste Import (Anki add‑on)[12][11]

Paste CSV directly into a dialog to create notes with automatic delimiter detection, optional header handling, note‑type selection by directive or smart matching, and a one‑click subdeck creator.[11][12]

### Features
- Paste CSV into a text box and import without saving a file.[11]
- Auto‑detect delimiter via csv.Sniffer with a robust fallback over comma, tab, semicolon, and pipe.[11]
- Note type directive at the top of the CSV: use “#notetype:Basic” or “#notetype:Cloze” to force selection.[11]
- Fallback note‑type auto‑pick based on header name similarity and column count if no directive is provided.[11]
- Optional “First row is header” checkbox to skip a header row during import.[11]
- Subdeck creator row that adds “Parent::Child” under the currently selected target deck and selects it.[11]
- Quick Import for direct note creation or open Anki’s standard Import dialog using a temporary CSV.[11]
- Tags can be provided in the last extra column and are split on whitespace.[11]

### Requirements
- Anki Desktop with Qt widgets available through Anki’s Qt bridge, as all widgets are imported from the Anki integration layer.[12]
- The dialog uses QWidget for the subdeck row to avoid QGroupBox child disable behavior in Qt.[13][14]

### Installation
- Place this add‑on’s folder in the add‑ons directory and restart Anki to register the “CSV Paste Import…” menu item under Tools.[12][11]
- The menu action is added on main window init via a hook that inserts a QAction into Tools.[11]

### Usage
- Open Tools → “CSV Paste Import…”.[11]
- Paste CSV content into the text area; the status line shows the detected delimiter, row count, and chosen note type.[11]
- Optionally add a subdeck name in “Add Subdeck” to create “Parent::YourName” beneath the selected Target Deck.[11]
- Choose Quick Import to add notes immediately, or “Import with Anki dialog” to review standard import options.[11]

### CSV directives
- Put a directive at the top to force note type, for example: “#notetype:Basic” or “#notetype:Cloze”.[11]
- Directive lines are stripped before delimiter detection, row counting, and import, so they never pollute the data.[11]
- Matching is case‑insensitive and supports common name variants like the standard Basic and Cloze names.[11]

### Auto‑detection details
- Delimiter detection tries csv.Sniffer first and falls back to a frequency‑and‑consistency check across the first lines.[11]
- Note‑type auto‑pick compares normalized header cells to field names and uses column count closeness if names are inconclusive.[11]
- The status line summarizes the detected delimiter, total rows, and the note type chosen by directive or heuristic.[11]

### Field mapping and tags
- Fields are filled left‑to‑right in the order of the selected note type’s fields.[11]
- If the row has more columns than fields, the last extra column is parsed as space‑separated tags.[11]

### Subdeck creation
- Enter a name in “Add Subdeck” to create a child deck under the currently selected Target Deck using “Parent::Child” format.[11]
- Decks are created via the collection API that returns or creates a deck ID for the given hierarchical name.[11]
- The subdeck UI uses a QWidget container rather than a QGroupBox so its children remain enabled under all styles.[14][13]

### Example CSV
- Basic:  
  “#notetype:Basic” then a header like “Front,Back,Tags” followed by lines such as “What is 2+2?,4,math”.[11]
- Cloze:  
  “#notetype:Cloze” with fields like “Text,Extra,Tags” and cloze content such as “{{c1::Humans}} landed on the moon in {{c1::1969}}.,,space”.[11]

### Buttons
- Quick Import adds notes immediately to the chosen deck and shows a completion summary including skipped empty rows.[11]
- Import with Anki dialog writes a temp CSV and opens Anki’s standard Import window for full control.[11]

### Troubleshooting
- “Add Subdeck” looks greyed out: ensure the row is wrapped in a QWidget container, not a QGroupBox, because QGroupBox can auto‑disable children.[13][14][11]
- NameError for QWidget: make sure QWidget is imported from the Anki Qt bridge in the dialog’s imports.[12][11]
- Directive doesn’t apply: confirm the exact note type name exists in your collection or rely on the heuristic auto‑pick.[11]

### How it integrates
- Widgets are imported through Anki’s Qt bridge module so the code stays compatible across Anki’s supported Qt versions.[12]
- The menu entry is registered on main window init and opens a modal QDialog implem# CSV Paste Import for Anki[11]

### Overview
Paste CSV directly into a dialog, auto‑detect the delimiter, optionally treat the first row as a header, pick the best matching note type (or force one with a directive), and create a subdeck under the selected deck before importing.[11]

### Key features
- Paste CSV into a text box and import without saving a file.[11]
- Auto‑detect delimiter with csv.Sniffer plus a robust fallback for comma, tab, semicolon, and pipe.[11]
- Optional “First row is header” checkbox that guides field matching and display.[11]
- Note type selection via directive at the top of the paste: “#notetype:Basic” or “#notetype:Cloze”.[12][11]
- Automatic note type guess when no directive is present, based on header/field name similarity and column count.[11]
- Create a new subdeck under the currently selected deck using a dedicated input and button.[11]
- Subdeck row uses QWidget (not QGroupBox) so it never auto‑disables its children under Qt’s checkable group behavior.[13][14][11]

### Requirements
- Desktop Anki with Qt support; widgets are imported through Anki’s Qt shim to stay compatible across versions.[15][11]

### Install
- Place this folder as an Anki add‑on and restart Anki, then open Tools → CSV Paste Import.[11]
- The add‑on registers a menu action via a main‑window hook so it appears after Anki starts.[11]

### Usage
1) Open Tools → CSV Paste Import.[11]
2) Paste your CSV into “CSV Content”; delimiter will be detected and shown in the status strip.[11]
3) Optionally check “First row is header” so header names can guide note‑type selection.[11]
4) Choose a Target Deck, or type a name in “Add Subdeck” and click “Create subdeck” to make and select a nested deck.[11]
5) Either click Quick Import for a direct add, or Import with Anki dialog to pass a temp file into Anki’s standard importer.[11]

### CSV directives
- Force a specific note type by placing a directive on the first lines of the paste, e.g., “#notetype:Basic” or “#notetype:Cloze”.[12][11]
- Directive lines are stripped before delimiter detection and import so they don’t pollute parsing.[11]
- If the directive name doesn’t match any existing model, the dialog falls back to header/column‑based auto‑pick.[11]

### Auto note‑type matching
- Header fields are normalized and compared against each model’s field names to compute a similarity score.[11]
- Column count closeness provides a secondary score so matching field counts are preferred.[11]
- The best score sets the Note Type combobox automatically, but you can override it.[11]

### Subdeck creation
- Enter a subdeck name and click “Create subdeck” to create “Parent::Child” under the currently selected deck, then select it.[11]
- Implementation uses mw.col.decks.id() to create if missing and refreshes the deck list afterward.[11]

### Field mapping and tags
- The importer fills fields left‑to‑right up to the number of fields in the selected note type.[11]
- If there are extra columns, the last column is treated as tags and split on whitespace.[11]

### Quick Import vs. Anki dialog
- Quick Import constructs notes directly in the collection and assigns them to the selected deck.[11]
- Import with Anki dialog writes a temp CSV and opens Anki’s standard Import UI for full control.[11]

### Status strip
- Shows detected delimiter, total row count, and the chosen note type; if chosen via directive it notes “via directive.”[11]
- When “Auto‑detect” is selected, the strip reiterates the delimiter used during import.[11]

### Troubleshooting
- “Add Subdeck” greyed out: this build uses QWidget for that row to avoid QGroupBox’s auto‑disable behavior under Qt; if you see it disabled, ensure you’re on this version and that at least one deck is present.[14][13][11]
- NameError for QWidget: ensure QWidget is included in the aqt.qt imports list at the top of the file.[15][11]
- Nothing imports: confirm the delimiter and header setting, and verify the selected note type has enough fields for your columns.[11]

### Privacy and data
- All parsing happens locally inside Anki, and temp files are only created when launching the default import dialog.[11]

### Uninstall
- Remove the add‑on folder and restart Anki to remove the menu entry and dialog.[11]

### Credits
- Built against Anki’s Qt layer and collection APIs so it remains compatible with Anki’s widget stack and model/deck managers.[15][11]

[1](https://www.reddit.com/r/Anki/comments/1k4yemm/ankimin_beautiful_minimal_card_templates_for_anki/)
[2](https://ankiweb.net/shared/addons)
[3](https://ankiweb.net/shared/info/904999275)
[4](https://forums.ankiweb.net/t/add-on-structure/37422)
[5](https://community.silverbullet.md/t/markdown-files-to-anki-notes/1644)
[6](https://ankiweb.net/shared/info/354124843)
[7](https://ankiweb.net/shared/info/162313389)
[8](https://ankiweb.net/shared/addons?search=Markdown)
[9](https://gitlab.phaidra.org/kartenaale/sinologie-anki-pack/-/blob/1.1.4/README.md)
[10](https://sourceforge.net/projects/anki.mirror/files/25.09.2/README.md/download)
[11](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/6472502/58e357a9-2a94-435b-8d7a-bc038a2ba9a4/init.py)
[12](https://docs.ankiweb.net/editing.html)
[13](https://doc.qt.io/qt-6/qgroupbox.html)
[14](https://doc.qt.io/qt-6/qwidget.html)
[15](https://addon-docs.ankiweb.net/qt.html)enting the paste‑import workflow.[11]

### Notes on privacy
- All parsing and importing happens locally in the Anki process without network access.[11]

### Support
- If you customize field orders or use non‑standard note types, double‑check field alignment since mapping is positional.[11]

This README reflects the current code behavior in the provided __init__.py and Anki’s Qt integration approach.[12][11]

[1](https://github.com/tianshanghong/awesome-anki)
[2](https://www.reddit.com/r/Anki/comments/cog19l/files_useful_to_create_addons/)
[3](https://forums.ankiweb.net/t/enhancement-request-use-github-as-addon-codebase-with-ankiweb-addon-page-copying-that-github-data/27546)
[4](https://ankiweb.net/shared/info/2063785767)
[5](https://www.youtube.com/watch?v=PkEnckXc7yk)
[6](https://www.youtube.com/watch?v=e6HMD32hngQ)
[7](https://ankiweb.net/shared/info/308574457)
[8](https://forums.ankiweb.net/t/a-new-drag-and-drop-interactive-matching-template/55002)
[9](https://publish.obsidian.md/hub/02+-+Community+Expansions/02.05+All+Community+Expansions/Auxiliary+Tools/obsidianki4)
[10](https://ankiweb.net/shared/info/871222788)
[11](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/6472502/58e357a9-2a94-435b-8d7a-bc038a2ba9a4/init.py)
[12](https://addon-docs.ankiweb.net/qt.html)
[13](https://doc.qt.io/qt-6/qwidget.html)
[14](https://doc.qt.io/qt-6/qgroupbox.html)
