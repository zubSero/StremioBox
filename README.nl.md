![StremioBox](docs/assets/boot-screen.png)

# StremioBox

**Android 16 voor een Intel NUC met Stremio op je tv.**

[Download](https://github.com/zubSero/StremioBox/releases/tag/r7) · [Installatie](docs/installation.md) · [Changelog](CHANGELOG.md) · [Website](https://zubsero.github.io/StremioBox/) · [English](README.md)

StremioBox is een opstartbaar Android TV-image op basis van Android 16 / LineageOS 23.2. Het bevat een startscherm voor bediening met een afstandsbediening, Stremio TV 1.10.4 en fixes voor Intel-video, HDMI-audio, Bluetooth en ondertitels. De gewone mpv-interface van Stremio, inclusief de afspeelbalk, blijft beschikbaar.

![StremioBox Home op de fysieke Intel NUC, met Aurora Store en Flicky onder Apps & settings](docs/assets/home-r7-app-stores.png)

**Deze preview is getest op één configuratie:** Intel NUC10i5FNH, Intel UHD-graphics, Intel AX201 Bluetooth, Homatics B21 en een LG HDR-tv. Andere hardware vraagt aparte tests. Langdurige afspeeltests en de schijfinstaller zijn nog niet gevalideerd; probeer eerst live boot vanaf USB.

## Wat is getest?

| Onderdeel | Resultaat | Beperking |
| --- | --- | --- |
| 4K HEVC Main10 HDR10 | Hardwaredecodering, goede kleuren en HDR-modus op de tv | Korte tests rond 24 fps; geen bevestiging voor 4K60 of andere HDR-formaten |
| HDMI-audio | Hoorbaar geluid voor en na display-standby | Bitstream-passthrough niet bevestigd |
| Homatics B21 | Gewone toetsen werken na reboot zonder opnieuw koppelen | Fysieke powerknop verdient nog een aparte hertest |
| Display-standby | Beeld, geluid en bediening keren terug na Android-slaap/wekcommando's | Vastloper na lange standby opgelost in r7; fysieke nachttest volgt; echte S3-slaap niet getest |
| Ondertitels | Disabled en taal-/audiowissels gecontroleerd met externe SRT | Niet ieder formaat of iedere stream getest |
| Startscherm | Engelse Home 1.1, ook na reboot | Eigen launcher; Android en Stremio hebben hun eigen taalinstellingen |
| Appwinkels | Aurora Store en Flicky openen vanuit Home en blijven na reboot | Volledige appinstallatie via elke winkel nog te testen; geen Google Play-diensten |

[Hardwarematrix](docs/hardware.md) · [Testresultaten](docs/testing.md)

## Nieuw in deze uitgave — Standby & App Stores

- **Geen vastloper meer na lange standby.** De box kon na uren standby of een HDMI-wissel zwart blijven met Geen signaal. De gecorrigeerde compositor zit nu in het image.
- **Aurora Store en Flicky** staan onder **Apps & settings**, zodat je andere apps kunt installeren. Stremio blijft de hoofdknop. [Apps](docs/standby-and-apps.md)
- **Geen scrollende consoletekst** meer op de tv tijdens standby.
- **Optioneel noodsysteem:** een item in het opstartmenu dat een klein Linux-systeem vanaf de EFI-partitie start als Android niet meer opstart. SSH werkt alleen met je eigen sleutel. [Handleiding (Engels)](docs/rescue.md)

De fysieke NUC draait dezelfde gewijzigde bestanden, maar de nachttest in standby en een herinstallatie met de nieuwe ISO staan nog open. [Testgrenzen](docs/testing.md#standby-and-app-stores-release)

## Downloaden

De huidige uitgave heet **Intel NUC Preview — Standby & App Stores**. Deze bevat alle eerdere fixes, het Engelse startscherm, de standby-fix en beide appwinkels. De [uitgebreide changelog](CHANGELOG.md) beschrijft elke wijziging en de bijbehorende tests.

1. Download en pak de [downloadhulp](https://github.com/zubSero/StremioBox/releases/download/r7/StremioBox-r7-native-download.zip) uit.
2. **Windows:** dubbelklik op `Download-StremioBox.cmd`. **Linux/macOS:** open een terminal in de uitgepakte map en voer `bash tools/download.sh --output downloads` uit. Python is niet nodig.
3. Reserveer ongeveer 6 GB vrije ruimte. De hulp downloadt twee delen en controleert de hashes van de delen en de samengestelde ISO.
4. Volg de [installatiegids](docs/installation.md), probeer live boot en koppel daarna je eigen remote en Stremio-account.

Draai je al r5 of r6? Installeer de winkels via ADB; voor de standby-fix is een herinstallatie met r7 nodig. [Updatemogelijkheden](docs/installation.md#update-an-existing-installation).

Heb je de eerste image met Nederlands Home al geïnstalleerd? De [losse Engelse Home-update](docs/installation.md#update-an-existing-installation) gebruikt dezelfde ondertekening en blijft na reboot actief. De technische downloadcode van deze uitgave is `r7`.

## Grenzen van deze preview

Dolby Vision, HLG, AV1, VLC/ExoPlayer, 4K60, HDMI-CEC, echte S3-slaap en andere GPU's zijn nog niet bevestigd. De ontwikkelbuild gebruikt permissieve SELinux en geauthenticeerde ADB op poort 5555; gebruik een vertrouwd netwerk. Het gedeelde image bevat geen persoonlijke accounts, privésleutels of Bluetooth-koppelingen.

De verpakte fixes blijven na reboot actief. Nieuwe Stremio-versies moeten opnieuw op compatibiliteit worden gecontroleerd. Er is geen automatisch OS-updatekanaal. Elke uitgave na de eerste is gemaakt met een vastgelegde, gecontroleerde wijziging van het vorige image; een volledige Android-build vanuit deze publieke repository staat nog open.

**Pull requests zijn welkom.** Iedereen kan het project forken en fixes, hardwareverbeteringen, vertalingen of documentatie insturen. Je kunt meteen een PR openen; wijzigingen worden bekeken voordat ze worden samengevoegd. [Zo draag je bij](CONTRIBUTING.md).

[Problemen oplossen](docs/troubleshooting.md) · [Noodsysteem](docs/rescue.md) · [Broncode bouwen](docs/building.md) · [Roadmap](docs/roadmap.md) · [Probleem melden](https://github.com/zubSero/StremioBox/issues/new/choose)

StremioBox is een onafhankelijk communityproject, zonder officiële band met Stremio of LineageOS. [Licenties en credits](THIRD_PARTY_NOTICES.md).
