# PolarHash

A free offline Windows desktop utility from **PolarLabs-OSS**.

![PolarHash icon](PolarHash.png)

## Features

# PolarHash v1.0.0

Utility desktop offline della suite PolarLabs-OSS.

## Install and run from source

Requires Python 3 with Tkinter. Install dependencies via `pip install -r requirements.txt`, then run:

```powershell
python polarhash.py
```

## Windows release

Download the Windows x64 release ZIP, extract the **entire archive** and run `PolarHash-PolarWhite-v5.exe`. Do not move the EXE away from the `_internal` directory. The x64 build was tested on Windows 11 ARM64 under emulation.

## Linux

The Linux ARM64 binary was compiled in Ubuntu WSL but its interactive desktop UI was not fully tested. Other Linux architectures require a native rebuild.

## Security and privacy

File processing happens locally. The executable is not digitally signed, so your device or organization's application-control policy may restrict launching it. Do not disable security protections to run it.

## License

MIT License — see [LICENSE](LICENSE).

PolarLabs / Space Services SRLS · https://www.polarlabs.it/
