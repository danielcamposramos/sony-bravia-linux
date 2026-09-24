#!/bin/bash
# Steam launch wrapper for the HL2 bench suite. Set a game's launch options
# once to:
#     /K3D/GitHub/sony-bravia-linux/tools/hl2-bench/game-wrap.sh %command%
# Outside a suite run it simply starts the game. During a run, hl2-suite.sh
# writes the step's settings to /K3D/temp/hl2-bench/current.env: environment
# (GPU selection, metrics) and STEP_ARGS, the game arguments for that step.
ENVFILE=/K3D/temp/hl2-bench/current.env
STEP_ARGS=""
if [ -f "$ENVFILE" ]; then
	set -a
	# shellcheck disable=SC1090
	. "$ENVFILE"
	set +a
	# The game's DXVK is v2.0, which reads a config file but not the
	# DXVK_CONFIG variable (2.1+). Write the suite's settings next to the
	# game, where Steam's runtime container sees it.
	if [ -n "${DXVK_CONFIG:-}" ]; then
		for a in "$@"; do case $a in */hl2.sh) gd=${a%/hl2.sh} ;; esac; done
		if [ -n "${gd:-}" ]; then
			printf '%s\n' "$DXVK_CONFIG" | tr ';' '\n' >"$gd/hl2-bench-dxvk.conf"
			export DXVK_CONFIG_FILE="$gd/hl2-bench-dxvk.conf"
		fi
	fi
	[ -n "${STEP_OUT:-}" ] && printf '%s\n' "$@" $STEP_ARGS >"$STEP_OUT/launch-args.txt"
fi
# shellcheck disable=SC2086 # STEP_ARGS is a deliberate word list
exec "$@" $STEP_ARGS
