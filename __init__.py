# -*- coding: utf-8 -*-
"""
CSV Paste Import Add-on for Anki
Allows direct pasting of CSV content with automatic delimiter detection
"""

from aqt import mw, gui_hooks
from aqt.qt import (
    QAction, QCheckBox, QComboBox, QDialog, QFormLayout, QGroupBox, QLabel,
    QHBoxLayout, QPlainTextEdit, QPushButton, QVBoxLayout
)
from aqt.utils import showInfo, showWarning
from aqt.importing import importFile
import csv
import io
import os
import tempfile


class CSVPasteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.deck_infos = []
        self.model_infos = []
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("CSV Paste Import")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout()

        instructions = QLabel(
            "<b>Instructions:</b><br>"
            "1. Paste CSV below (delimiter auto-detected)<br>"
            "2. Optional: check 'First row is header'<br>"
            "3. Choose deck and note type<br>"
            "4. Click 'Quick Import' (direct) or 'Import with Anki dialog' (full UI)<br><br>"
            "<b>Supported delimiters:</b> comma, tab, semicolon, pipe"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        layout.addWidget(QLabel("CSV Content:"))
        self.csv_text = QPlainTextEdit()
        self.csv_text.setPlaceholderText(
            "Paste CSV here...\n\n"
            "Examples:\n"
            "What is the capital of France?,Paris,geography\n"
            "What is 2+2?,4,math\n\n"
            "OR with tabs:\n"
            "Front\tBack\tTags\n"
            "Question\tAnswer\ttag1"
        )
        self.csv_text.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.csv_text)

        # Detection status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #21808D; font-weight: 500;")
        layout.addWidget(self.status_label)

        settings_group = QGroupBox("Import Settings")
        settings_layout = QFormLayout()

        # Decks
        self.deck_combo = QComboBox()
        try:
            self.deck_infos = list(mw.col.decks.all_names_and_ids())
        except Exception:
            self.deck_infos = []
        self.deck_combo.addItems([d.name for d in self.deck_infos])

        # Default: current deck
        try:
            cur = mw.col.decks.current()
            try:
                cur_name = cur["name"]
            except TypeError:
                cur_name = cur.name
            idx = self.deck_combo.findText(cur_name)
            if idx >= 0:
                self.deck_combo.setCurrentIndex(idx)
        except Exception:
            pass
        settings_layout.addRow("Target Deck:", self.deck_combo)

        # Note types
        self.notetype_combo = QComboBox()
        try:
            self.model_infos = list(mw.col.models.all_names_and_ids())
        except Exception:
            self.model_infos = []
        self.notetype_combo.addItems([m.name for m in self.model_infos])
        settings_layout.addRow("Note Type:", self.notetype_combo)

        # Delimiter selection (now with Auto option)
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems([
            "Auto-detect",
            "Comma (,)",
            "Tab",
            "Semicolon (;)",
            "Pipe (|)"
        ])
        self.delimiter_combo.setCurrentIndex(0)  # Default to auto-detect
        settings_layout.addRow("Delimiter:", self.delimiter_combo)

        # Header checkbox
        self.header_check = QCheckBox("First row is header")
        settings_layout.addRow("", self.header_check)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Buttons
        btns = QHBoxLayout()
        
        # Quick import button (direct import)
        self.import_btn = QPushButton("Quick Import")
        self.import_btn.clicked.connect(self.do_import)
        self.import_btn.setDefault(True)
        
        # Anki dialog button (use standard import UI)
        self.import_anki_btn = QPushButton("Import with Anki dialog")
        self.import_anki_btn.clicked.connect(self.open_with_default_importer)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btns.addStretch()
        btns.addWidget(self.import_btn)
        btns.addWidget(self.import_anki_btn)
        btns.addWidget(cancel_btn)
        
        layout.addLayout(btns)
        self.setLayout(layout)

    def on_text_changed(self):
        """Update status when text changes"""
        if self.delimiter_combo.currentText() == "Auto-detect":
            content = self.csv_text.toPlainText().strip()
            if content:
                try:
                    delimiter, rows = self.detect_csv_format(content)
                    delim_name = self.get_delimiter_name(delimiter)
                    self.status_label.setText(
                        f"✓ Detected: {delim_name} delimiter, {rows} row(s)"
                    )
                except Exception as e:
                    self.status_label.setText(f"⚠ Detection failed: {str(e)}")
            else:
                self.status_label.setText("")

    def detect_csv_format(self, content):
        """
        Auto-detect CSV delimiter and count rows
        Returns: (delimiter, row_count)
        """
        sample = content[:2048]  # Use first 2KB for detection
        
        # Try csv.Sniffer first
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=',;\t|')
            delimiter = dialect.delimiter
        except Exception:
            # Fallback: count occurrences of common delimiters
            delimiter = self.fallback_delimiter_detection(sample)
        
        # Count rows
        reader = csv.reader(io.StringIO(content), delimiter=delimiter)
        rows = sum(1 for _ in reader)
        
        return delimiter, rows

    def fallback_delimiter_detection(self, sample):
        """
        Fallback delimiter detection by counting occurrences
        """
        lines = sample.split('\n')[:5]  # Check first 5 lines
        if not lines:
            return ','
        
        delimiters = [',', '\t', ';', '|']
        delimiter_counts = {}
        
        for delim in delimiters:
            # Count average occurrences per line
            counts = [line.count(delim) for line in lines if line.strip()]
            if counts:
                avg = sum(counts) / len(counts)
                # Check consistency (same count across lines)
                if len(set(counts)) == 1 and counts[0] > 0:
                    delimiter_counts[delim] = (avg, True)  # Consistent
                elif avg > 0:
                    delimiter_counts[delim] = (avg, False)  # Inconsistent
        
        # Prefer consistent delimiter with highest count
        if delimiter_counts:
            sorted_delims = sorted(
                delimiter_counts.items(),
                key=lambda x: (x[1][1], x[1][0]),  # Sort by (consistent, count)
                reverse=True
            )
            return sorted_delims[0][0]
        
        return ','  # Default to comma

    def get_delimiter_name(self, delimiter):
        """Convert delimiter character to readable name"""
        names = {
            ',': 'Comma (,)',
            '\t': 'Tab',
            ';': 'Semicolon (;)',
            '|': 'Pipe (|)'
        }
        return names.get(delimiter, f"'{delimiter}'")

    def get_delimiter(self):
        """Get the delimiter based on selection or auto-detect"""
        selection = self.delimiter_combo.currentText()
        
        if selection == "Auto-detect":
            content = self.csv_text.toPlainText().strip()
            if content:
                try:
                    delimiter, _ = self.detect_csv_format(content)
                    return delimiter
                except Exception:
                    return ','  # Fallback to comma
            return ','
        
        # Manual selection
        mapping = {
            "Comma (,)": ",",
            "Tab": "\t",
            "Semicolon (;)": ";",
            "Pipe (|)": "|",
        }
        return mapping.get(selection, ',')

    def _deck_id_from_index(self, i):
        if not self.deck_infos:
            return None
        d = self.deck_infos[i]
        return getattr(d, "id", getattr(d, "did", None))

    def _model_id_from_index(self, i):
        if not self.model_infos:
            return None
        m = self.model_infos[i]
        return getattr(m, "id", None)

    def open_with_default_importer(self):
        """Open Anki's standard import dialog with the pasted CSV"""
        csv_content = self.csv_text.toPlainText().strip()
        if not csv_content:
            showWarning("Please paste CSV content first.")
            return

        # Select the target deck first so dialog picks sensible defaults
        deck_idx = self.deck_combo.currentIndex()
        deck_id = self._deck_id_from_index(deck_idx)
        if deck_id is not None:
            try:
                mw.col.decks.select(deck_id)
            except Exception:
                pass

        # Write to a temporary CSV file
        try:
            fd, path = tempfile.mkstemp(prefix="anki_csv_paste_", suffix=".csv", text=True)
            try:
                with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
                    f.write(csv_content)
            except Exception as e:
                os.close(fd)
                showWarning(f"Could not write temp CSV: {e}")
                return
        except Exception as e:
            showWarning(f"Could not create temp file: {e}")
            return

        # Open Anki's default Import dialog with this file
        try:
            importFile(mw, path)
            # Close our dialog since user will use Anki's import UI
            self.accept()
        except Exception as e:
            showWarning(f"Could not open import dialog: {e}")
            # Clean up temp file on failure
            try:
                os.unlink(path)
            except Exception:
                pass

    def do_import(self):
        """Quick import - directly add cards without showing Anki's import dialog"""
        csv_content = self.csv_text.toPlainText().strip()
        if not csv_content:
            showWarning("Please paste CSV content first.")
            return

        deck_idx = self.deck_combo.currentIndex()
        model_idx = self.notetype_combo.currentIndex()
        deck_id = self._deck_id_from_index(deck_idx)
        model_id = self._model_id_from_index(model_idx)

        if deck_id is None:
            showWarning("Could not resolve target deck.")
            return
        if model_id is None:
            showWarning("Could not resolve note type.")
            return

        try:
            notetype = mw.col.models.get(model_id)
            if not notetype:
                showWarning("Selected note type not found.")
                return

            delimiter = self.get_delimiter()
            reader = csv.reader(io.StringIO(csv_content), delimiter=delimiter)
            rows = [r for r in reader]
            
            if not rows:
                showWarning("No data rows found.")
                return
                
            # Show delimiter info if auto-detected
            if self.delimiter_combo.currentText() == "Auto-detect":
                delim_name = self.get_delimiter_name(delimiter)
                self.status_label.setText(f"✓ Using {delim_name} delimiter")
            
            if self.header_check.isChecked() and len(rows) > 1:
                rows = rows[1:]

            field_names = [f["name"] for f in notetype["flds"]]
            mw.col.decks.select(deck_id)

            added = 0
            skipped_empty = 0

            for row in rows:
                if not row or all(not c.strip() for c in row):
                    skipped_empty += 1
                    continue

                note = mw.col.new_note(notetype)

                # Fill fields
                for i, val in enumerate(row[:len(field_names)]):
                    note.fields[i] = val.strip()

                # Tags from last extra column
                if len(row) > len(field_names):
                    tags = row[-1].strip()
                    if tags:
                        note.tags = tags.split()

                mw.col.add_note(note, deck_id)
                added += 1

            mw.reset()
            
            msg = f"Import complete!\n\nAdded: {added} note(s)"
            if skipped_empty:
                msg += f"\nSkipped empty rows: {skipped_empty}"
            if self.delimiter_combo.currentText() == "Auto-detect":
                msg += f"\n\nUsed delimiter: {self.get_delimiter_name(delimiter)}"
                
            showInfo(msg)
            self.accept()

        except Exception as e:
            showWarning(f"Import failed: {str(e)}")


def show_csv_paste_dialog():
    dlg = CSVPasteDialog(mw)
    dlg.exec()


def setup_menu():
    action = QAction("CSV Paste Import...", mw)
    action.triggered.connect(show_csv_paste_dialog)
    mw.form.menuTools.addAction(action)


gui_hooks.main_window_did_init.append(setup_menu)
