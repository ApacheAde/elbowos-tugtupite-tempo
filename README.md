# Tugtupite Tempo

Full-colour Python 3 neon 4-lane rhythm tap for [ElbowOS](https://x.com/ElbowOS).

Diamonds fall in coral, gold, cyan, and magenta lanes. Tap on the glowing pad. Perfect hits build a combo and burst sparks. Miss and the streak breaks.

This is an original arcade toy. It is not a commercial rhythm game, not a ROM, and not an emulator.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 tugtupite_tempo.py --play
```

Keys: `A` `S` `D` `F` tap the four lanes. `R` restarts. `Esc` quits.

## Record a 9:16 reel

```bash
python3 tugtupite_tempo.py --record
```

Headless autoplay uses `SDL_VIDEODRIVER=dummy`, draws a 1080x1920 surface, and pipes 15 seconds at 30 fps to ffmpeg (libx264, yuv420p, CRF 20, +faststart). Override the output path with `ELBOWOS_MP4`.

## Links

* Featured account: https://x.com/ElbowOS
* Drive reel: https://drive.google.com/file/d/19oXRpSxloyQkHun_QgoHuLGwHbxh-NXT/view
* Posted copy: https://drive.google.com/file/d/10Ry4MpJs8mFA0bpSl2gyrEMj49w2mkqQ/view
