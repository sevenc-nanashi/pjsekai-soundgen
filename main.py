import audioop
import gzip
import io
import time
import json
from urllib.parse import quote

import pydub
import requests

from type import LevelData, LevelList

SOUND_MAP = {
    3: "perfect",
    4: "flick",
    5: "sperfect",
    6: "tick",
    7: "sperfect",
    8: "flick",
    10: "critical_tap",
    11: "critical_flick",
    12: "sperfect",
    13: "critical_tick",
    14: "sperfect",
    15: "critical_flick",
}


def overlay_without_sync(seg1, seg2, position):
    output = io.BytesIO()
    sample_width = seg1.sample_width
    spawn = seg1._spawn

    output.write(seg1[:position]._data)

    # drop down to the raw data
    seg1 = seg1[position:]._data
    seg2 = seg2._data
    pos = 0
    seg2_len = len(seg2)
    output.write(audioop.add(seg1[pos : pos + seg2_len], seg2, sample_width))
    pos += seg2_len
    output.write(seg1[pos:])

    return spawn(data=output)


def overlay_without_sync_loop(seg1, seg2, start, end):
    output = io.BytesIO()
    sample_width = seg1.sample_width
    spawn = seg1._spawn

    output.write(seg1[:start]._data)
    seg2_len = len(seg2)

    # drop down to the raw data
    # bseg1 = seg1[start:]._data
    # bseg2 = seg2._data
    pos = 0
    while ((end - start) - pos) >= sample_width:
        current_len = min(seg2_len, end - start)
        if current_len % sample_width > 0:
            current_len -= current_len % sample_width
        current_start = start + pos
        bseg1 = seg1[current_start : current_start + current_len]._data
        bseg2 = seg2[:current_len]._data
        seg_max = max(len(bseg1), len(bseg2))
        bseg1 = bseg1.ljust(seg_max, b"\x00")
        bseg2 = bseg2.ljust(seg_max, b"\x00")
        output.write(audioop.add(bseg1, bseg2, sample_width))
        pos += current_len
    output.write(seg1[end:]._data)

    return spawn(data=output)


def sync_segment(seg1, seg2):
    return seg2.set_channels(seg1.channels).set_frame_rate(seg1.frame_rate).set_sample_width(seg1.sample_width)


def color_escape(color: int):
    r, g, b = color // 65536, (color // 256) % 256, color % 256
    return f"\033[38;2;{r};{g};{b}m"


print(
    f"""
{color_escape(0x00bbd0)}== pjsekai-soundgen -----------------------------------------------------------\033[m
    {color_escape(0x00afc7)}pjsekai-soundgen / プロセカ風譜面音声生成ツール\033[m
    Version: {color_escape(0x0f6ea3)}0.1.0\033[m
    Developed by {color_escape(0x48b0d5)}名無し｡(@sevenc-nanashi)\033[m
    https://github.com/sevenc-nanashi/pjsekai-soundgen
{color_escape(0xff5a91)}-------------------------------------------------------------------------------\033[m
"""
)

total_time = time.time()
session = requests.Session()
name = input("曲名を入力してください: ")
volume = 0.8
keywords = quote(name.encode("utf-8"))
levels: LevelList = session.get(f"https://servers-legacy.purplepalette.net/levels/list?keywords={keywords}").json()

if not levels["items"]:
    exit("曲が見つかりませんでした。")

level_names = [level["title"] for level in levels["items"]]
print("曲を選択して下さい: \n")
for i, level_name in enumerate(level_names):
    print(f"{i + 1}) {level_name}")
print("")
while True:
    index = input("> ")
    try:
        index = int(index)
        level = levels["items"][index - 1]
        break
    except (ValueError, IndexError):
        pass
print(f"{level['title']} / {level['author']} #{level['name']} を選択しました。")

bgm_data = session.get("https://servers.purplepalette.net" + level["bgm"]["url"]).content
bgm = pydub.AudioSegment.from_file(io.BytesIO(bgm_data))
SEG_MAP = {
    name: sync_segment(bgm, pydub.AudioSegment.from_mp3(f"./sounds/{name}.mp3")).apply_gain(volume)
    for name in SOUND_MAP.values()
}

CONNECT_SEG = {
    9: sync_segment(bgm, pydub.AudioSegment.from_mp3("./sounds/connect.mp3")).apply_gain(volume),
    16: sync_segment(bgm, pydub.AudioSegment.from_mp3("./sounds/connect_critical.mp3")).apply_gain(volume),
}

chart_data_gzip = session.get("https://servers.purplepalette.net" + level["data"]["url"]).content
chart_data: LevelData = json.loads(gzip.decompress(chart_data_gzip).decode("utf-8"))
print("音声を合成中...")
single_sounds = set()
hold_sounds = {9: [], 16: []}
for i, entity in enumerate(chart_data["entities"], 1):
    if entity["archetype"] < 3:
        continue
    if entity["archetype"] in [9, 16]:
        hold_sounds[entity["archetype"]].append((entity["data"]["values"][0], entity["data"]["values"][3]))
        continue
    if SOUND_MAP.get(entity["archetype"]) is None:
        continue
    single_sounds.add((SOUND_MAP[entity["archetype"]], round(entity["data"]["values"][0] * 1000)))

start_time = time.time()
eta = "??:??"
print("単ノーツの音声を生成中:")
for i, (sound, position) in enumerate(single_sounds, 1):
    if i % 20 == 19:
        current_time = time.time() - start_time
        eta_int = current_time / (i / len(single_sounds)) - current_time
        eta = f"{int(eta_int / 60):02d}:{int(eta_int % 60):02d}"
    print(f"\r  {i}/{len(single_sounds)}   残り時間: {eta}  ", end="")
    bgm = overlay_without_sync(bgm, SEG_MAP[sound], position)

print("\n長押しノーツの音声を生成中:")
for ari, (archetype, ranges) in enumerate(hold_sounds.items(), 1):
    print(f"  {ari}/2")
    count = 0
    time_data = []
    range_data = []
    for start, end in ranges:
        time_data.append((1, round(start * 1000)))
        time_data.append((-1, round(end * 1000)))
    for diff, ntime in time_data:
        count += diff
        if count == 1 and diff == 1:
            range_data.append([ntime, None])
        elif count == 0 and diff == -1:
            range_data[-1][1] = ntime

    eta = "??:??"
    start_time = time.time()
    for i, (start, end) in enumerate(range_data, 1):
        if i % 20 == 19:
            current_time = time.time() - start_time
            eta_int = current_time / (i / len(range_data)) - current_time
            eta = f"{int(eta_int / 60):02d}:{int(eta_int % 60):02d}"
        print(f"\r    {i}/{len(range_data)}   残り時間: {eta}  ", end="")
        bgm = overlay_without_sync_loop(bgm, CONNECT_SEG[archetype], start, end)
    print("")

print("音声を出力中...")
bgm.export(f"./dist/{level['name']}.mp3", format="mp3")
print(f"完了しました。音声は dist/{level['name']}.mp3 に出力されました。")
total_time = time.time() - total_time
print(f"合計時間: {int(total_time / 60)}:{int(total_time % 60):02d}")
