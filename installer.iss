#define AppName "Plague's Voice Studio 0.2.4"
#define AppVersion "0.2.4"
#define AppPublisher "Kaotick Jay"
#define AppExeName "PlaguesVoiceStudio024.exe"

[Setup]
AppId={{C3E84B0B-B962-470D-9F4D-9CC056BB45D8}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName}
VersionInfoProductName={#AppName}
VersionInfoCopyright=Copyright (c) 2026 Kaotick Jay
DefaultDirName={localappdata}\Programs\Plague's Voice Studio 0.2.4
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
PrivilegesRequired=lowest
OutputDir=dist-installer
OutputBaseFilename=PlaguesVoiceStudio024-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
; Full offline builds exceed the single-executable practical size limit.
; Keep all generated Setup-*.bin slices beside the setup EXE.
DiskSpanning=yes
DiskSliceSize=2100000000
WizardStyle=modern
SetupIconFile=assets\plagues-voice-studio.ico
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
LicenseFile=LICENSE

[Files]
Source: "dist\PlaguesVoiceStudio024\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Plague's Voice Studio 0.2.4"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\Plague's Voice Studio 0.2.4"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch Plague's Voice Studio"; Flags: nowait postinstall skipifsilent
