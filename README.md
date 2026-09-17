# DSA Combo Shooting Game — Web Build & Deployment Guide

A Python/Pygame shooting game converted to run in any modern browser via
**Pygbag** (WebAssembly) and deployed on **Vercel**.

---

## 🎮 How to Play

| Key | Action |
|-----|--------|
| ← Arrow | Move player left |
| → Arrow | Move player right |
| Space | Shoot |

**Combo System:** Shoot enemies of the same type 3 times in a row → they are
removed from the stack and added to your Combo Stack (+1 score).  
**Game Over:** An enemy reaches you, OR your vertical stack hits 10 items.

---

## 📁 Project Structure

```
DSA ASSIGNMENT/
├── main.py              # Pygame game (Pygbag-compatible, asyncio loop)
├── background.png
├── player.png
├── bullet.png
├── enemy1.png  (Scizor)
├── enemy2.png  (Magneton)
├── enemy3.png  (Voltorb)
├── enemy4.png  (Gloom)
├── gamestart_bg.png
├── gameover_bg.png
├── 22.ico
├── requirements.txt
├── vercel.json
└── build/
    └── web/             # ← generated browser build (git-ignored)
        ├── index.html
        └── ...
```

---

## 🏗️ Build the Web Version

### 1. Install dependencies

```bash
pip install pygame pygbag
```

### 2. Build with Pygbag

Run this command from the project root (the folder containing `main.py`):

```bash
pygbag --build main.py
```

> The web-ready files are generated into **`build/web/`**.  
> `build/web/index.html` is the entry point.

### 3. Test locally (optional)

```bash
pygbag main.py
```

Then open **http://localhost:8000** in your browser.  
(Do NOT open `index.html` directly as a `file://` URL — it requires a server.)

---

## 🚀 Deploy to Vercel

### Option A — Vercel CLI (recommended)

```bash
npm i -g vercel
vercel --prod
```

Vercel reads `vercel.json` and serves `build/web/` as a static site.

### Option B — Vercel Dashboard (drag & drop)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import this GitHub repository **OR** drag-and-drop the `build/web/` folder
3. Set **Output Directory** to `build/web`
4. Click **Deploy**

---

## ⚙️ Vercel Configuration (`vercel.json`)

```json
{
  "outputDirectory": "build/web",
  "buildCommand": "",
  "routes": [
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
```

---

## ✅ What Was Changed (Original → Web)

| Original | Changed To | Why |
|---|---|---|
| `tkinter` + `Pillow` | `pygame` | Pygbag only supports Pygame (WebAssembly) |
| `root.mainloop()` | `asyncio` event loop | Browser requires async/yield |
| `tk.Toplevel` popup | In-canvas game-over screen | No native windowing in browser |
| `.wm_iconbitmap("22.ico")` | Graceful fallback | `.ico` unsupported in browser |
| `root.after(50, ...)` | Frame-rate timer in async loop | Equivalent 50 ms physics step |
| Blocking spawn timer | `pygame.time.get_ticks()` delta | Non-blocking equivalent |

All gameplay, assets, enemies, shooting, combo system, scoring, and visuals
are **preserved identically**.

---

## ❗ Known Limitations / Notes

- **First load may take 10–20 seconds** in the browser (downloading WASM runtime).
- The `.ico` icon is skipped in the browser build (no effect on gameplay).
- Audio is not present in the original game, so nothing changes there.
- The Vercel free tier is sufficient for this static build.
