![StremioBox](docs/assets/boot-screen.png)

# StremioBox

**Android 16 voor een Intel NUC met Stremio op je tv.**

[Download](https://github.com/zubSero/StremioBox/releases/tag/r6) · [Installatie](docs/installation.md) · [Changelog](CHANGELOG.md) · [Website](https://zubsero.github.io/StremioBox/) · [English](README.md)

StremioBox is een opstartbaar Android TV-image op basis van Android 16 / LineageOS 23.2. Het bevat een startscherm voor bediening met een afstandsbediening, Stremio TV 1.10.4 en fixes voor Intel-video, HDMI-audio, Bluetooth en ondertitels. De gewone mpv-interface van Stremio, inclusief de afspeelbalk, blijft beschikbaar.

**Deze preview is getest op één configuratie:** Intel NUC10i5FNH, Intel UHD-graphics, Intel AX201 Bluetooth, Homatics B21 en een LG HDR-tv. Andere hardware vraagt aparte tests. Langdurige afspeeltests en de schijfinstaller zijn nog niet gevalideerd; probeer eerst live boot vanaf USB.

## Wat is getest?

| Onderdeel | Resultaat | Beperking |
| --- | --- | --- |
| 4K HEVC Main10 HDR10 | Hardwaredecodering, goede kleuren en HDR-modus op de tv | Korte tests rond 24 fps; geen bevestiging voor 4K60 of andere HDR-formaten |
| HDMI-audio | Hoorbaar geluid voor en na display-standby | Bitstream-passthrough niet bevestigd |
| Homatics B21 | Gewone toetsen werken na reboot zonder opnieuw koppelen | Fysieke powerknop verdient nog een aparte hertest |
| Display-standby | Beeld, geluid en bediening keren terug na Android-slaap/wekcommando's | Android blijft draaien; echte S3-slaap niet getest |
| Ondertitels | Disabled en taal-/audiowissels gecontroleerd met externe SRT | Niet ieder formaat of iedere stream getest |
| Startscherm | Engelse Home 1.1, ook na reboot | Eigen launcher; Android en Stremio hebben hun eigen taalinstellingen |

[Hardwarematrix](docs/hardware.md) · [Testresultaten](docs/testing.md)

## Downloaden

De huidige uitgave heet **Intel NUC Preview — English Home**. Deze bevat de fixes van de eerste publieke image en het Engelse startscherm. De [uitgebreide changelog](CHANGELOG.md) beschrijft elke wijziging en de bijbehorende tests.

1. Download en pak de [downloadhulp](https://github.com/zubSero/StremioBox/releases/download/r6/StremioBox-r6-download-helper.zip) uit.
2. Open een terminal in de uitgepakte map. Met Python 3.10 of nieuwer voer je op Windows `py tools/download.py --output downloads` uit. Op Linux/macOS gebruik je `python3 tools/download.py --output downloads`.
3. Reserveer ongeveer 6 GB vrije ruimte. De hulp downloadt twee delen en controleert de hashes van de delen en de samengestelde ISO.
4. Volg de [installatiegids](docs/installation.md), probeer live boot en koppel daarna je eigen remote en Stremio-account.

Heb je de eerste image met Nederlands Home al geïnstalleerd? De [losse Engelse Home-update](docs/installation.md#update-an-existing-installation) gebruikt dezelfde ondertekening en blijft na reboot actief. De technische downloadcode `r6` blijft in bestandsnamen en links staan.

## Grenzen van deze preview

Dolby Vision, HLG, AV1, VLC/ExoPlayer, 4K60, HDMI-CEC, echte S3-slaap en andere GPU's zijn nog niet bevestigd. De ontwikkelbuild gebruikt permissieve SELinux en geauthenticeerde ADB op poort 5555; gebruik een vertrouwd netwerk. Het gedeelde image bevat geen persoonlijke accounts, privésleutels of Bluetooth-koppelingen.

De verpakte fixes blijven na reboot actief. Nieuwe Stremio-versies moeten opnieuw op compatibiliteit worden gecontroleerd. Er is geen automatisch OS-updatekanaal. Het Engelse image is gemaakt door Home in het geverifieerde basisimage te vervangen; een volledige Android-build vanuit deze publieke repository staat nog open.

**Pull requests zijn welkom.** Iedereen kan het project forken en fixes, hardwareverbeteringen, vertalingen of documentatie insturen. Je kunt meteen een PR openen; wijzigingen worden bekeken voordat ze worden samengevoegd. [Zo draag je bij](CONTRIBUTING.md).

[Problemen oplossen](docs/troubleshooting.md) · [Broncode bouwen](docs/building.md) · [Roadmap](docs/roadmap.md) · [Probleem melden](https://github.com/zubSero/StremioBox/issues/new/choose)

StremioBox is een onafhankelijk communityproject, zonder officiële band met Stremio of LineageOS. [Licenties en credits](THIRD_PARTY_NOTICES.md).
