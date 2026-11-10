# Shorts formato novo: quadrado central preenchendo a tela vertical, gancho fixo no topo desde o 1º frame,
# legenda grande embaixo, vários trechos concatenados, sem tela preta no final.
import re, json, subprocess, itertools, sys, os
S = '/tmp/claude-0/-home-user-Claude-/d82a132e-9aaa-538d-95eb-b7f679f02500/scratchpad/'
SRC = '/home/user/Claude-/roteiros/video-13-calculo.mp4'
OUTD = '/home/user/Claude-/roteiros/'
js = open(S + 'c13.js').read()
says = [b for a, b in re.findall(r"^scene\('[^']*',(.+?),\s*'(.*?)',\(\)=>", js, re.M)]
durs = json.load(open(S + 'video/durs_c13.json'))
assert len(says) == len(durs) == 23, (len(says), len(durs))
starts = [0] + list(itertools.accumulate(durs))

caps = []
for txt, st, du in zip(says, starts, durs):
    if not txt: continue
    words = txt.replace('—', '').split()
    chunks, cur = [], []
    for w in words:
        if cur and (len(cur) >= 3 or len(' '.join(cur + [w])) > 18 or cur[-1][-1] in '.?!:,'):
            chunks.append(' '.join(cur)); cur = []
        cur.append(w)
    if cur: chunks.append(' '.join(cur))
    speech = max(0.6, du - 0.45); tot = sum(len(c) for c in chunks); t = st
    for c in chunks:
        d = speech * len(c) / tot; caps.append((t, t + d, c.upper())); t += d

def ts(x):
    return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"

SHORTS = [
    ('short-13calc-1-segunda-menor', [(0, 2), (14, 16)], ['13º 2026: POR QUE A 2ª', 'PARCELA VEM MENOR?']),
    ('short-13calc-2-quando-cai', [(4, 6)], ['QUANDO CAI', 'O 13º EM 2026?']),
    ('short-13calc-3-como-calcular', [(6, 7), (8, 10)], ['COMO CALCULAR', 'O SEU 13º']),
]
for name, segs, hook in SHORTS:
    pieces = [(starts[a], starts[b]) for a, b in segs]
    L = sum(b - a for a, b in pieces)
    ass = ['[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 1080', 'PlayResY: 1920', '', '[V4+ Styles]',
           'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
           'Style: Hook,Anton,104,&H00141414,&H00141414,&H004AD5FF,&H004AD5FF,0,0,0,0,100,100,1,0,3,22,0,8,40,40,110,1',
           'Style: Cap,Anton,120,&H00FFFFFF,&H00FFFFFF,&H00141414,&H00000000,0,0,0,0,100,100,1,0,1,8,0,2,50,50,190,1',
           'Style: End,Anton,80,&H004AD5FF,&H004AD5FF,&H00141414,&H00000000,0,0,0,0,100,100,1,0,1,7,0,2,50,50,200,1',
           '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    ass.append(f"Dialogue: 1,{ts(0)},{ts(L)},Hook,,0,0,0,,{hook[0]}\\N{hook[1]}")
    off = 0
    for a0, b0 in pieces:
        for a, b, c in caps:
            if b <= a0 + .05 or a >= b0 - .05: continue
            s2 = max(a, a0) - a0 + off; e2 = min(b, b0) - a0 + off
            if e2 > L - 1.4: e2 = min(e2, L - 1.4)
            if e2 - s2 > .1:
                ass.append(f"Dialogue: 0,{ts(s2)},{ts(e2)},Cap,,0,0,0,,{c}")
        off += b0 - a0
    ass.append(f"Dialogue: 2,{ts(L-1.4)},{ts(L)},End,,0,0,0,,VÍDEO COMPLETO NO CANAL 🥫")
    af = S + f'{name}.ass'; open(af, 'w').write('\n'.join(ass) + '\n')
    inputs = []; fc = ''
    for i, (a, b) in enumerate(pieces):
        inputs += ['-ss', f'{a:.3f}', '-t', f'{b-a:.3f}', '-i', SRC]
        fc += f"[{i}:v]crop=720:720:280:0,scale=1080:1080,setsar=1[v{i}];[{i}:a]afade=t=in:d=0.03,afade=t=out:st={b-a-0.05:.3f}:d=0.05[a{i}];"
    n = len(pieces)
    fc += ''.join(f'[v{i}][a{i}]' for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca];"
    fc += (f"color=c=0x0d1019:s=1080x1920:r=30:d={L:.3f}[bg];[bg][cv]overlay=0:420:shortest=1,"
           f"subtitles='{af}':fontsdir='{S}fonts',format=yuv420p[v]")
    out = OUTD + name + '.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', '[v]', '-map', '[ca]',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', out], check=True)
    print(name, round(L, 1), 's')
