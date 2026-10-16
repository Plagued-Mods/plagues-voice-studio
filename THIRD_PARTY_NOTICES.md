# Third-party notices

Plague's Voice Studio was created by Kaotick Jay. It is an independent graphical frontend, not an official Resemble AI product.

- **Chatterbox** by Resemble AI: MIT-licensed source, audio watermarking retained.
  https://github.com/resemble-ai/chatterbox
- **Model weights**: distributed separately by Resemble AI via Hugging Face.
  Review license/model cards and usage conditions before redistributing bundles.
- **PyTorch**: BSD-style license, https://pytorch.org/
- **PyQt6**: GPL v3 or commercial licensing, https://www.riverbankcomputing.com/software/pyqt/
  IMPORTANT: This project is distributed as GPL-compatible source when using GPL PyQt6;
  distributing closed-source binaries requires appropriate PyQt6 commercial licensing.
- **FFmpeg binary via imageio-ffmpeg**: governed by the specific packaged FFmpeg build
  license (may be LGPL or GPL); review and supply notices/source offers as required.

Before distributing a binary, review licenses for all bundled libraries and model weights.
The example installer copies this notice; it is not a complete legal compliance audit.

### Optional Bethesda voice-export integration (v0.2.1)

- WMAEncodeRS: MIT license, https://github.com/MSIVST/WMAEncodeRS . NOT BUNDLED. Uses Windows Media runtime.
- Nukem9 FaceFXWrapper: https://github.com/Nukem9/FaceFXWrapper . NOT BUNDLED. Its license expressly acknowledges use of Bethesda Creation Kit code and subject matter; do not presume the entire compiled tool is freely redistributable.
- Bethesda `FonixData.cdf`, Creation Kit and `xwmaencode.exe`: Bethesda-controlled assets and tools; NOT BUNDLED. Installed locally by the end user.
- Optional clean-room OpenFaceFX: https://github.com/OpenFaceFX/OpenFaceFX (MIT); its Bethesda LIP writer remains experimental, no in-game verification and no Fallout 4 support as of this review. Not used or bundled.
- `.fuz` packing implementation and test code are original Python source distributed with this project.
