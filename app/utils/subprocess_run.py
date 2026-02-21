import subprocess
from typing import Optional
from fastapi import HTTPException


def run_cmd(cmd: list[str], stdin: Optional[bytes] = None) -> bytes:
    try:
        p = subprocess.run(
            cmd,
            input=stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return p.stdout
    except subprocess.CalledProcessError as e:
        err = (e.stderr or b"").decode(errors="replace")
        raise HTTPException(status_code=500, detail=err or str(e))