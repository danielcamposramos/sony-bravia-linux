#!/bin/bash
# Steam launch wrapper for the HL2 bench suite. Set a game's launch options
# once to:
#     /K3D/GitHub/sony-bravia-linux/tools/hl2-bench/game-wrap.sh %command%
# Outside a suite run it starts the game as is, or with play.env (below).
# During a run, hl2-suite.sh writes the step's settings to
# /K3D/temp/hl2-bench/current.env: environment (GPU selection, metrics) and
# STEP_ARGS, the game arguments for that step.
# Outside a run, play.env (same format) holds Daniel's play launch, when set:
# Steam's Play button then starts the game the way that file says.
ENVFILE=${HL2_BENCH_ENVFILE:-/K3D/temp/hl2-bench/current.env}
[ -f "$ENVFILE" ] || ENVFILE=${HL2_BENCH_PLAY_ENVFILE:-/K3D/temp/hl2-bench/play.env}
STEP_ARGS=""
if [ -f "$ENVFILE" ]; then
	set -a
	# shellcheck disable=SC1090
	. "$ENVFILE"
	set +a
	[ -n "${STEP_OUT:-}" ] && mkdir -p "$STEP_OUT"
	# The system output (version B): the game's screen holds two eyes of the
	# render resolution saved in the game's settings (vr_display_render, the
	# menu's "Render resolution per eye"), side by side; the game's and
	# gamescope's sizes are set from it here, at start.
	if [ "${SVRTV_OUTPUT:-}" = system ]; then
		gdir="" mod=""
		prev=""
		for a in "$@"; do
			case $a in */hl2.sh) gdir=${a%/hl2.sh} ;; esac
			[ "$prev" = -game ] && mod=$a
			prev=$a
		done
		idx=$(sed -n 's/^vr_display_render "\([0-9]\)".*/\1/p' "$gdir/${mod:-hl2}/cfg/config.cfg" 2>/dev/null)
		case ${idx:-2} in
		0) ew=1280 eh=720 ;;
		1) ew=1600 eh=900 ;;
		3) ew=2560 eh=1440 ;;
		4) ew=3200 eh=1800 ;;
		5) ew=3840 eh=2160 ;;
		*) ew=1920 eh=1080 ;;
		esac
		fw=$((ew * 2))
		# gamescope's window on the desktop stays at most two 1920x1080 eyes:
		# above that it scales the game's frame down (the supersampling), so
		# the window fits the desktop's X screen (the pointer reaches all of
		# it) and is placed on the 3D display like the 1080 one (2026-10-02)
		ww=$fw wh=$eh
		[ "$eh" -gt 1080 ] && ww=3840 wh=1080
		export SVRTV_WIDTH=$ew SVRTV_HEIGHT=$eh
		STEP_ARGS=$(printf '%s' "$STEP_ARGS" | sed "s/-w [0-9]* -h [0-9]*/-w $fw -h $eh/")
		SVRTV_GAMESCOPE=$(printf '%s' "${SVRTV_GAMESCOPE:-}" | sed "s/-W [0-9]* -H [0-9]* -w [0-9]* -h [0-9]*/-W $ww -H $wh -w $fw -h $eh/")
	fi
	# The game's DXVK is v2.0, which reads a config file but not the
	# DXVK_CONFIG variable (2.1+). Write the suite's settings next to the
	# game, where Steam's runtime container sees it.
	if [ -n "${DXVK_CONFIG:-}" ]; then
		for a in "$@"; do case $a in */hl2.sh) gd=${a%/hl2.sh} ;; esac; done
		if [ -n "${gd:-}" ]; then
			# play.env owns a persistent, separately named config. Suite runs
			# supply their unique run ID, app tag and recovery directory.
			if [ -z "${HL2BENCH_RUN_ID:-}" ]; then
				HL2BENCH_RUN_ID=play
				HL2BENCH_DXVK_TAG=play
				HL2BENCH_STATE_DIR=$(dirname "$ENVFILE")
				mkdir -p "$HL2BENCH_STATE_DIR"
			fi
			case ${HL2BENCH_RUN_ID:-} in *[!A-Za-z0-9._-]*|'')
				echo "refusing DXVK bench config without a safe HL2BENCH_RUN_ID" >&2
				exit 1
			;; esac
			case ${HL2BENCH_DXVK_TAG:-} in 220|2477290|play) ;; *)
				echo "refusing DXVK bench config without a known app tag" >&2
				exit 1
			;; esac
			[ -d "${HL2BENCH_STATE_DIR:-}" ] || {
				echo "refusing DXVK bench config without an active state directory" >&2; exit 1;
			}
			cfg="$gd/hl2-bench-dxvk-$HL2BENCH_RUN_ID-$HL2BENCH_DXVK_TAG.conf"
			sha="$HL2BENCH_STATE_DIR/dxvk-$HL2BENCH_DXVK_TAG.sha256"
			if [ -e "$cfg" ]; then
				[ -f "$sha" ] && [ "$(sha256sum "$cfg" | cut -d' ' -f1)" = "$(cat "$sha")" ] || {
					echo "refusing to overwrite unowned DXVK config: $cfg" >&2; exit 1;
				}
			fi
			tmp="$cfg.tmp.$$"
			printf '%s\n' "$DXVK_CONFIG" | tr ';' '\n' >"$tmp"
			mv "$tmp" "$cfg"
			sha256sum "$cfg" | cut -d' ' -f1 >"$sha"
			export DXVK_CONFIG_FILE="$cfg"
		fi
	fi
	[ -n "${STEP_OUT:-}" ] && printf '%s\n' "$@" $STEP_ARGS >"$STEP_OUT/launch-args.txt"
fi
# Anaglyph steps run the game inside gamescope, which applies the effect
# (the suite sets SVRTV_GAMESCOPE to its arguments).
# shellcheck disable=SC2086 # deliberate word lists
# The game must use gamescope's own X11 display, not the desktop's Wayland
# (a Vulkan test program that inherited WAYLAND_DISPLAY aborted inside it).
# gamescope's SDL window goes through X11 (its Wayland path hands NVIDIA
# buffers to KWin on the AMD iGPU, which cannot import them).
if [ -n "${SVRTV_GAMESCOPE:-}" ]; then
	export SDL_VIDEODRIVER=x11
	[ -n "${STEP_OUT:-}" ] && env | grep -E '^(DISPLAY|WAYLAND_DISPLAY|XDG_RUNTIME_DIR|XDG_SESSION_TYPE|SDL_VIDEODRIVER)=' >"$STEP_OUT/gamescope-env.txt"
fi
# gamescope's log (and the game's stderr under it) goes to the step's folder,
# so a run shows which present mode gamescope used.
if [ -n "${SVRTV_GAMESCOPE:-}" ] && [ -n "${STEP_OUT:-}" ]; then
	exec "${SVRTV_GAMESCOPE_BIN:-gamescope}" $SVRTV_GAMESCOPE -- env -u WAYLAND_DISPLAY "$@" $STEP_ARGS 2>"$STEP_OUT/gamescope.log"
fi
[ -n "${SVRTV_GAMESCOPE:-}" ] && exec "${SVRTV_GAMESCOPE_BIN:-gamescope}" $SVRTV_GAMESCOPE -- env -u WAYLAND_DISPLAY "$@" $STEP_ARGS
# shellcheck disable=SC2086 # STEP_ARGS is a deliberate word list
exec "$@" $STEP_ARGS
