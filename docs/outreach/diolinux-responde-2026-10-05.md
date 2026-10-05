# Diolinux Responde: the question on stereo 3D, posted 2026-10-05

Diolinux Responde is the question-and-answer series of the Brazilian Linux channel Diolinux (Dionatan Simioni). Daniel posted this question to it on 2026-10-05, in his own words (drafted with Claude, edited by him; the posted text is below, verbatim). It asks the question the whole campaign in this repository starts from, and names the edition that answers it, Sparky Stereo OS, ahead of its release.

> Olá, Dio e equipe.
> Pergunta para o Diolinux Responde.
> Por que o Linux nunca teve um suporte decente a 3D estereoscópico?
> Entre 2010 e 2016 as TVs 3D estavam em toda loja, e o 3D Vision da NVIDIA e o HD3D da AMD rodavam jogos em 3D no Windows.
> No Linux, o kernel sabe ligar os modos 3D do HDMI desde 2013, mas nunca houve um desktop que usasse isso, e praticamente nenhum jogo: nem mesmo players como o mpv e o VLC sabiam interpretar e passar o sinal 3D.
> Foi falta de interesse dos fabricantes, de um padrão aberto, ou de gente com as TVs certas na mão?
> Estou nessa há semanas: uma edição do SparkyLinux com 3D estéreo no sistema inteiro, com correções já aceitas no HandBrake, no MKVToolNix, no mpv e no Universal Media Server.
> Queria ouvir a sua leitura dessa história.

The facts behind the lines, with where they are measured in this repository: the kernel's HDMI 3D modes (Intel since 2013, nouveau complete, AMD and NVIDIA missing) in [hdmi-3d](../upstream/README.md); the players that did not read or pass the 3D signal, and the merges that fixed it (HandBrake [#8100](https://github.com/HandBrake/HandBrake/pull/8100), MKVToolNix [!6311](https://codeberg.org/mbunkus/mkvtoolnix/pulls/6311), mpv [#18490](https://github.com/mpv-player/mpv/pull/18490), Universal Media Server [#6330](https://github.com/UniversalMediaServer/UniversalMediaServer/pull/6330), released in 15.9.0), in [media-stack](../upstream/media-stack/README.md). If the channel answers, the answer is logged here.
