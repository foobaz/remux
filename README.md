# remux

Losslessly convert video files to the best container format for the streams they contain.

### Synopsis

`remux.py path/to/video.ext [path/to/another/video.ext]`

### Description

Given a video, Remux will try to find a simpler format for it, such as:
- .avi to .mp4
- .mp4 to .m4v (raw stream without metadata)
- .mkv to .mp4
- .mkv to .webm
- .mov to .mp4

It will only perform the conversion if it is lossless. For example, it will not convert to .m4v if there is metadata that would be lost. It will not re-encode video or audio - it copies existing streams to the new container format unchanged.

If Remux determines the video is already in the optimal format, it will still perform the conversion. This is bad for performance but good for thorough data normalization.

Files without a video stream will be skipped, including images, audio files, and subtitle files. It is safe to run Remux on a directory with a mix of video and non-video files.
