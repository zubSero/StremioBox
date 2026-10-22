<div align="center">

![StremioBox](docs/assets/boot-screen.png)

# StremioBox

### Maak van een kleine Intel-pc een Stremio-box voor je tv.

**4K HDR · Dolby Digital 5.1 · één afstandsbediening · geen Google-account**

[![Download](https://img.shields.io/github/v/release/zubSero/StremioBox?label=download&style=for-the-badge&color=8b7bff)](https://github.com/zubSero/StremioBox/releases/latest)
[![Website](https://img.shields.io/badge/website-bekijk-65dfc1?style=for-the-badge)](https://zubsero.github.io/StremioBox/)

[**Aan de slag**](#-aan-de-slag) · [**Wat je krijgt**](#-wat-je-krijgt) · [**Vragen**](#-vragen) · [**English**](README.md)

</div>

---

StremioBox is een gratis systeem voor een **Intel NUC** (een pc zo groot als je hand). Sluit hem aan op je tv, neem de afstandsbediening en je komt meteen op een eenvoudig startscherm met **Stremio** — geen bureaublad, geen eindeloze accounts, geen reclame.

![Het StremioBox-startscherm op een tv](docs/assets/home-r7-app-stores.png)

## ✨ Wat je krijgt

| | |
| --- | --- |
| 🎬 **Films in 4K HDR** | Vloeiend 4K met echte HDR op je tv, via de eigen videochip van de pc. |
| 🔊 **Echt surroundgeluid** | Dolby Digital 5.1 naar je soundbar of receiver, zodat de dialoog verstaanbaar blijft. Stereo-tv's werken ook. |
| 🎮 **Eén afstandsbediening** | Koppel een Bluetooth-afstandsbediening één keer; ze blijft werken na herstarten en standby. |
| 💬 **Ondertitels die meewerken** | Uitzetten, van taal of audiospoor wisselen — de ondertitels volgen. |
| 🌙 **Wordt betrouwbaar wakker** | Standby en wakker worden zoals bij een gewone tv-box; beeld en geluid komen terug. |
| 🛒 **Meer apps als je wilt** | Aurora Store en Flicky zitten erin om andere apps te installeren. |
| 🧩 **NuvioTV, als je dat liever hebt** | Optioneel: installeer NuvioTV en StremioBox geeft het HDR en neemt je Stremio-addons over. [Hoe (Engels)](docs/nuvio.md) |
| 🛟 **Een vangnet** | Een optioneel noodsysteem laat je de box herstellen als Android ooit niet meer opstart. [Hoe (Engels)](docs/rescue.md) |

## 🤔 Is dit iets voor mij?

StremioBox past bij je als:

- ✅ je een **Intel NUC** hebt (of wilt kopen) — getest op de **NUC10i5FNH**
- ✅ je al **Stremio** gebruikt of er een aparte box voor wilt
- ✅ je het niet erg vindt om één keer vanaf een **USB-stick** te installeren

Goed om te weten:

- Er is tot nu toe **één** opstelling getest (Intel NUC10i5FNH, LG-tv, Homatics B21-afstandsbediening). Andere pc's kunnen werken, maar niemand heeft het al gecontroleerd — [laat het weten](https://github.com/zubSero/StremioBox/issues/new/choose) als je het probeert!
- Het is een gemeenschapsproject, geen commercieel product. Probeer het eerst vanaf USB; installeren op de schijf kan, maar is nog niet volledig getest.
- Diensten die gecertificeerde Android-toestellen eisen (zoals Netflix) zijn hier niet het doel.

## 🚀 Aan de slag

1. **Download** de [downloadhulp](https://github.com/zubSero/StremioBox/releases/download/r9/StremioBox-r9-native-download.zip) en pak hem uit.
2. **Start hem.** Op Windows dubbelklik je op `Download-StremioBox.cmd`. Op Mac of Linux voer je in die map `bash tools/download.sh --output downloads` uit. Hij haalt het image op (ongeveer 2,9 GB) en controleert dat het volledig en ongewijzigd is. Houd zo'n 6 GB vrij.
3. **Zet het op een USB-stick** met bijvoorbeeld [balenaEtcher](https://etcher.balena.io/) of Rufus, steek hem in de NUC en start vanaf USB. → [Stap-voor-stap installatiegids (Engels)](docs/installation.md)
4. **Koppel je afstandsbediening, log in bij Stremio** met je eigen account en kijk. 🍿

> **Tip voor surroundgeluid:** zet de digitale audio-uitgang van je tv op **Auto** of **Passthrough**, zodat je soundbar Dolby Digital krijgt.

## 🆕 Nieuw

**Surround Sound & NuvioTV** — de eerste uitgave die we iedereen aanraden:

- 🔊 Echte **5.1 Dolby Digital** via je tv naar de soundbar — geen verdronken dialoog meer.
- 🔁 **Het geluid komt vanzelf terug** als de tv van ingang wisselde en het geluid kwijt was.
- ⏱️ De **audio/ondertitel-sync** in Stremio werkt zonder dat het beeld bevriest.
- 🧩 Optioneel **NuvioTV** met HDR.

[Alle wijzigingen bekijken (Engels) →](CHANGELOG.md)

## ❓ Vragen

<details>
<summary><b>Moet ik iets van Linux of Android kennen?</b></summary>

Nee. Downloaden, op USB zetten, vanaf USB starten, afstandsbediening gebruiken. Alleen de optionele extra's (NuvioTV instellen, een oudere installatie bijwerken) gebruiken een commando op je computer, en de gidsen tonen precies wat je moet typen.
</details>

<details>
<summary><b>Welke afstandsbediening werkt?</b></summary>

Getest met de Homatics B21 (Bluetooth). De meeste Bluetooth-afstandsbedieningen en USB-toetsenborden zouden moeten werken; een toetsenbord is handig bij de eerste installatie.
</details>

<details>
<summary><b>Ik heb al een oudere StremioBox. Moet ik opnieuw installeren?</b></summary>

Voor het nieuwe geluid en NuvioTV wel — die zitten in het systeem. Kleinere dingen kunnen soms zonder herinstallatie. [Updatemogelijkheden (Engels)](docs/installation.md#update-an-existing-installation)
</details>

<details>
<summary><b>Geen geluid, of mijn soundbar toont alleen stereo?</b></summary>

Zet de digitale audio-uitgang van je tv op Auto/Passthrough en gebruik de nieuwste uitgave. Meer oplossingen in de [probleemgids (Engels)](docs/troubleshooting.md).
</details>

<details>
<summary><b>Ik heb geen USB-stick.</b></summary>

Er zijn een paar andere manieren, elk met hun beperkingen. [Installeren zonder USB (Engels)](docs/without-usb.md)
</details>

<details>
<summary><b>Is het veilig?</b></summary>

Het image bevat geen accounts, sleutels of persoonlijke gegevens — je stelt alles zelf in. Het is een build in ontwikkelaarsstijl, dus houd hem op je thuisnetwerk. [Beveiliging (Engels)](SECURITY.md)
</details>

## 🤝 Hulp en gemeenschap

- 🐛 Werkt iets niet? [Meld een probleem](https://github.com/zubSero/StremioBox/issues/new/choose)
- 💬 Een vraag? [Discussions](https://github.com/zubSero/StremioBox/discussions)
- 🛠️ Helpen? Pull requests zijn welkom — fixes, andere hardware, vertalingen, documentatie. [Zo draag je bij](CONTRIBUTING.md)

---

<details>
<summary><b>🔧 Voor de technisch nieuwsgierigen</b></summary>

StremioBox is een opstartbaar Android TV-image op basis van **Android 16 / LineageOS 23.2** met Stremio TV 1.10.4, een startscherm voor de afstandsbediening en fixes voor Intel-HDR-video (HEVC Main10, HDR10), HDMI-audio (AC-3-bitstream in de audio-HAL), Bluetooth, display-standby en ondertitels. Afspelen gebeurt via de eigen mpv-interface van Stremio.

[Hardware](docs/hardware.md) · [Testresultaten](docs/testing.md) · [Architectuur](docs/architecture.md) · [Platformpatches](platform/README.md) · [Bouwen](docs/building.md) · [Changelog](CHANGELOG.md) · [Roadmap](docs/roadmap.md)

**Huidig image:** `StremioBox-Android16-r9-nuc10_tv.iso`, 2.886.336.512 bytes, SHA-256 `06267691ec264d0233d6c34c4d32740fc9df393bcb55bd3b717ee103fa0eef1e` · [manifest](releases/r9.json). De technische downloadcode is `r9`.

</details>

## 📜 Credits en licentie

Gebouwd op [LineageOS](https://lineageos.org/), [los-tv-x86](https://github.com/los-tv-x86/lineage_bass_android), [Android-x86](https://www.android-x86.org/), [Mesa](https://www.mesa3d.org/), [drm_hwcomposer](https://gitlab.freedesktop.org/drm-hwcomposer/drm-hwcomposer), Intels mediastack en de Android Generic / AAROPA-gemeenschap. Stremio, mpv en NuvioTV houden hun eigen licenties.

Onze eigen tools, documentatie, artwork en het startscherm vallen onder MIT; platformwijzigingen houden hun oorspronkelijke licenties. [Licentie](LICENSE) · [Licenties van derden](THIRD_PARTY_NOTICES.md)

StremioBox is een onafhankelijk gemeenschapsproject, niet verbonden aan Stremio, LineageOS, Nuvio of Dolby.
