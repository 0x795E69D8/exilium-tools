# Audio Extractor

## Features

- 📦 Extracts audio from all .acb/.awb files in the directory into .wav and .opus files
- ⚙️ Embeds loop starting and ending sample as well as the sample rate into .opus files when available (BGM, Ambient SFX etc.)

## Setup

Download [vgmstream-cli](https://github.com/vgmstream/vgmstream) and [FFmpeg](https://www.ffmpeg.org/) and add them to your `PATH`.

## Usage

```
.\audio_extractor.ps1
```

Will extract all .acb/.awb files in the directory this is run in.
