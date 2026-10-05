![StremioBox](docs/assets/boot-screen.png)

# StremioBox

**Je NUC. Je afstandsbediening. Je filmavond.**

Een eigen Android TV-ervaring voor Intel NUC, met StremioBox Home en Stremio als middelpunt. Gebaseerd op Android 16 / LineageOS 23.2, met onze fixes voor Intel-video, HDR10, HDMI-audio, Bluetooth en display-standby.

[Download r5](https://github.com/zubSero/StremioBox/releases/tag/r5) · [Website](https://zubsero.github.io/StremioBox/) · [Uitgebreide README](README.md)

## Wat werkt op onze testopstelling?

- 4K HEVC Main10 rond 24 fps met hardwaredecodering en HDR10 op de LG-tv.
- De gewone mpv-bediening binnen Stremio; geen vervangende externe speler.
- Homatics B21-bediening na een volledige reboot zonder opnieuw koppelen.
- Filmbeeld, geluid en Bluetooth na display-standby.
- Ondertitels uitzetten, ook na wisselen van audiotrack of taal.
- Ons startscherm, bootbeeld en first-boot-installatie van de originele ondertekende Stremio-app.

**r5 is een preview voor specifieke hardware.** Getest op de Intel NUC10i5FNH, Intel UHD / AX201, Homatics B21 en een LG HDR-tv. Andere pc's, alle codecs, Dolby Vision, VLC/Exo, 4K60, echte S3-slaap en HDMI-CEC zijn nog niet bevestigd. De fysieke Homatics-powerknop verdient nog een aparte controle op deze definitieve revisie.

## Downloaden

```powershell
git clone https://github.com/zubSero/StremioBox.git
cd StremioBox
py tools/download.py --output downloads
```

Het script haalt twee delen op en controleert zowel de delen als de samengestelde ISO. Reserveer ongeveer 6 GB vrije ruimte. Lees daarna de [installatie-instructies](docs/installation.md) en probeer eerst live boot; maak een back-up voordat je op schijf installeert.

De fixes zitten in het image en blijven na reboot actief. Nieuwe app- of OS-versies moeten opnieuw getest worden; er is nog geen OTA-kanaal. r5 is een gecontroleerde branding- en launcherwijziging op het gecompileerde r4-platform, geen nieuwe volledige platformbuild.

Deze ontwikkelbuild gebruikt permissieve SELinux en geauthenticeerde ADB op poort 5555. Gebruik een vertrouwd netwerk. De gedeelde ISO bevat geen persoonlijke accounts, Bluetooth-koppelingen of privésleutels.

[Hardware](docs/hardware.md) · [Testresultaten](docs/testing.md) · [Broncode bouwen](docs/building.md) · [Branding](docs/branding.md) · [Roadmap](docs/roadmap.md)

Een onafhankelijk communityproject, zonder officiële band met Stremio of LineageOS. Zie [licenties en credits](THIRD_PARTY_NOTICES.md).
