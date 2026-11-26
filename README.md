# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/Elyonel28/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/Elyonel28/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

A newspaper front page that sums up the world's news of Wednesday 25 November 2026 in one image: six verified stories from that day alone — the Houthi strike on Riyadh's tallest tower, Iran's claimed downing of two US drones over the Strait of Hormuz, Huawei's conviction in a US criminal trial, Pakistan's first astronaut aboard China's Shenzhou-24, the US Army's detonation of its entire lead-azide stockpile in Iowa, and the first-ever postponement of the Macy's Thanksgiving Day Parade — plus a markets footer. Every story is readable from the image alone, with a small drawn icon per story.

Pure Python 3 standard library: `main.py` draws the 1024×1024 PNG from scratch (its own 5×7 bitmap font, its own PNG encoder), with no network, no randomness and no clock, so two runs write byte-identical files. Sources for every story are listed in [NEWS.md](NEWS.md).

## Run it

```sh
python3 main.py
```

This writes `entry.png` (1024×1024, under 1 MiB) next to `main.py`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=h0sbywyp&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
