#!/bin/bash
# HL2 bench suite: every planned configuration in one unattended session.
#
# Each step of a steps file launches the game through Steam (via
# game-wrap.sh in the game's launch options), plays the reference demo, lets
# the engine quit, and collects metrics. Step kinds:
#   timedemo  timed playback, identical frames every run: SourceBench.csv
#             rows (fps, framerate variability, frames, resolution, vsync,
#             MSAA, aniso, dxlevel, command line, driver name, vendor/device
#             id, quality settings, step id as comment), the console log
#             with the result lines, GPU samples (nvidia-smi, 250 ms), CPU
#             load and the game's CPU/RSS (1 s), MangoHud frame times if it
#             is installed, and the stereo module's log;
#   frame     benchframe: one fixed demo frame saved as an image, for
#             comparing renderers, drivers and wiz3D picture for picture;
#   watch     real-time playback for Daniel's eyes on the television;
#   play      Daniel plays, starting on the map in the frame column; nothing
#             is scripted, and the step ends when he quits the game;
#   view      "does it render at all": load d1_town_01 and save one picture
#             of the spawn view (4526 -2747 -3760, yaw 90, read from the
#             map's entity lump), independent of the demo, so it also
#             compares against wiz3D on the steam_legacy branch. Console
#             "wait" cannot hold commands until the player is in, so the
#             camera is not moved; the frame column is informational.
# An optional 8th column names the output to go fullscreen on (e.g.
# HDMI-A-2); "# display: NAME" sets the session default. The name is turned
# into HL2's -displayindex from the display server's monitor list at launch.
# 3D steps set the stereo module's layout (svrtv.ini next to it), which makes
# the module force VR mode at start; demo steps also send vr_activate.
#
# Usage: hl2-suite.sh STEPS_FILE [--force] [--only id1,id2] [--reboot-after]
# Results: /K3D/temp/hl2-bench/suite-<time>-<name>/<step>/ and summary.tsv
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
LIB=/mnt/games/SteamLibrary/steamapps
# Steam's per-user settings (launch options); the most recently written one.
LOCALCONFIG=${STEAM_LOCALCONFIG:-$(ls -t "$HOME"/.steam/*/userdata/*/config/localconfig.vdf "$HOME"/.local/share/Steam/userdata/*/config/localconfig.vdf 2>/dev/null | head -1)}
ROOT=/K3D/temp/hl2-bench
ENVFILE=$ROOT/current.env
DEMO=ref_ravenholm
RES_W=1920 RES_H=1080

STEPS=${1:?usage: hl2-suite.sh STEPS_FILE [--force] [--only ids]}
shift
FORCE=0 ONLY="" REBOOT=0
while [ $# -gt 0 ]; do
	case "$1" in
		--force) FORCE=1 ;;
		--only) ONLY=",$2,"; shift ;;
		--reboot-after) REBOOT=1 ;;
		*) echo "unknown option $1" >&2; exit 2 ;;
	esac
	shift
done

# --- per-app facts ---------------------------------------------------------
app_game() { case $1 in 220) echo "$LIB/common/Half-Life 2" ;; 2477290) echo "$LIB/common/Half-Life 2 RTX" ;; esac; }
app_write() { case $1 in 220) echo "$(app_game 220)/hl2" ;; 2477290) echo "$(app_game 2477290)/hl2rtx" ;; esac; }
# Native HL2 is hl2_linux; under Proton (wiz3D sessions, HL2 RTX) it is hl2.exe.
# Prints the PID and succeeds only when the game is running. (A pipe into
# head reports success even when nothing matched, which let session 0's
# first run launch every step within seconds.)
app_pid() {
	local p=""
	case $1 in
		220) p=$(pgrep -x hl2_linux | head -1); [ -n "$p" ] || p=$(pgrep -f 'hl2\.exe' | head -1) ;;
		2477290) p=$(pgrep -f 'hl2\.exe' | head -1) ;;
	esac
	[ -n "$p" ] && echo "$p"
}
# Close a game completely before anything else starts: TERM, then KILL,
# then the Proton prefix's Wine processes, then wait for Steam's launch
# reaper for that app to exit, so Steam no longer counts the game running.
close_game() { # app
	local app=$1 i p
	for p in $(app_pid "$app"); do kill -TERM "$p" 2>/dev/null; done
	i=0; while [ -n "$(app_pid "$app")" ] && [ $i -lt 20 ]; do sleep 1; i=$((i + 1)); done
	for p in $(app_pid "$app"); do kill -KILL "$p" 2>/dev/null; done
	pkill -TERM -f "compatdata/$app/pfx" 2>/dev/null; sleep 2
	pkill -KILL -f "compatdata/$app/pfx" 2>/dev/null
	i=0; while pgrep -f "SteamLaunch AppId=$app( |$)" >/dev/null && [ $i -lt 60 ]; do sleep 1; i=$((i + 1)); done
	if pgrep -f "SteamLaunch AppId=$app( |$)" >/dev/null; then echo "    warning: Steam still reports app $app running after 60 s"; fi
}

# Place the game's window with a KWin rule: HL2's -displayindex is not
# followed on this desktop (session 0: the window went to the screen with the
# mouse). The rule forces position (the target output's origin) and
# fullscreen and keyboard focus (focus-stealing prevention off: under
# gamescope the keys did not reach the game, 2026-09-24), matched on the
# window class (a regular expression: native
# hl2_linux, and Proton's steam_app_<id> for HL2 on Windows and HL2 RTX,
# which a plain match missed on 2026-09-24); the user's own rules file is
# backed up and restored after every step.
export DBUS_SESSION_BUS_ADDRESS=${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/$(id -u)/bus}
KWINRULES=$HOME/.config/kwinrulesrc
kwin_reload() { qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || qdbus org.kde.KWin /KWin reconfigure >/dev/null 2>&1; }
kwin_rule_set() { # output-name
	local geo x y
	geo=$(timeout 10 xrandr --listmonitors 2>/dev/null | awk -v n="$1" 'NR > 1 && $NF == n {print $3}')
	[ -n "$geo" ] || return 1
	x=$(echo "$geo" | cut -d+ -f2); y=$(echo "$geo" | cut -d+ -f3)
	[ -f "$KWINRULES.hl2bench-backup" ] || cp -p "$KWINRULES" "$KWINRULES.hl2bench-backup" 2>/dev/null || : >"$KWINRULES.hl2bench-backup"
	cat >"$KWINRULES" <<EOR
[General]
count=1
rules=hl2bench

[hl2bench]
Description=HL2 bench suite: place the game on $1 (temporary)
wmclass=^(hl2_linux|steam_app_220|steam_app_2477290|hl2\\.exe|gamescope)$
wmclassmatch=3
position=$x,$y
positionrule=2
fullscreen=true
fullscreenrule=2
acceptfocus=true
acceptfocusrule=2
fsplevel=0
fsplevelrule=2
EOR
	kwin_reload
	echo "$x,$y"
}
kwin_rule_clear() {
	[ -f "$KWINRULES.hl2bench-backup" ] || return 0
	mv "$KWINRULES.hl2bench-backup" "$KWINRULES"
	kwin_reload
}

launch_options() {
	python3 - "$LOCALCONFIG" "$1" <<'EOF'
import re, sys
t = open(sys.argv[1], encoding='utf-8', errors='replace').read()
m = re.search(r'\n\t{5}"' + sys.argv[2] + r'"\n\t{5}\{(.*?)\n\t{5}\}', t, re.S)
lo = re.search(r'"LaunchOptions"\s+"([^"]*)"', m.group(1)) if m else None
print(lo.group(1) if lo else '')
EOF
}

# --- preflight ---------------------------------------------------------------
if ! pgrep -x steam >/dev/null; then
	echo "starting Steam"
	steam -silent >/dev/null 2>&1 &
	i=0; until pgrep -x steamwebhelper >/dev/null || [ $i -ge 180 ]; do sleep 1; i=$((i + 1)); done
	pgrep -x steam >/dev/null || { echo "Steam did not start" >&2; exit 1; }
	sleep 30   # let it finish logging in before the first launch
fi
[ -f "$(app_write 220)/$DEMO.dem" ] || { echo "demo $DEMO.dem not found" >&2; exit 1; }
for app in $(grep -v '^#' "$STEPS" | awk 'NF{print $2}' | sort -u); do
	lo=$(launch_options "$app")
	case "$lo" in
		*game-wrap.sh*%command%*) ;;
		*) echo "app $app launch options must be: $HERE/game-wrap.sh %command%   (now: '$lo')" >&2; exit 1 ;;
	esac
done
for app in 220 2477290; do
	if [ -n "$(app_pid $app)" ]; then echo "a game ($app) is already running" >&2; exit 1; fi
done

contention() {
	local load1 ncpu gpulist fossil
	load1=$(cut -d' ' -f1 /proc/loadavg); ncpu=$(nproc)
	gpulist=$(nvidia-smi --query-compute-apps=process_name --format=csv,noheader 2>/dev/null |
		grep -v -E 'kwin_wayland|kwin_x11|Xwayland|steamwebhelper|/steam$|gnome-shell|hl2_linux|hl2\.exe|wine' | grep -c .)
	fossil=$(pgrep -c -x fossilize_repla 2>/dev/null); fossil=${fossil:-0}
	if python3 -c "import sys; sys.exit(0 if $load1/$ncpu > 0.30 else 1)" || [ "$gpulist" -gt 0 ] || [ "$fossil" -gt 0 ]; then
		echo "CONTENDED load1=$load1/$ncpu gpu_jobs=$gpulist shader_compiles=$fossil"
	else
		echo "CLEAN load1=$load1/$ncpu"
	fi
}
STATE=$(contention)
echo "machine: $STATE"
case "$STATE" in CONTENDED*) [ "$FORCE" = 1 ] || { echo "refusing; wait for a quiet machine or use --force" >&2; exit 1; } ;; esac

# "# gpu: nvidia" (proprietary, default) or "# gpu: mesa" (nouveau + NVK)
GPU=$(sed -n 's/^# gpu: *\([a-z]*\).*/\1/p' "$STEPS" | head -1)
GPU=${GPU:-nvidia}
case "$GPU" in nvidia|mesa) ;; *) echo "unknown gpu family '$GPU'" >&2; exit 1 ;; esac
DISPLAY_DEFAULT=$(sed -n 's/^# display: *\([A-Za-z0-9-]*\).*/\1/p' "$STEPS" | head -1)
export DISPLAY=${DISPLAY:-:0}

# Output name -> SDL display index, in the order the display server lists
# its monitors (checked in the first run: the view steps show which TV lit).
display_index() { # name
	timeout 10 xrandr --listmonitors 2>/dev/null | awk -v n="$1" 'NR > 1 && $NF == n {sub(":", "", $1); print $1; exit}'
}

SUITE="$ROOT/suite-$(date +%Y%m%d-%H%M%S)-$(basename "$STEPS" .conf)"
mkdir -p "$SUITE"
cp "$STEPS" "$SUITE/"
{
	echo "suite: $SUITE"
	echo "kernel: $(uname -r)"
	nvidia-smi --query-gpu=name,driver_version,pcie.link.gen.current,pcie.link.width.current --format=csv,noheader 2>/dev/null | sed 's/^/gpu: /'
	echo "demo sha256: $(sha256sum "$(app_write 220)/$DEMO.dem" | cut -c1-64)"
	for app in 220 2477290; do echo "app $app build: $(grep -m1 '"buildid"' "$LIB/appmanifest_$app.acf" 2>/dev/null | grep -o '[0-9]\+')"; done
	echo "stereo module: $(sha256sum "$(app_game 220)/bin/sourcevr.so" | cut -c1-64)"
	echo "gpu family: $GPU"
	echo "default display: ${DISPLAY_DEFAULT:-game default}"
	echo "monitors:"; timeout 10 xrandr --listmonitors 2>/dev/null | sed 's/^/  /' 
	echo "mangohud: $(command -v mangohud || echo none)"
	echo "start state: $STATE"
} | tee "$SUITE/suite-info.txt"
printf 'step\tkind\tapp\trenderer\tvr\tstate\tfps\tvariability\tframes\tseconds\tvendor\tdevice\tresult\n' >"$SUITE/summary.tsv"

cleanup() {
	rm -f "$ENVFILE" "$(app_game 220)/bin/svrtv.ini" "$(app_write 220)/cfg/game.cfg" "$(app_write 2477290)/cfg/game.cfg"
	kwin_rule_clear
	"$HERE/wiz3d-setup.sh" remove >/dev/null 2>&1 || true
	sync
	[ "$REBOOT" = 1 ] && { echo "rebooting (--reboot-after)"; systemctl reboot; }
}
trap cleanup EXIT

# --- one step ----------------------------------------------------------------
run_step() { # id app renderer vr runs frame kind [display]
	local id=$1 app=$2 renderer=$3 vr=$4 runs=$5 frame=$6 kind=$7 disp=${8:-$DISPLAY_DEFAULT} didx=""
	local game write out args pid i limit state gpumon cpumon
	game=$(app_game "$app"); write=$(app_write "$app")
	out="$SUITE/$id"; mkdir -p "$out" "$write/bench" "$write/cfg"
	state=$(contention)
	echo "=== step $id ($kind, app $app, $renderer, vr=$vr) $(date +%T) $state"

	# The RTX game needs the demo in its own directory.
	[ -f "$write/$DEMO.dem" ] || cp "$(app_write 220)/$DEMO.dem" "$write/"

	# wiz3D (vr=wiz) is installed for its step only; our module stays idle.
	if [ "$vr" = wiz ]; then "$HERE/wiz3d-setup.sh" install | sed 's/^/    /'; fi

	# Anaglyph steps: the module packs side by side and gamescope (64-bit,
	# outside the game) turns it into red/cyan anaglyph with
	# tools/vr-stereo-spectator/anaglyph/svrtv-anaglyph.fx: technique 0
	# "CRT", 1 "modern screens".
	# gamescope must composite on the GPU the game renders on (RTX 3060,
	# 10de:2504): on another one the import of the game's frames failed and
	# gamescope aborted (2026-09-24). The backend is named, since in Steam's
	# launch environment the automatic choice fell to headless: sdl. The
	# wayland backend hands frames to KWin as NVIDIA buffers, which KWin on the
	# AMD iGPU cannot import (the same dmabuf error, then an abort).
	local GS_VK_DEVICE=${GS_VK_DEVICE:-10de:2504}
	# sbs-gamescope and sbs-gamescope-identity: side by side for the 3D TV,
	# through gamescope with no effect or with the Identity pass (technique 2),
	# to separate gamescope's path from the anaglyph colour filtering
	# (the swim investigation, 2026-09-25).
	local layout=$vr gsfx="" usegs="" gsgrab=""
	case "$vr" in
		anaglyph-crt) layout=sbs; gsfx=0; usegs=1 ;;
		anaglyph-modern) layout=sbs; gsfx=1; usegs=1 ;;
		sbs-gamescope) layout=sbs; usegs=1 ;;
		sbs-gamescope-identity) layout=sbs; gsfx=2; usegs=1 ;;
		# the same with gamescope in relative mouse mode throughout
		# (--force-grab-cursor): p08/p09 showed the swim is gamescope's path
		# with mouse look only (2026-09-25).
		sbs-gamescope-grab) layout=sbs; usegs=1; gsgrab=1 ;;
		anaglyph-modern-grab) layout=sbs; gsfx=1; usegs=1; gsgrab=1 ;;
		# stereo3d: the module with no preset layout, so the game's own
		# switches turn 3D on: -stereo3d on the launch line (HL2BENCH_ARGS) or
		# vr_display_3d from the video options (the in-game 3D offer, 2026-09-26).
		stereo3d) layout="" ;;
	esac
	if [ -n "$gsfx" ]; then
		mkdir -p "$HOME/.local/share/gamescope/reshade/Shaders"
		cp "$HERE/../vr-stereo-spectator/anaglyph/svrtv-anaglyph.fx" "$HOME/.local/share/gamescope/reshade/Shaders/"
	fi

	# Stereo module settings (native HL2 only).
	if [ "$app" = 220 ]; then
		if [ "$vr" = off ] || [ "$vr" = wiz ]; then rm -f "$game/bin/svrtv.ini"
		else
			printf 'SVRTV_WIDTH=%s\nSVRTV_HEIGHT=%s\nSVRTV_LOG=%s\n' "$RES_W" "$RES_H" "$out/svrtv.log" >"$game/bin/svrtv.ini"
			[ -n "$layout" ] && printf 'SVRTV_LAYOUT=%s\n' "$layout" >>"$game/bin/svrtv.ini"
			# Extra module settings for a test run, e.g. SVRTV_EXTRA="SVRTV_HUDCOPY=1".
			[ -n "${SVRTV_EXTRA:-}" ] && printf '%s\n' $SVRTV_EXTRA >>"$game/bin/svrtv.ini"
		fi
	fi

	# This build ignores "wait" unless sv_allow_wait_command is on (session 0
	# showed every wait skipped). View steps load the map from the command
	# line, before the step config runs.
	# -condebug: the whole console from the first line (con_logfile starts
	# only when bench_step runs), to game-dir/console.log.
	rm -f "$write/console.log"
	args="-condebug -novid -console -w $RES_W -h $RES_H -fullscreen -timedemo_comment $id +sv_allow_wait_command 1"
	# Extra launch options for a test run, as a player would put them in Steam's
	# launch options (e.g. HL2BENCH_ARGS="+mat_forceaniso 16").
	[ -n "${HL2BENCH_ARGS:-}" ] && args="$args $HL2BENCH_ARGS"
	[ "$kind" = view ] && args="$args +sv_cheats 1 +map d1_town_01"
	# play: Daniel plays; the frame column names the map to start on.
	[ "$kind" = play ] && args="$args +map $frame"
	rm -f "$write/bench/$id.log" "$write/cfg/game.cfg"
	args="$args +exec bench_step"
	case "$renderer" in opengl) args="-opengl $args" ;; vulkan) args="-vulkan $args" ;; esac
	if [ -n "$disp" ]; then
		didx=$(display_index "$disp")
		if [ -z "$didx" ]; then
			echo "    display $disp is not an enabled monitor; skipping"
			printf '%s\t%s\t%s\t%s\t%s\t\t\t\t\t\t\t\tno-display-%s\n' "$id" "$kind" "$app" "$renderer" "$vr" "$disp" >>"$SUITE/summary.tsv"
			return
		fi
		# Inside gamescope the game sees one display; gamescope picks the TV.
		[ -z "$usegs" ] && args="-displayindex $didx $args"
		echo "    display $disp = index $didx, KWin rule at $(kwin_rule_set "$disp")"
	fi

	{
		echo "STEP_OUT=$out"
		echo "STEP_ARGS=\"$args\""
		# GAMESCOPE_BIN picks another gamescope, e.g. the 3D TV build with its
		# nested output on MAILBOX (~/.local/bin/gamescope-3dtv, 2026-09-25).
		[ -n "$usegs" ] && echo "SVRTV_GAMESCOPE_BIN=\"${GAMESCOPE_BIN:-gamescope}\""
		[ -n "$usegs" ] && [ -n "${GAMESCOPE_NESTED_PRESENT_MODE:-}" ] && echo "export GAMESCOPE_NESTED_PRESENT_MODE=$GAMESCOPE_NESTED_PRESENT_MODE"
		[ -n "$usegs" ] && echo "SVRTV_GAMESCOPE=\"--backend ${GS_BACKEND:-sdl} -g --prefer-vk-device $GS_VK_DEVICE -f -W $RES_W -H $RES_H -w $RES_W -h $RES_H ${didx:+--display-index $didx}${gsgrab:+ --force-grab-cursor}${gsfx:+ --reshade-effect svrtv-anaglyph.fx --reshade-technique-idx $gsfx}\""
		# Render on the RTX 3060 (the desktop runs on the AMD iGPU), through
		# the driver family the steps file names in its "# gpu:" line.
		if [ "$GPU" = mesa ]; then
			# Steam's own environment carries NVIDIA offload variables
			# (__NV_PRIME_RENDER_OFFLOAD, __GLX_VENDOR_LIBRARY_NAME,
			# __VK_LAYER_NV_optimus); with no proprietary driver they must go.
			echo "unset __NV_PRIME_RENDER_OFFLOAD __GLX_VENDOR_LIBRARY_NAME __VK_LAYER_NV_optimus"
			echo "DRI_PRIME=1"
			echo "MESA_VK_DEVICE_SELECT_FORCE_DEFAULT_DEVICE=1"
		else
			echo "__NV_PRIME_RENDER_OFFLOAD=1"
			echo "__GLX_VENDOR_LIBRARY_NAME=nvidia"
			echo "__VK_LAYER_NV_optimus=NVIDIA_only"
		fi
		# DXVK (the -vulkan renderer) presents with its own interval; the
		# engine's mat_vsync 0 does not reach it (a07: locked at 59.94 fps).
		# Watch steps force vsync the same way: VR mode's Activate() sets
		# mat_vsync 0 on Linux, and once that reached the display the demo
		# raced at 364 fps (2026-09-24).
		if [ "$renderer" = vulkan ]; then
			if [ "$kind" = watch ] || [ "$kind" = play ]; then echo "DXVK_CONFIG=\"d3d9.presentInterval = ${PLAY_PRESENT_INTERVAL:-1}${DXVK_EXTRA:+;$DXVK_EXTRA}\""
			else echo 'DXVK_CONFIG="d3d9.presentInterval = 0"'; fi
		fi
		if command -v mangohud >/dev/null && [ "$kind" = timedemo ]; then
			echo "MANGOHUD=1"
			echo "MANGOHUD_DLSYM=1"
			echo "MANGOHUD_CONFIG=no_display,output_folder=$out,autostart_log=1,log_interval=0"
		fi
	} >"$ENVFILE"

	{
		echo "sv_allow_wait_command 1"
		echo "con_logfile \"bench/$id.log\""
		case "$kind" in watch|play) echo "mat_vsync 1" ;; *) echo "mat_vsync 0"; echo "fps_max 0" ;; esac
		echo "demo_quitafterplayback 1"
		case "$vr" in sbs|sbs-gamescope*|tab|anaglyph-*) [ "$kind" != view ] && echo "vr_activate" ;; esac
		# Extra console commands for a test run, separated by ";"
		# (e.g. HL2BENCH_CMDS="sv_cheats 1;viewmodel_fov 75").
		[ -n "${HL2BENCH_CMDS:-}" ] && printf '%s\n' "$HL2BENCH_CMDS" | tr ';' '\n'
		case "$kind" in
			view) ;;   # the sequence goes in game.cfg, below
			timedemo) echo "timedemo_runcount $runs"; echo "timedemo $DEMO" ;;
			# benchframe plays the demo once, and this demo's first playback
			# stops after 2 frames; a second run is where frame $frame comes.
			frame) echo "timedemo_runcount 2"; echo "benchframe $DEMO $frame ${id}_frame$frame" ;;
			# Real speed: a timed demo at vsync 60 Hz takes the demo's own length
			# (a07, 164 s). This demo's first playback always stops after 2
			# frames (every timed step), so the second run is the one to watch.
			watch) echo "timedemo_runcount 2"; echo "timedemo $DEMO" ;;
			play) ;;
		esac
	} >"$write/cfg/bench_step.cfg"
	cp "$write/cfg/bench_step.cfg" "$out/"
	# View steps: the server runs "exec game.cfg" in GameInit() on every map
	# load, single-player included (SDK gameinterface.cpp); listenserver.cfg
	# only runs under the multiplayer rules. GameInit comes before the player
	# exists, and "wait" does not hold commands until the player is in (the
	# 15:10 run: getpos printed 0 0 0 during loading, setang did nothing, and
	# the sequence stalled). "screenshot" is different: it waits for the next
	# rendered frame, which is the spawn view (d1_town_01, yaw 90). So a view
	# step takes that one picture and the suite closes the game once the file
	# exists. No game.cfg ships in the game's VPKs; the loose file is removed
	# after the step so it never touches normal play.
	if [ "$kind" = view ]; then
		{
			echo "con_logfile \"bench/$id.log\""
			echo "screenshot"
		} >"$write/cfg/game.cfg"
		cp "$write/cfg/game.cfg" "$out/"
	fi
	[ "$kind" = watch ] && echo "    WATCH: television to 3D ${vr}; real-time playback, about 3 minutes"

	local before=0 csv
	for csv in "$write/sourcebench.csv" "$write/SourceBench.csv" "$game/sourcebench.csv" "$game/SourceBench.csv"; do [ -f "$csv" ] && before=$(wc -l <"$csv") && break; done
	touch "$out/.start"

	# Nothing may still be running from an earlier step.
	close_game 220; close_game 2477290
	steam -applaunch "$app" >/dev/null 2>&1 &
	i=0; until pid=$(app_pid "$app") || [ $i -ge 180 ]; do sleep 1; i=$((i + 1)); done
	if [ -z "${pid:-}" ]; then
		echo "    game did not start within 180 s"
		printf '%s\t%s\t%s\t%s\t%s\t%s\t\t\t\t\t\t\tno-start\n' "$id" "$kind" "$app" "$renderer" "$vr" "${state%% *}" >>"$SUITE/summary.tsv"
		return
	fi
	echo "    pid $pid after ${i}s"
	nvidia-smi --query-gpu=timestamp,clocks.gr,clocks.mem,utilization.gpu,utilization.memory,power.draw,temperature.gpu,memory.used,pstate \
		--format=csv,nounits -lms 250 >"$out/gpu.csv" 2>/dev/null &
	gpumon=$!
	{
		echo "time,load1,proc_cpu_pct,proc_rss_mb"
		while kill -0 "$pid" 2>/dev/null; do
			ps -o %cpu=,rss= -p "$pid" 2>/dev/null | awk -v t="$(date +%T)" -v l="$(cut -d' ' -f1 /proc/loadavg)" '{printf "%s,%s,%s,%.0f\n", t, l, $1, $2/1024}'
			sleep 1
		done
	} >"$out/cpu.csv" &
	cpumon=$!

	# The game quits itself after timedemo and watch; frame and view steps
	# are done as soon as their image exists.
	# A frame step reaches demo frame 3000 in well under a minute; a view
	# step waits for the level (HL2 RTX took 53 s on its first launch).
	case "$kind" in frame) limit=240 ;; view) limit=180 ;; play) limit=86400 ;; *) limit=$(( (runs > 0 ? runs : 1) * 400 + 300 )) ;; esac
	local result=exited
	i=0
	while kill -0 "$pid" 2>/dev/null && [ $i -lt $limit ]; do
		if { [ "$kind" = frame ] || [ "$kind" = view ]; } && [ -n "$(find "$write" "$game" -maxdepth 2 -newer "$out/.start" -name '*.tga' 2>/dev/null | head -1)" ]; then
			sleep 3; result=$kind-saved; break
		fi
		sleep 1; i=$((i + 1))
	done
	if kill -0 "$pid" 2>/dev/null && [ "$result" = exited ]; then result=timeout; echo "    still running after ${limit}s"; fi
	close_game "$app"
	[ "$result" = exited ] || echo "    closed ($result)"
	kill "$gpumon" "$cpumon" 2>/dev/null; wait "$gpumon" "$cpumon" 2>/dev/null
	echo "    $result after ${i}s"

	# Collect.
	cp "$write/bench/$id.log" "$out/console.log" 2>/dev/null
	cp "$write/console.log" "$out/condebug.log" 2>/dev/null
	# The module's per-frame angle log (SVRTV_ANGLELOG=1), moved so the next
	# step starts clean.
	[ -f "$game/bin/svrtv-angles.tsv" ] && mv "$game/bin/svrtv-angles.tsv" "$out/svrtv-angles.tsv"
	for csv in "$write/sourcebench.csv" "$write/SourceBench.csv" "$game/sourcebench.csv" "$game/SourceBench.csv"; do
		[ -f "$csv" ] || continue
		{ head -1 "$csv"; tail -n +"$((before + 1))" "$csv" | grep -v '^demofile'; } >"$out/SourceBench-rows.csv"
		break
	done
	find "$write" "$game" -maxdepth 2 -newer "$out/.start" \( -name '*.tga' -o -name '*.jpg' -o -name '*.png' \) -exec cp {} "$out/" \; 2>/dev/null
	python3 - "$out" "$id" "$kind" "$app" "$renderer" "$vr" "${state%% *}" "$result" <<'EOF' >>"$SUITE/summary.tsv"
import csv, os, re, sys
out, sid, kind, app, rend, vr, state, result = sys.argv[1:9]
rows = []
p = os.path.join(out, 'SourceBench-rows.csv')
if os.path.exists(p):
    rows = list(csv.DictReader(open(p), skipinitialspace=True))
if not rows:
    print('\t'.join([sid, kind, app, rend, vr, state, '', '', '', '', '', '', result]))
for r in rows:
    print('\t'.join([sid, kind, app, rend, vr, state, r.get('fps', ''), r.get('framerate variability', ''),
                     r.get('numframes', ''), r.get('totaltime', ''), r.get('vendor id', ''), r.get('device id', ''), result]))
EOF
	grep -h -E 'frames .* seconds .* fps|Demo playback finished' "$out/console.log" 2>/dev/null | sed 's/^/    /'
	if [ "$vr" = wiz ]; then "$HERE/wiz3d-setup.sh" remove | sed 's/^/    /'; fi
	rm -f "$write/cfg/game.cfg"
	kwin_rule_clear
	sleep 5
}

# --- run every step ----------------------------------------------------------
grep -v '^#' "$STEPS" | awk 'NF' | while read -r id app renderer vr runs frame kind disp; do
	case "$ONLY" in ""|*",$id,"*) run_step "$id" "$app" "$renderer" "$vr" "$runs" "$frame" "$kind" "$disp" </dev/null ;; esac
done

echo "=== done $(date +%T)"
column -t -s "$(printf '\t')" "$SUITE/summary.tsv"
sync
echo "results: $SUITE"
