# Telewizory Sony BRAVIA 3D (modele 2011–2012): znowu oglądaj filmy 3D i zdjęcia 3D, otwarty projekt naprawczy prowadzony przez właściciela

<!-- lang: pl · canonical source: ../../README.md (English) · translated 2026-09-18 -->

Ten projekt przywraca do życia telewizory BRAVIA sprzed ery Androida (seria KDL, 2010–2012) po tym, jak Sony wyłączyło ich usługi online, w całości w domowej sieci właściciela. Firmware nie jest modyfikowany, a zabezpieczenia DRM nie są naruszane. **Prawo do naprawy** w praktyce.

## Czy tego szukasz?

Ta strona odpowiada na pytania takie jak:

- „Sony Bravia film 3D z pendrive'a nie działa”
- „3D side by side przez sieć domową (DLNA) wyświetla się płasko”
- „Czy 3D działa tylko przez HDMI?”
- „Bravia nie wykrywa zdjęć 3D (plik MPO)”
- „Obraz obok siebie w menu 3D”

## Dlaczego film 3D wyświetla się płasko

- Te telewizory **same przełączają się w tryb 3D** tylko wtedy, gdy **sam strumień wideo** zawiera informację H.264 „frame packing” (SEI).
- Typowe pliki 3D (MKV side-by-side / top-bottom) mają tylko znacznik w kontenerze, który ginie, gdy plik wysyła serwer DLNA. Efekt: dwa obrazy obok siebie, bez 3D.
- **Rozwiązanie (bezstratne, bez ponownego kodowania):** `tools/bravia_sei3d.py` jednorazowo zapisuje SEI w pliku. Potem telewizor sam przełącza się w 3D, także przez DLNA. HandBrake przyjął już tę funkcję (PR #8100, w następnej wersji). Dołączony profil Serviio dodaje SEI automatycznie podczas transkodowania.
- Zamienione oczy? Telewizor nie pozwala zamienić lewego i prawego obrazu, a filtr ffmpeg tak (`stereo3d=sbsl:sbsr`).

## Zdjęcia 3D (side-by-side / JPS / MPO)

- Zmierzone na KDL-46EX725 i KDL-46HX855: w przeglądarce zdjęć (DLNA lub USB) przycisk 3D oferuje **tylko „konwersję 2D→3D”**. Nie ma opcji side-by-side dla zdjęć.
- Standardowy format aparatów 3D, **MPO**, z pendrive'a USB: Sony wymienia go w tabeli zgodności modeli z 2011 roku, a właściciele zgłaszają, że działa. Test w toku.
- Zdjęcia i filmy anaglifowe (okulary czerwono-cyjanowe) można przekonwertować na side-by-side: `tools/bravia_anaglyph.py`.

## Dotyczy modeli

- Przetestowane: **KDL-46EX725** (2011), **KDL-46HX855** (2012)
- Ta sama rodzina płyt: KDL-46EX724, KDL-40HX853, KDL-55HX753
- Problem sygnału 3D (SEI) dotyczy każdego telewizora i projektora, który rozpoznaje 3D ze strumienia wideo (ten sam objaw zgłaszano w telewizorach Samsung).

## Dokumentacja (po angielsku)

- [Przegląd projektu](../../README.md)
- [Sygnał 3D wyjaśniony](../3d-signalling-explainer.md)
- [Badanie: zdjęcia 3D na BRAVIA](../3d-photos-on-bravia.md)
- [Jak powtórzyć to u siebie](../build-your-own-bravia-portal.md)
- [Stare formaty 3D (anaglif, przeplot)](../legacy-3d-formats.md)

---

*Przetłumaczono z angielskiego 18 września 2026. Poprawki od rodzimych użytkowników języka są mile widziane: otwórz issue.*
