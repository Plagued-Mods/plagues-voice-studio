"""Browse and play ANY audio export, including files made by older versions."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QTreeWidget, QTreeWidgetItem, QFileDialog, QMessageBox)
from .pvs_library import old_export_directories, new_export_directory

SUPPORTED = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}


class ExportBrowser(QWidget):
    def __init__(self, host):
        super().__init__(host)
        self.host = host
        self.roots: list[Path] = []
        self._build()
        saved = host.settings.value('export_browser/roots', [])
        if isinstance(saved, str):
            saved = [saved]
        for folder in [new_export_directory(host.storage), *old_export_directories(), *saved]:
            self.add_root(Path(folder), refresh=False)
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        description = QLabel("Play any narration in your exports, including recordings from older Plague's Voice Studio and Plagued Voice Studio versions. Older files are never moved or modified.")
        description.setWordWrap(True)
        layout.addWidget(description)
        tools = QHBoxLayout()
        self.folders = QComboBox()
        self.folders.currentIndexChanged.connect(self.refresh)
        tools.addWidget(self.folders, 1)
        add = QPushButton('Add folder...')
        add.clicked.connect(self._browse)
        tools.addWidget(add)
        refresh = QPushButton('Refresh')
        refresh.clicked.connect(self.refresh)
        tools.addWidget(refresh)
        layout.addLayout(tools)
        self.list = QTreeWidget()
        self.list.setHeaderLabels(['File', 'Modified', 'Location'])
        self.list.setRootIsDecorated(False)
        self.list.setAlternatingRowColors(True)
        self.list.setSortingEnabled(True)
        self.list.itemDoubleClicked.connect(lambda *_: self.play_selected())
        layout.addWidget(self.list, 1)
        action = QHBoxLayout()
        self.play = QPushButton('Play selected')
        self.play.clicked.connect(self.play_selected)
        action.addWidget(self.play)
        stop = QPushButton('Stop')
        stop.clicked.connect(self.host.player.stop)
        action.addWidget(stop)
        send = QPushButton('Use selected for Bethesda export')
        send.clicked.connect(self.send_selected)
        action.addWidget(send)
        show = QPushButton('Open containing folder')
        show.clicked.connect(self.open_selected)
        action.addWidget(show)
        layout.addLayout(action)
        self.info = QLabel('')
        layout.addWidget(self.info)

    def add_root(self, path: Path, *, refresh=True):
        path = path.expanduser()
        if path not in self.roots:
            self.roots.append(path)
            self.folders.addItem(str(path), str(path))
        if refresh:
            self.folders.setCurrentIndex(self.roots.index(path))
            self.host.settings.setValue('export_browser/roots', [str(x) for x in self.roots])
            self.refresh()

    def _browse(self):
        path = QFileDialog.getExistingDirectory(self, 'Choose a folder containing narration exports')
        if path:
            self.add_root(Path(path))

    def refresh(self):
        if not hasattr(self, 'list'):
            return
        self.list.clear()
        root_str = self.folders.currentData()
        if not root_str:
            return
        root = Path(root_str)
        if not root.is_dir():
            self.info.setText('This folder does not exist yet. Generate audio there or choose another directory.')
            return
        count = 0
        # Capped to avoid freezing Qt when a user chooses an entire drive.
        try:
            for path in root.rglob('*'):
                if not path.is_file() or path.suffix.lower() not in SUPPORTED:
                    continue
                modified = datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                item = QTreeWidgetItem([path.name, modified, str(path.parent)])
                item.setData(0, Qt.ItemDataRole.UserRole, str(path))
                self.list.addTopLevelItem(item)
                count += 1
                if count >= 3000:
                    break
        except OSError as exc:
            self.info.setText(f'Unable to scan export folder: {exc}')
            return
        self.info.setText(f'{count} playable files' + (' (first 3000 shown)' if count >= 3000 else ''))

    def selected_path(self) -> Path | None:
        item = self.list.currentItem()
        return Path(item.data(0, Qt.ItemDataRole.UserRole)) if item else None

    def play_selected(self):
        file = self.selected_path()
        if file and file.is_file():
            self.host._play_file(str(file))
        else:
            QMessageBox.information(self, 'Select an export', 'Choose a recording from the list first.')

    def send_selected(self):
        file = self.selected_path()
        if file and file.is_file():
            self.host.bethesda_tab.audio.setText(str(file))
            self.host.tabs.setCurrentWidget(self.host.bethesda_tab)
        else:
            QMessageBox.information(self, 'Select an export', 'Choose a recording first.')

    def open_selected(self):
        file = self.selected_path()
        if file:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(file.parent)))
