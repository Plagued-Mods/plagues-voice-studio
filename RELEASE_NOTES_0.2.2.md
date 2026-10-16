# Plague's Voice Studio 0.2.2

- Fixed Export Library startup `NameError` in `export_browser.py`: references `self.host.player.stop`.
- Added a packaged Qt window startup smoke test to Windows build script. Installer construction fails if it cannot initialize the GUI.
- Included full branded logo in PyInstaller distribution for Help/About.
- Updated standalone Windows EXE to `PlaguesVoiceStudio023.exe` and separate installer identity.
- Retained the existing v0.2.1 storage/settings keys to preserve project, voices and export locations.
- No changes to Chatterbox synthesis or Bethesda voice-export algorithms.

Requires local Windows build. This ZIP contains Python source only.
