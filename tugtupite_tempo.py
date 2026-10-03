#!/usr/bin/env python3
"""Tugtupite Tempo — neon 4-lane rhythm tap for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/TUGTUPITE_TEMPO_ElbowOS.mp4")
LANES, LANE_W, GAP = 4, 180, 28
TABLE = LANES * LANE_W + (LANES - 1) * GAP
LEFT = (W - TABLE) // 2
HIT_Y, NOTE_R = 1540, 46
CORAL, GOLD = (255, 92, 78), (255, 196, 64)
CYAN, MAG = (64, 240, 220), (255, 64, 180)
INK, WHITE = (12, 4, 18), (255, 244, 236)
COLORS = [CORAL, GOLD, CYAN, MAG]


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            self.screen = pygame.Surface((W, H))
        pygame.display.set_caption("Tugtupite Tempo")
        self.font = pygame.font.SysFont("dejavusans", 62, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 36, bold=True)
        self.tiny = pygame.font.SysFont("dejavusans", 28, bold=True)
        self.reset()

    def reset(self):
        self.t = 0.0
        self.score = 0
        self.combo = 0
        self.notes = []
        self.sparks = []
        self.flashes = [0.0] * 4
        self.judge, self.judge_t = "", 0.0
        self.spawn_i = 0
        self.chart = self.build_chart()
        self.held = [False] * 4
        random.seed(11)
        for lane, y in ((0, 900), (2, 620), (1, 1180), (3, 400)):
            self.notes.append(self.make_note(lane, y))

    def build_chart(self):
        beat = 60.0 / 136
        pat = [[0], [1], [2], [3], [0, 2], [1, 3], [3], [0], [1, 2], [2], [0, 3], [1]]
        chart, t, i = [], 0.35, 0
        while t < 14.2:
            for ln in pat[i % len(pat)]:
                chart.append((t, ln))
            t += beat * (0.5 if i % 7 == 6 else 1)
            i += 1
        return chart

    def make_note(self, lane, y):
        return {"lane": lane, "y": float(y), "vy": 980, "alive": True, "col": COLORS[lane]}

    def lx(self, i):
        return LEFT + i * (LANE_W + GAP)

    def burst(self, lane, col):
        x = self.lx(lane) + LANE_W // 2
        for i in range(16):
            ang = i / 16 * math.tau + random.random()
            sp = random.uniform(160, 560)
            self.sparks.append({
                "x": x, "y": HIT_Y, "vx": math.cos(ang) * sp,
                "vy": math.sin(ang) * sp - 60, "life": random.uniform(0.28, 0.6),
                "col": col, "r": random.randint(4, 11),
            })

    def auto_keys(self):
        keys = [False] * 4
        for n in self.notes:
            if n["alive"] and HIT_Y - 64 <= n["y"] <= HIT_Y + 28:
                keys[n["lane"]] = True
        return keys

    def step(self, dt, keys):
        self.t += dt
        self.held = keys
        while self.spawn_i < len(self.chart) and self.chart[self.spawn_i][0] <= self.t:
            _, ln = self.chart[self.spawn_i]
            self.notes.append(self.make_note(ln, 260))
            self.spawn_i += 1
        for i in range(4):
            self.flashes[i] = max(0.0, self.flashes[i] - dt * 3.4)
        self.judge_t = max(0.0, self.judge_t - dt)
        for n in self.notes:
            if not n["alive"]:
                continue
            n["y"] += n["vy"] * dt
            if keys[n["lane"]] and abs(n["y"] - HIT_Y) < 80:
                n["alive"] = False
                dist = abs(n["y"] - HIT_Y)
                add, word = (160, "PERFECT") if dist < 26 else (100, "GREAT") if dist < 52 else (45, "OK")
                self.combo += 1
                self.score += add + self.combo * 6
                self.judge, self.judge_t = word, 0.42
                self.flashes[n["lane"]] = 1.0
                self.burst(n["lane"], n["col"])
            elif n["y"] > HIT_Y + 130:
                n["alive"] = False
                self.combo = 0
                self.judge, self.judge_t = "MISS", 0.35
        for s in self.sparks:
            s["x"] += s["vx"] * dt
            s["y"] += s["vy"] * dt
            s["life"] -= dt
        self.sparks = [s for s in self.sparks if s["life"] > 0]
        self.notes = [n for n in self.notes if n["alive"]]

    def draw(self, surf):
        surf.fill(INK)
        for y in range(0, H, 10):
            k = y / H
            c = (
                max(0, int(22 + 36 * math.sin(k * 2.4 + self.t * 0.6))),
                6 + int(16 * k),
                32 + int(48 * (1 - k)),
            )
            pygame.draw.rect(surf, c, (0, y, W, 10))
        for i in range(22):
            h = 36 + int(86 * abs(math.sin(self.t * 7.2 + i * 0.55)))
            pygame.draw.rect(surf, (255, 70 + i * 4, 130), (90 + i * 42, 214 - h, 24, h), border_radius=7)
        for i in range(4):
            x, glow, col = self.lx(i), self.flashes[i], COLORS[i]
            pygame.draw.rect(surf, (48 + int(90 * glow), 10, 32), (x, 250, LANE_W, 1400), border_radius=30)
            pygame.draw.rect(surf, col, (x, 250, LANE_W, 1400), 5, border_radius=30)
            off = int((self.t * 320) % 90)
            for yy in range(-off, 1400, 90):
                pygame.draw.line(surf, (110, 40, 70), (x + 24, 250 + yy), (x + LANE_W - 24, 250 + yy), 2)
            pad = pygame.Rect(x + 18, HIT_Y - 30, LANE_W - 36, 74)
            if self.held[i]:
                pygame.draw.rect(surf, col, pad, border_radius=18)
            else:
                pygame.draw.rect(surf, col, pad, 6, border_radius=18)
        for n in self.notes:
            x = self.lx(n["lane"]) + LANE_W // 2
            y = int(n["y"])
            pygame.draw.circle(surf, n["col"], (x, y), NOTE_R + 10)
            pts = [(x, y - NOTE_R), (x + NOTE_R, y), (x, y + NOTE_R), (x - NOTE_R, y)]
            pygame.draw.polygon(surf, n["col"], pts)
            pygame.draw.polygon(surf, WHITE, pts, 4)
            pygame.draw.circle(surf, WHITE, (x, y), 11)
        for s in self.sparks:
            pygame.draw.circle(surf, s["col"], (int(s["x"]), int(s["y"])), max(2, int(s["r"] * s["life"] * 2)))
        title = self.font.render("TUGTUPITE TEMPO", True, GOLD)
        surf.blit(title, title.get_rect(center=(W // 2, 78)))
        sc = self.small.render(f"SCORE  {self.score}", True, WHITE)
        surf.blit(sc, sc.get_rect(center=(W // 2, 142)))
        cb = self.tiny.render(f"COMBO  x{self.combo}", True, CYAN)
        surf.blit(cb, cb.get_rect(center=(W // 2, 184)))
        if self.judge_t > 0:
            j = self.font.render(self.judge, True, GOLD if self.judge != "MISS" else CORAL)
            surf.blit(j, j.get_rect(center=(W // 2, HIT_Y - 150)))
        tag = self.small.render("x.com/ElbowOS", True, (255, 214, 150))
        surf.blit(tag, tag.get_rect(center=(W // 2, H - 64)))

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        dt = 1.0 / FPS
        try:
            for _ in range(FPS * SECS):
                self.step(dt, self.auto_keys())
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
            proc.stdin.close()
        except BrokenPipeError:
            pass
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("wrote", OUT)
        pygame.quit()

    def play_interactive(self):
        clock = pygame.time.Clock()
        keymap = {pygame.K_a: 0, pygame.K_s: 1, pygame.K_d: 2, pygame.K_f: 3}
        held = [False] * 4
        running = True
        while running:
            dt = min(clock.tick(FPS) / 1000.0, 0.05)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
                elif ev.type == pygame.KEYDOWN and ev.key in keymap:
                    held[keymap[ev.key]] = True
                elif ev.type == pygame.KEYUP and ev.key in keymap:
                    held[keymap[ev.key]] = False
            self.step(dt, held)
            self.draw(self.screen)
            pygame.display.flip()
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
