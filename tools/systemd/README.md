# d2server durable services — systemd units

The TV-lane services on d2server (192.168.0.60) used to run as bare
`nohup` processes: they died with their parent shell, never came back
after a reboot, and leaked ffmpeg transcode children on hard exits.
These units make them real system services, and `bravia-stack.target`
is the single "detect and launch everything" bucket Daniel asked for:
starting the target starts anything in the stack that isn't already
running (systemd tracks state, no duplicate launches), and enabling it
brings the whole stack up at boot.

```
bravia-stack.target          umbrella bucket
 ├─ bravia-mediabrowser.service   tv-mediabrowser app  (:8090)
 ├─ bravia-rd1-probe.service       rd1 HTTPS probe     (:8443)
 ├─ serviio.service                stock unit (Serviio 2.5, :8895/:23423)
 └─ apache2.service                stock unit (rd1 portal :80/:443)
```

## Deploy (on d2server, as root)

```
sudo cp bravia-*.service bravia-stack.target /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bravia-mediabrowser.service bravia-rd1-probe.service
sudo systemctl enable bravia-stack.target
```

## Migration from the nohup-era processes

The old processes hold ports 8090/8443 — the units cannot start until
they are gone. **Kill and start are two separate ssh calls** (project
rule: never pkill a pattern contained in the running command line).

```
# 1. verify nobody is streaming first (app + portal + Serviio + Apache):
ss -tn state established '( sport = :80 or sport = :443 or sport = :8090 or sport = :8443 or sport = :8895 )'
# 2. (separate ssh call) stop the old processes:
pkill -f "[s]erver.py 8090"
pkill -f "[s]erve.py 8443"
# 3. (separate ssh call) start the bucket:
sudo systemctl start bravia-stack.target
# 4. verify:
systemctl status bravia-mediabrowser bravia-rd1-probe --no-pager
curl -s http://127.0.0.1:8090/ >/dev/null && echo app-ok
curl -sk https://127.0.0.1:8443/ >/dev/null && echo probe-ok
```

## Notes

- Logs keep flowing into the same files the nohup era used
  (`server.log`, `rd1-serve.log`) via `StandardOutput=append:` —
  existing tooling and history stay valid. systemd 252 (Debian 12)
  supports `append:`.
- `KillMode` stays default (`control-group`): ffmpeg transcode children
  of the app are cleaned up on stop instead of leaking, which the
  nohup era could not guarantee.
- `serviio.service` and `apache2.service` are NOT rewritten here —
  they are stock units, already systemd-native. The target only gains
  a `Wants=` handle on them so the bucket launches the full stack.
- The SEI-3D batch (`bravia_sei3d.py`) is deliberately NOT part of the
  stack: it is a one-shot media job, not a service.