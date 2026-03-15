Get-ChildItem -Path .\ -Filter *.acb | ForEach-Object {
    $acbFile = $_.Name
    $baseName = $acbFile -replace '\.acb$',''
    $awbFile = "$baseName.awb"
    $sourceFile = if (Test-Path ".\$awbFile") { $awbFile } else { $acbFile }
    
    [void]([System.IO.Directory]::CreateDirectory(".\$baseName"))
    
    # Get total subsong count
    $metaAll = vgmstream-cli -m -S 0 $sourceFile 2>&1
    $streamCountMatch = ($metaAll | Select-String "stream count:\s+(\d+)")
    $streamCount = if ($streamCountMatch) { $streamCountMatch.Matches[0].Groups[1].Value -as [int] } else { 1 }
    
    for ($i = 1; $i -le $streamCount; $i++) {
        $meta = vgmstream-cli -m -s $i $sourceFile 2>&1
        
        $sampleRateMatch = ($meta | Select-String "sample rate:\s+(\d+)")
        $loopStartMatch = ($meta | Select-String "loop start:\s+(\d+)")
        $loopEndMatch   = ($meta | Select-String "loop end:\s+(\d+)")
        $sampleRate = if ($sampleRateMatch) { $sampleRateMatch.Matches[0].Groups[1].Value } else { $null }
        $loopStart = if ($loopStartMatch) { $loopStartMatch.Matches[0].Groups[1].Value } else { $null }
        $loopEnd   = if ($loopEndMatch)   { $loopEndMatch.Matches[0].Groups[1].Value   } else { $null }
        $streamName  = ($meta | Select-String "stream name:\s+(.+)").Matches[0].Groups[1].Value.Trim()
        
        # Convert to WAV (raw, no loop rendering)
        $outWav  = ".\$baseName\$streamName.wav"
        $outOpus = ".\$baseName\$streamName.opus"
        vgmstream-cli -s $i -L -o $outWav $sourceFile
        
        # Convert WAV to Opus and embed loop tags
        $ffmpegArgs = @("-i", $outWav, "-c:a", "libopus", "-b:a", "128k")
        if ($sampleRate -and $loopStart -and $loopEnd) {
            $ffmpegArgs += @("-metadata", "SAMPLE_RATE=$sampleRate", "-metadata", "LOOP_START=$loopStart", "-metadata", "LOOP_END=$loopEnd")
        }
        $ffmpegArgs += @("-y", "-loglevel", "warning", $outOpus)
        & ffmpeg @ffmpegArgs
    }
}