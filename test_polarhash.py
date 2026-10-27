from pathlib import Path
import tempfile
import hashlib
from polarhash import checksum,verify_manifest
with tempfile.TemporaryDirectory() as td:
 p=Path(td)
 file=p/"hello.bin";file.write_bytes(b"abc")
 expected=hashlib.sha256(b"abc").hexdigest()
 assert checksum(file,"SHA256")==expected
 assert checksum(file,"SHA512")==hashlib.sha512(b"abc").hexdigest()
 manifest=p/"SHA256SUMS"
 manifest.write_text(expected+"  hello.bin\n",encoding="utf-8")
 assert verify_manifest(manifest)==[("hello.bin","OK")]
 file.write_bytes(b"xyz")
 assert verify_manifest(manifest)==[("hello.bin","DIFFERENTE")]
 file.unlink()
 assert verify_manifest(manifest)==[("hello.bin","MANCANTE")]
 print("PASS: SHA256 SHA512 manifest changes missing files")
