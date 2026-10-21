# KDL-40EX720: independent Opera compatibility observations

[Contributor ygtbsm reported these results in issue #22](https://github.com/danielcamposramos/sony-bravia-linux/issues/22) on 21 October 2026, using independently developed LAN diagnostics on a KDL-40EX720 with firmware **PKG4.027GAA-0104**.
The browser identified itself as Opera 11.00, Presto 2.7.61, InettvBrowser 2.2 on Linux/MIPS, with a reported 1920×1080 screen.
These are contributor-reported observations, not a repeat of our own hardware tests; the diagnostic source and raw captures are not attached to the issue.

## Findings and their limits

| Area | Reported observation | Limit |
| --- | --- | --- |
| Basic remote keys | OK 13; Left 37; Right 39; Up 38; Down 40 | Confirms these five EX725 mappings on this model/firmware; media-button attribution remains unresolved |
| Green button | Navigated to earlier pages | Consistent with EX725 history Back; no numeric mapping established |
| AppCache | API present, status UNCACHED; no manifest request observed; offline reopening failed | A negative experiment, not proof that every configuration is unsupported |
| Storage | Both cookies and localStorage worked initially; later initialization retained the cookie but lost localStorage | Cause unknown; no controlled power-cycle test |
| Already loaded page | JavaScript continued after the server stopped; a later diagnostic recorded 300 seconds of heartbeats | Does not demonstrate offline reopening or recovery after restart |

Other exercised capabilities included JSON, XMLHttpRequest, Canvas/PNG generation, data-URL and HTTP images, and keyboard events.
CSS transforms/transitions, audio/video elements, Server-Sent Events and Workers were reported as available; functional behavior was not established for each.
The diagnostic did not find WebSockets, Fetch, IndexedDB, WebSQL, Service Workers, Blob, FileReader, requestAnimationFrame or history.pushState.

## What this changes for the project

The independent key measurements extend the model-specific evidence in [the remote-key vocabulary](../era-key-vocabulary.md).
They do not extend the EX725's media-button findings to the EX720.
The contributor did not run our `/keys` page or MediaBrowser, and made no firmware modifications.

For unattended applications, keeping an existing page running and recovering after a restart are separate requirements.
This report supports the former in the tested conditions; it supplies no working offline installation or restart mechanism.
Do not rely on persistent configuration until retention is tested across controlled reload, history navigation, browser exit and TV power cycling.
Keep API detection separate from a successful operation: exposing an AppCache object, for example, did not establish caching here.
