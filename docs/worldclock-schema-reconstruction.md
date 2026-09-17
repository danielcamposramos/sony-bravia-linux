# Reconstructing a lost configuration schema — World Clock

**2026-09-17.** The first piece of this platform we did not recover, but
**rebuilt**. Everything else in the AppliCast lane so far has been
preservation: byte-exact bundles, original signatures, Sony's own files
served from our own LAN. This one is different. The file no longer
exists anywhere, so it was reconstructed from the widget's own code and
now runs on the TV.

## The symptom

`SNY_BasicAlarm` and `SNY_WorldClock` both declare
`<preference>1</preference>` in `info.xml`, meaning "this widget has a
settings screen". On the restored TV, the Alarm's settings worked as
soon as its schema was in place. **World Clock's did not** — the widget
loaded and immediately showed its own error text:

> *"Please enter the Time Zone Hour in the preferential settings"*
> (`por:` *"Por favor introduza a Hora do Fuso Horário nas configurações
> preferenciais"*)

It was asking the owner to configure something the TV gave them no way
to configure.

## Why it happened

The settings editor is rendered by the TV's widget engine, not by the
widget, from a `preference.xml` inside the bundle. That file is:

- **not listed in `digest.txt`** — so it is outside the signed set, and
- **referenced by nothing** — no widget JavaScript mentions it, no
  layout points at it. Only the engine reads it.

Both properties matter. The second is why a scavenger that follows
references — fetch the manifest, then follow every asset the code names
— never sees the file at all. It has to be asked for by name. The first
is what makes the repair below legitimate rather than forgery.

`SNY_BasicAlarm/preference.xml` is still on Sony's CDN and was simply
missing from our mirror; fetching it fixed the Alarm outright (owner
verified on the EX725 the same day). **`SNY_WorldClock/preference.xml`
returns nothing** — not on the GA CDN, not under any of the filename
variants probed (`preference_fullscreen.xml`, `setting.xml`,
`settings.xml`, `option.xml`, `config.xml`, `preference_<lang>.xml`, and
the same set under `WidgetInfos/<id>/<locale>/`). The widget survives;
its configuration schema does not.

## What the code told us

`widget.js` names the file in a comment and then states its own contract:

```js
/******* Get Preference Setting from preference.xml *******/
function checkPreference() {
    var tmp_timezone = getStoredValue("Item1");
    var tmp_dst      = getStoredValue("Item2");
    var tmp_ampm     = getStoredValue("Item3");
    if (tmp_timezone == null) { Error_Message(1); }
    ...
```

Three slots, and the rest of the file fixes their domains exactly:

| Slot | Meaning | Domain | Evidence in `widget.js` |
|---|---|---|---|
| `Item1` | local GMT offset, whole hours | −12 … +14 | `gmt_hour = local_time - timezone - dstArray[0]`, and the sign tests `if ((timezone>0)&&…) / if ((timezone<0)&&…)` — it is signed arithmetic, not a city index |
| `Item2` | local daylight saving | `0` / `1` | `var _DST_OFF=0; var _DST_ON=1;` then `dstArray[0] = dst` |
| `Item3` | 12-hour display | `0` / `1` | `var _AMPM_OFF=0; var _AMPM_ON=1;` then `if(ampm==1){ … "pm" … "am" … }` |

Note `Item1` is *not* the city list. The 23 cities in `dic.txt` are the
panel display; the preference is the viewer's own offset from GMT, which
every other city is then computed against. Reading it as a city index
would have produced a clock that is silently wrong rather than visibly
broken — the kind of mistake that only shows up as "the time is off by
four hours" months later.

## The reconstruction

27 timezone options (−12 … +14) with a handful of familiar cities as
hints, plus two on/off pairs — written to `preference.xml` in the
bundle, where the engine looks for it:

```xml
<Preference>
    <Item name="Item1" type="single_select" label="Fuso horario (GMT)">
        <option value="-12">GMT-12</option>
        …
        <option value="-3">GMT-3 (Brasilia)</option>
        …
        <option value="14">GMT+14</option>
    </Item>
    <Item name="Item2" type="single_select" label="Horario de verao">
        <option value="0">Desligado</option>
        <option value="1">Ligado</option>
    </Item>
    <Item name="Item3" type="single_select" label="Formato 12 horas (AM/PM)">
        <option value="0">Desligado</option>
        <option value="1">Ligado</option>
    </Item>
</Preference>
```

The element grammar is not invented: it is taken from the surviving
schemas (`SNY_RSSReader`, `SNY_BasicAlarm`, `SNY_Facebook`,
`SNY_Twitter`), which establish `<Item name type label>` with
`type="text" | "password" | "single_select"` and `<option value>`
children. The reconstruction follows that grammar exactly, so the
engine parses it the way it parses Sony's own.

**1 681 bytes. No signed file touched. No signature recomputed.** The
bundle still verifies against Sony's original `digest.sig`, because the
file we added was never in the manifest to begin with.

## Why this one is different

Everything else in this lane is preservation — the bundles are Sony's,
byte-exact, signature intact, and our contribution is that they are
*served* at all. This is the first artifact where the original is
unrecoverable and the replacement is ours: read the machine's
expectations out of its own code, and write the missing half back.

It is also the smallest possible demonstration of the argument this
project keeps making. A widget that works perfectly was rendered
useless by one missing 1.6 KB XML file on a server the owner does not
control. Nothing was broken, nothing wore out, no license expired. The
feature died because a file stopped being served — and it came back
because the owner could serve it themselves.

That is the whole of right to repair, in 1 681 bytes.

## Reusable method

For any era widget whose settings screen is dead:

1. `grep getStoredValue` in `widget.js` → the `ItemN` slots it needs.
2. Read how each value is *used* — arithmetic means a number, a
   comparison against a named constant means an enum, concatenation into
   a URL means text. The constants (`_DST_ON`, `_AMPM_OFF`) name
   themselves.
3. Copy the `<Preference>` grammar from any surviving schema.
4. Write `preference.xml` into the bundle. It is unsigned, so the
   bundle still verifies.
5. Confirm on the EX725 before the HX855 (rule 5).

## Status

- Authored and deployed to the LAN AppliCast mirror; serving 200.
- `SNY_BasicAlarm`: Sony's own schema restored — **owner-verified
  working on the EX725, 2026-09-17**.
- `SNY_WorldClock`: reconstruction deployed, awaiting owner test.
- Labels are pt-BR here; a localized `preference.xml` per language is
  being generated separately, since Sony's surviving schemas are
  hardcoded English in every locale — the configuration UI was never
  translated for anyone.
