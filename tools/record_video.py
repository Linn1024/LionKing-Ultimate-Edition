"""Record the installed Windows preview in real time, with its mixed game audio."""
import argparse
import ctypes as C
from ctypes import wintypes as W
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import struct
import time

ROOT = Path(__file__).resolve().parents[1]
PRESETS = {'best': 'the-best', 'genesis': 'full-genesis',
           'snes': 'native', 'mixed': 'snes-visuals-genesis'}
ASSETS = {'--asset-cache': 'scene_cache', '--final-menu-assets': 'menu_assets',
          '--final-native-assets': 'native_final_assets', '--title-bank-assets': 'title_bank_assets',
          '--hud-assets': 'hud_assets', '--sprite-assets': 'sprite_assets',
          '--caption-assets': 'caption_assets', '--checkpoint-assets': 'checkpoint_assets',
          '--revival-assets': 'revival_assets', '--native-hud-assets': 'native_hud_assets'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preset', choices=PRESETS, default='best')
    parser.add_argument('--seconds', type=int, choices=range(3, 3601), metavar='3..3600', default=180)
    start = parser.add_mutually_exclusive_group()
    start.add_argument('--level', type=int, choices=range(14), metavar='0..13')
    start.add_argument('--start-state', type=Path, help='Begin at a local saved scene; no movie is played.')
    parser.add_argument('--width', type=int, default=1280)
    parser.add_argument('--height', type=int, default=720)
    parser.add_argument('--original-view', action='store_true', help='Use the selected console framing.')
    parser.add_argument('--desktop', action='store_true', help='Include the primary desktop and F12 window.')
    parser.add_argument('--fps-counter', action='store_true')
    parser.add_argument('--ffmpeg', help='Path to ffmpeg.exe (otherwise PATH or tools/ffmpeg.exe).')
    args = parser.parse_args()
    if os.name != 'nt':
        parser.error('Recording currently requires Windows.')
    if not (640 <= args.width <= 7680 and 480 <= args.height <= 4320):
        parser.error('Choose a window between 640x480 and 7680x4320.')
    ffmpeg = args.ffmpeg or shutil.which('ffmpeg') or str(ROOT/'tools/ffmpeg.exe')
    if not Path(ffmpeg).is_file():
        parser.error('Install FFmpeg and add ffmpeg.exe to PATH, or use --ffmpeg PATH.')
    launcher = (ROOT/'scripts/RunInstalledPreview.ps1').read_text()
    match = re.search(r"\$package = Join-Path \$projectRoot '([^']+)'", launcher)
    if not match:
        raise RuntimeError('Cannot find the installed package.')
    package = ROOT/match[1]
    info = json.loads((package/'package.json').read_text())
    player = package/'LionKing.exe'
    if digest(player) != info['player_sha256'] or digest(package/'genesis_plus_gx_libretro.dll') != info['backend_sha256']:
        raise RuntimeError('Player files do not match the package manifest.')
    manifest_path = ROOT/'game-data/install.json'
    if not manifest_path.is_file():
        raise RuntimeError('Run Setup.cmd with the two ROMs first.')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    command = [str(player)]
    specs = {'--rom': manifest['roms']['snes'], '--md-rom': manifest['roms']['megadrive']}
    specs.update({flag: manifest[key] for flag, key in ASSETS.items()})
    for flag, spec in specs.items():
        path = (ROOT/'game-data'/spec['file']).resolve()
        if not path.is_relative_to((ROOT/'game-data').resolve()) or not path.is_file() or digest(path) != spec['sha256']:
            raise RuntimeError('Installed data is missing or damaged. Run Setup.cmd again.')
        command += [flag, str(path)]
    folder = ROOT/'build/video-recordings'/dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f')
    folder.mkdir(parents=True)
    shutil.copy2(ROOT/'profiles'/(PRESETS[args.preset]+'.ini'), folder/'resources.ini')
    (folder/'game.ini').write_text(f'opengl = 0\nscale = 3\nwindow_size = {args.width} x {args.height}\n'
                                 'fullscreen = 0\nvsync = 0\naudio = 1\nvolume = 10\n'
                                 'widescreen = '+('off' if args.original_view else 'adaptive')+
                                 '\nwidescreen_enemies = out of view\n')
    command += ['--config', str(folder/'game.ini'), '--resource-profile', str(folder/'resources.ini')]
    env = {k: v for k, v in os.environ.items() if not k.startswith(('TLK_', 'SDL_', 'SNESRECOMP_'))}
    env.update(TLK_SMOOTH_UPDATES='1', TLK_FPS_COUNTER=str(int(args.fps_counter)),
               TLK_FPS_LOG=str(folder/'updates.csv'))
    starting_field = 0
    if args.level is not None:
        print('Preparing the selected level before recording...', flush=True)
        state = folder/'start.state'
        prepare = command + ['--practice-level', str(args.level), '--frames', '1700',
                             '--save-at', '1700', str(state), '--no-record', '--no-pace', '--no-audio']
        with (folder/'prepare.log').open('wb') as log:
            subprocess.run(prepare, cwd=ROOT,
                           env=dict(env, SDL_VIDEODRIVER='dummy', SDL_AUDIODRIVER='dummy'),
                           stdout=log, stderr=subprocess.STDOUT, check=True, timeout=60,
                           creationflags=subprocess.CREATE_NO_WINDOW)
        command += ['--load', str(state)]
        starting_field = 1700
    elif args.start_state:
        state = args.start_state.resolve()
        raw = state.read_bytes()
        offset = 96 if raw[:8] == b'TLKFSV01' else 0
        if raw[offset:offset+8] != b'TLKSTAT1':
            raise RuntimeError('The supplied scene is not a supported save state.')
        starting_field = struct.unpack_from('<I', raw, offset+12)[0]
        command += ['--load', str(state)]
    command += ['--wav', str(folder/'game-audio.wav'), '--wav-seconds', str(args.seconds+15),
                '--record', str(folder/'input.rec')]
    user = C.WinDLL('user32', use_last_error=True)
    user.SetProcessDPIAware()
    enum_type = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
    user.EnumWindows.argtypes = [enum_type, W.LPARAM]
    user.GetWindowThreadProcessId.argtypes = [W.HWND, C.POINTER(W.DWORD)]
    user.IsWindowVisible.argtypes = [W.HWND]
    user.GetClientRect.argtypes = [W.HWND, C.POINTER(W.RECT)]
    user.GetWindowRect.argtypes = [W.HWND, C.POINTER(W.RECT)]
    user.ClientToScreen.argtypes = [W.HWND, C.POINTER(W.POINT)]
    user.SetWindowPos.argtypes = [W.HWND, W.HWND, C.c_int, C.c_int, C.c_int, C.c_int, W.UINT]
    user.SetForegroundWindow.argtypes = [W.HWND]
    user.PostMessageW.argtypes = [W.HWND, W.UINT, W.WPARAM, W.LPARAM]

    def find_window(pid):
        found = []
        @enum_type
        def each(hwnd, unused):
            actual = W.DWORD()
            user.GetWindowThreadProcessId(hwnd, C.byref(actual))
            rect = W.RECT()
            if actual.value == pid and user.IsWindowVisible(hwnd) and user.GetClientRect(hwnd, C.byref(rect)):
                if rect.right >= 256 and rect.bottom >= 128:
                    found.append((rect.right*rect.bottom, hwnd))
            return True
        user.EnumWindows(each, 0)
        return max(found)[1] if found else None

    hidden = subprocess.CREATE_NO_WINDOW
    game = video = None
    hwnd = None
    capture_start = None
    start = time.time()
    print('Output: '+str(folder/'video.mp4'), flush=True)
    print('Records '+('the PRIMARY DESKTOP, including F12. Close unrelated windows.' if args.desktop else
                       'the game rectangle. Keep its window visible and do not move or resize it.'), flush=True)
    print('Close the game window to finish early. Recording stops after '+str(args.seconds)+' seconds.', flush=True)
    (folder/'command.json').write_text(json.dumps(command, indent=2))
    with (folder/'game.log').open('wb') as game_log, (folder/'capture.log').open('wb') as capture_log:
        try:
            game = subprocess.Popen(command, cwd=ROOT, env=env, stdout=game_log, stderr=subprocess.STDOUT, creationflags=hidden)
            deadline = time.monotonic()+20
            while game.poll() is None and time.monotonic() < deadline:
                hwnd = find_window(game.pid)
                if hwnd:
                    break
                time.sleep(.05)
            if not hwnd:
                raise RuntimeError('No game window. See '+str(folder/'game.log'))
            user.SetForegroundWindow(hwnd)
            # Rectangle capture must not silently film a window covering the game.
            # Desktop mode leaves stacking alone so F12 can appear above the game.
            user.SetWindowPos(hwnd, None if args.desktop else W.HWND(-1), 20, 20, 0, 0,
                              0x15 if args.desktop else 0x11)
            time.sleep(.25)
            rect = W.RECT(); origin = W.POINT()
            user.GetClientRect(hwnd, C.byref(rect)); user.ClientToScreen(hwnd, C.byref(origin))
            if args.desktop:
                width, height, left, top = user.GetSystemMetrics(0), user.GetSystemMetrics(1), 0, 0
            else:
                width = min(rect.right, user.GetSystemMetrics(0)-origin.x)
                height = min(rect.bottom, user.GetSystemMetrics(1)-origin.y)
                left, top = origin.x, origin.y
            if min(width, height) <= 0 or min(left, top) < 0:
                raise RuntimeError('The game is outside the primary screen. Move it into view.')
            grab = f'ddagrab=framerate=60:draw_mouse={int(args.desktop)}:video_size={width}x{height}:offset_x={left}:offset_y={top}'
            vc = [ffmpeg, '-hide_banner', '-y', '-f', 'lavfi', '-i', grab, '-an',
                  '-vf', 'hwdownload,format=bgra,pad=ceil(iw/2)*2:ceil(ih/2)*2',
                  '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-threads', '2',
                  '-pix_fmt', 'yuv420p', str(folder/'screen.mp4')]
            (folder/'capture-command.json').write_text(json.dumps(vc, indent=2))
            capture_start = time.time()
            video = subprocess.Popen(vc, stdin=subprocess.PIPE, stdout=capture_log, stderr=subprocess.STDOUT, creationflags=hidden)
            while game.poll() is None and time.time()-capture_start < args.seconds:
                if video.poll() is not None:
                    raise RuntimeError('FFmpeg capture failed. See '+str(folder/'capture.log'))
                time.sleep(.1)
        finally:
            if video and video.poll() is None:
                video.communicate(b'q\n', timeout=30)
            if game and game.poll() is None:
                if hwnd:
                    user.PostMessageW(hwnd, 0x10, 0, 0)
                try:
                    game.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    game.terminate(); game.wait(timeout=5)
    if not video or video.returncode or not (folder/'screen.mp4').is_file():
        raise RuntimeError('Recording did not finish. Existing files are retained in '+str(folder))
    audio = folder/'game-audio.wav'
    if not audio.is_file() or audio.stat().st_size < 44:
        raise RuntimeError('Game audio is missing; silent capture retained in '+str(folder/'screen.mp4'))
    offset = max(0, capture_start-start)
    mux = [ffmpeg, '-hide_banner', '-y', '-i', str(folder/'screen.mp4'), '-ss', str(offset),
           '-i', str(audio), '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
           '-c:a', 'aac', '-b:a', '192k', '-af', 'apad', '-shortest', '-movflags', '+faststart', str(folder/'video.mp4')]
    with (folder/'mux.log').open('wb') as log:
        subprocess.run(mux, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120, creationflags=hidden)
    if (folder/'video.mp4').stat().st_size < 1000:
        raise RuntimeError('MP4 is empty; intermediate files retained.')
    (folder/'session.json').write_text(json.dumps(dict(player_sha256=info['player_sha256'], preset=args.preset,
        desktop=args.desktop, audio='mixed game output; start-time aligned; no microphone/system audio',
        audio_trim_seconds=offset, game_exit_code=game.returncode, video=str(folder/'video.mp4'),
        starting_field=starting_field, window=[args.width,args.height],
        enemy_spawning='out of view', movie_playback=False), indent=2))
    recording = folder/'input.rec'
    if starting_field and recording.is_file():
        recording.write_bytes(bytes(starting_field*2)+recording.read_bytes())
    # Keep one finished compressed copy, not two videos and an uncompressed WAV.
    audio.unlink(); (folder/'screen.mp4').unlink()
    (folder.parent/'latest.txt').write_text(str(folder/'video.mp4')+'\n')
    print('SAVED VIDEO: '+str(folder/'video.mp4'), flush=True)
    return game.returncode


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (Exception, KeyboardInterrupt) as error:
        print('Recording stopped: '+str(error), flush=True)
        raise SystemExit(1)
