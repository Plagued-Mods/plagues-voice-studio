# Plague's Voice Studio 0.2.3 — About Dialog and Memory Diagnostics

## Fixed / mitigated

- Changed About from a blocking nested Qt event loop (`QDialog.exec`) to a
  persistent, lightweight, non-modal dialog. The branded logo remains visible,
  as do the copyright, credits, upstream source link, and application version.
- Added Windows frozen GUI smoke coverage that actually clicks **About**, closes
  it, and reopens it. The build aborts before producing a portable ZIP/installer
  if this Qt interaction crashes or fails in the frozen binary.
- Render failures containing Windows paging-file error 1455 now include concrete
  recovery instructions in the session log. **No code can manufacture sufficient
  virtual memory:** the Windows pagefile/commit issue must be corrected on the
  computer that loads the model.
- Preserved v0.2 settings/data directory to retain users' voice references and
  export profiles. Existing v0.1 fallback installation is untouched.

## What the error means

A message such as `The paging file is too small for this operation to complete
(os error 1455)` means Windows cannot commit enough virtual memory to load the
selected model. In System Properties > Advanced > Performance Settings >
Advanced > Virtual memory, enable Windows-managed paging (or provide an adequate
custom file), ensure the relevant drive has free space, and reboot. Switching
from Original English to Nano can reduce memory usage. Selecting `-Models turbo`
during packaging does not change the model selected inside the application.

## Validation scope

Python source and unit tests run in this environment. The Windows GUI and real
Chatterbox loading require a Windows build. The new build smoke test exercises
About but **does not prove the model will fit in available system memory**.

Windows build from a fresh extracted folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1 -Models turbo
```

Test the exact EXE generated here:

`dist\PlaguesVoiceStudio023\PlaguesVoiceStudio023.exe`

The GUI smoke report is `build\frozen-ui-smoke-test.json`.
