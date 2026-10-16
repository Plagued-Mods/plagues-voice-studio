"""Searchable, keyboard-friendly help center. No WebEngine or internet required."""
from __future__ import annotations
import re
import sys
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QLineEdit,
    QTextBrowser, QPushButton, QFrame, QSplitter, QComboBox,
)

# (Title, tags used for filtering, human-maintained documentation).
# Text is not externally loaded and does not execute scripts.
TOPICS: tuple[tuple[str, str, str], ...] = (
    ('Getting started', 'quick start narrator beginner generate', '''
<h2>Getting started</h2>
<p>Plague's Voice Studio is a local narration workstation. No account is required to write scripts or manage your recordings.</p>
<ol><li><b>Choose a model</b> in Narration Studio. For a quick CPU test, try Nano.</li>
<li><b>Choose a voice</b>, if that model requires a reference recording.</li>
<li><b>Write or import</b> your script. Short paragraphs work well for spoken delivery.</li>
<li><b>Generate now</b> or add multiple jobs to the Batch Queue.</li>
<li><b>Review</b> the result in Export Library, then send it to Bethesda Voice Export if needed.</li></ol>
<h3>Offline models</h3><p>Models bundled during a <b>FullOffline</b> build are available without downloads. Otherwise the program may download model weights on first use. The build option and the model chosen in the GUI are separate.</p>
'''),
    ('Models and voices', 'nano turbo original english multilingual tags reference expressive clone', '''
<h2>Models and voices</h2>
<table width="100%" cellspacing="0" cellpadding="7">
<tr><th align="left">Model</th><th align="left">Best use</th><th align="left">Vocal tags</th></tr>
<tr><td><b>Nano</b></td><td>Compact English / CPU-first</td><td>Some native tags</td></tr>
<tr><td><b>Turbo</b></td><td>Expressive English, voice reference required</td><td>Native vocal-event tags</td></tr>
<tr><td><b>Original English</b></td><td>Expressiveness and CFG controls</td><td>Not native vocal-event tags</td></tr>
<tr><td><b>Multilingual V3</b></td><td>Language selection and voice controls</td><td>Not Turbo-style tags</td></tr></table>
<p><b>References:</b> Prefer 6–20 seconds of clean, single-speaker audio with no music. Only use recordings you own or have permission to clone.</p>
<p>Legacy voice references from v0.1.x are offered read-only. The current app stores newly imported recordings in its own data directory.</p>
<p><b>Original English controls:</b> Start around expressiveness 0.50 and CFG 0.50, then make small adjustments while listening.</p>
'''),
    ('Script tags', 'pause rate volume emphasis laugh chuckle sigh cough syntax markup', '''
<h2>Script tags and markup</h2>
<h3>Handled by Plague's Voice Studio</h3>
<p>These directives are interpreted by the <b>application</b> and work with all supported models. The model does not pronounce the directives.</p>
<pre>[pause:0.8s]
[pause:800ms]
[rate:0.90]Speak slowly.[/rate]
[volume:0.85]Speak quietly.[/volume]
[emphasis]Important words.[/emphasis]</pre>
<p>Maximum exact pause: 10 seconds. Rate: 0.50 to 2.00, volume: 0.00 to 2.00. App emphasis adds gain; it does not guarantee the model changes its performance.</p>
<h3>Chatterbox vocal-event tags</h3>
<p>Tags such as <code>[laugh]</code>, <code>[chuckle]</code>, and <code>[sigh]</code> are passed to the speech model. They are best suited to Turbo or Nano. Original English and Multilingual V3 do not have the same native tag support and may read them as words.</p>
<p>Use <b>Check tags</b> to validate app-level syntax and inspect how the script will be split. Non-native vocal tags are not a guaranteed effect.</p>
'''),
    ('Export Library', 'recordings browse play wav mp3 older file folders playback', '''
<h2>Export Library</h2>
<p>Choose a folder to browse and play earlier renders. Double-click a recording or use <b>Play selected</b>.</p>
<p>Use <b>Add folder</b> to include another export directory. Older exported audio is not moved, edited, or deleted. Supported playback formats depend on codecs available to Qt Multimedia on your computer.</p>
<p><b>Use selected for Bethesda export</b> loads the file path into the game-audio converter; it does not alter the recording itself.</p>
<p>New exports are automatically named from the selected voice and a timestamp, unless you explicitly enter a filename. Existing files are not silently overwritten.</p>
'''),
    ('Bethesda voice export', 'fallout skyrim lip xwm fuz game data mo2 mod voice type response facefx', '''
<h2>Bethesda voice export</h2>
<p>This workflow builds a Fallout 4 / Skyrim-compatible FUZ file and can place it in an exact game or mod folder. <b>The game plugin is not opened or edited.</b></p>
<ol><li>Save a project with the owning plugin filename and the target <b>Data</b> folder or MO2 mod root.</li>
<li>Save a Voice Profile pairing a Creation Kit <b>VoiceType EditorID</b> with a Chatterbox voice/model.</li>
<li>Choose the generated recording and enter the <b>exact dialogue response filename</b> from the Creation Kit.</li>
<li>Supply the correctly licensed external FaceFX, Fonix, xWMA and optionally FFmpeg tools.</li>
<li>Check the destination preview and approve any replacement.</li></ol>
<p><b>Expected path:</b> <code>Sound/Voice/&lt;OwningPlugin&gt;/&lt;VoiceType&gt;/&lt;Response&gt;.fuz</code></p>
<p><b>Important:</b> Real LIP and XWM generation depends on compatible external tools; structurally valid FUZ packing does not guarantee in-game audio or lip-sync success. Test in the target game.</p>
'''),
    ('Build and troubleshooting', 'install windows offline build model download paging error 1455 python exe', '''
<h2>Build and troubleshooting</h2>
<h3>Windows portable build</h3>
<pre>powershell -ExecutionPolicy Bypass -File .\\scripts\\build_windows.ps1 -Models turbo</pre>
<h3>All models, fully offline</h3>
<pre>powershell -ExecutionPolicy Bypass -File .\\scripts\\build_windows.ps1 -FullOffline</pre>
<p>Once all four models are already downloaded in the project, <code>-FullOffline -SkipModels</code> skips the downloads but still verifies the model files.</p>
<h3>Common problems</h3>
<p><b>OS error 1455:</b> Windows has insufficient available virtual memory (RAM plus paging file) for the model load. Close memory-intensive applications and check your system-managed paging file and disk space.</p>
<p><b>A Python traceback when opening a dialog:</b> rebuild the executable after source edits. An old desktop shortcut may still point to an older version.</p>
<p><b>First generation seems slow:</b> first use may load or download model weights and initialize PyTorch. CPU inference can be significantly slower than GPU inference.</p>
<p><b>Windows AMD GPU:</b> this build does not automatically enable AMD acceleration. Auto selects CUDA only where supported; otherwise it uses CPU.</p>
'''),
    ('Privacy and licenses', 'permissions watermark local data licensing credits copyright internet', '''
<h2>Privacy, permissions and licenses</h2>
<p>Speech synthesis and voice-reference handling are local after required models have been downloaded. Initial weight retrieval may contact Hugging Face or other upstream model providers.</p>
<p>Only clone a person's voice with their permission. <b>Chatterbox's upstream watermarking has not been removed.</b></p>
<p>Chatterbox TTS is developed by <b>Resemble AI</b>; third-party libraries, model weights and game conversion utilities retain their individual terms. See <code>THIRD_PARTY_NOTICES.md</code> in the project.</p>
<p><a href="https://github.com/resemble-ai/chatterbox">Resemble AI's Chatterbox source</a></p>
'''),
)

# QTextDocument HTML support is a subset of browser HTML. Keep it conservative.
DOC_CSS = '''<style>
body { color: #e0eee2; background: #0e1716; font-family: Segoe UI, sans-serif; font-size: 14px; }
h2 { color: #b0f8b9; font-size: 22px; margin-bottom: 12px; }
h3 { color: #c6ead0; font-size: 17px; margin-top: 18px; }
p, li { line-height: 1.4; margin-bottom: 8px; }
a { color: #8cddff; } code, pre { color: #e8f0de; background: #233528; }
th { color: #b1ffbe; background: #20382a; } td { background: #18251e; }
</style>'''


def matched_topic_indices(query: str) -> list[int]:
    words = query.lower().strip().split()
    if not words:
        return list(range(len(TOPICS)))
    return [i for i, (title, keywords, html) in enumerate(TOPICS)
            if all(word in (title + ' ' + keywords + ' ' + html).lower() for word in words)]


class HelpCenter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('help_center')
        self._zoom = 100
        self._current_html = ''
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(12)

        title_row = QHBoxLayout()
        label = QLabel('Help center')
        label.setObjectName('sectionTitle')
        title_row.addWidget(label)
        title_row.addStretch()
        subtitle = QLabel('Local guide  •  Search topics and examples')
        subtitle.setObjectName('mutedText')
        title_row.addWidget(subtitle)
        outer.addLayout(title_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        sidebar = QFrame()
        sidebar.setObjectName('helpSidebar')
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(12, 12, 12, 12)
        artwork = QLabel()
        artwork.setObjectName('help_logo')
        artwork.setAlignment(Qt.AlignmentFlag.AlignCenter)
        base = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[2]))
        logo = QPixmap(str(base / 'assets' / 'plagues-voice-studio-logo.png'))
        if not logo.isNull():
            artwork.setPixmap(logo.scaled(134, 134, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation))
        artwork.setFixedHeight(136)
        side.addWidget(artwork)
        side.addWidget(QLabel('FIND A TOPIC'))
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search help topics…')
        self.search.setAccessibleName('Search help topics')
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter)
        side.addWidget(self.search)
        self.topic_list = QListWidget()
        self.topic_list.setObjectName('help_topics')
        self.topic_list.setAccessibleName('Help topics')
        self.topic_list.currentRowChanged.connect(self._select)
        side.addWidget(self.topic_list, 1)
        shortcuts = QLabel('Ctrl+F focuses search.\nUse Up/Down to browse topics.')
        shortcuts.setObjectName('mutedText')
        shortcuts.setWordWrap(True)
        side.addWidget(shortcuts)
        splitter.addWidget(sidebar)

        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(6, 0, 0, 0)
        tools = QHBoxLayout()
        tools.addWidget(QLabel('Guide'))
        tools.addStretch()
        tools.addWidget(QLabel('Text size'))
        self.font_size = QComboBox()
        self.font_size.setAccessibleName('Help text size')
        for p in (90, 100, 115, 130, 150):
            self.font_size.addItem(f'{p}%', p)
        self.font_size.setCurrentIndex(1)
        self.font_size.currentIndexChanged.connect(self._font_changed)
        tools.addWidget(self.font_size)
        main_layout.addLayout(tools)
        self.browser = QTextBrowser()
        self.browser.setObjectName('help_article')
        self.browser.setAccessibleName('Help article')
        self.browser.setOpenExternalLinks(True)
        main_layout.addWidget(self.browser, 1)
        splitter.addWidget(main)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([245, 690])
        outer.addWidget(splitter, 1)
        self._filter('')

    def _filter(self, query: str):
        previous = self.topic_list.currentItem()
        previous_id = previous.data(Qt.ItemDataRole.UserRole) if previous is not None else 0
        ids = matched_topic_indices(query)
        self.topic_list.blockSignals(True)
        self.topic_list.clear()
        for i in ids:
            self.topic_list.addItem(TOPICS[i][0])
            self.topic_list.item(self.topic_list.count() - 1).setData(Qt.ItemDataRole.UserRole, i)
        self.topic_list.blockSignals(False)
        if not ids:
            self._current_html = '<h2>No matches found</h2><p>Try a shorter search term.</p>'
            self._apply_zoom()
        else:
            idx = ids.index(previous_id) if previous_id in ids else 0
            self.topic_list.setCurrentRow(idx)

    def _select(self, row: int):
        if row < 0:
            return
        item = self.topic_list.item(row)
        if item is None:
            return
        idx = item.data(Qt.ItemDataRole.UserRole)
        self._current_html = TOPICS[int(idx)][2]
        self._apply_zoom()
        self.browser.moveCursor(QTextCursor.MoveOperation.Start)

    def _font_changed(self, _index: int):
        self._zoom = self.font_size.currentData() or 100
        self._apply_zoom()

    def _apply_zoom(self):
        if self._current_html:
            css = re.sub(r'font-size: (\d+)px;',
                         lambda m: f'font-size: {round(int(m.group(1)) * self._zoom / 100)}px;',
                         DOC_CSS)
            self.browser.setHtml(css + self._current_html)

    def focus_search(self):
        self.search.setFocus()
        self.search.selectAll()
