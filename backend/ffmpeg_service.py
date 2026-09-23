import subprocess
from pathlib import Path

def concat_clips(clips, output):
    output = Path(output)
    manifest = output.with_suffix(".txt")
    manifest.write_text("\n".join(f"file '{Path(p).resolve()}'" for p in clips), encoding="utf-8")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(manifest), "-c:v", "libx264", "-c:a", "aac",
        "-movflags", "+faststart", str(output)
    ]
    subprocess.run(cmd, check=True)
    return str(output)
