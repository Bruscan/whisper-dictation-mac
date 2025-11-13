# 🎙️ Voice Dictation för Mac

Röststyrning och diktering för macOS med hjälp av Whisper AI. Fungerar offline och stödjer både svenska och engelska!

## ✨ Funktioner

- **Push-to-talk läge**: Tryck på Option+Space för att börja/stoppa inspelning
- **Live läge**: Kontinuerlig lyssning som transkriberar när du pausar
- **Offline**: Allt körs lokalt på din Mac, ingen internetanslutning behövs
- **Flerspråkigt**: Automatisk språkdetektering för svenska och engelska
- **Snabbt**: Transkriberar på sekunder med lokal AI
- **Integritet**: Ingen data lämnar din dator

## 📋 Krav

- macOS (testat på macOS Sonoma och senare)
- Homebrew
- Python 3
- Ca 500 MB - 3 GB lagringsutrymme (beroende på modell)

## 🚀 Installation

### Automatisk installation (rekommenderat)

```bash
# 1. Klona detta repo
cd ~
git clone https://github.com/DIN-ANVÄNDARNAMN/whisper-dictation-mac.git
cd whisper-dictation-mac

# 2. Kör installationsskriptet
chmod +x install.sh
./install.sh
```

Installationsskriptet kommer att:
- Installera sox (för ljudinspelning)
- Installera pynput (för tangentkontroll)
- Klona och bygga whisper.cpp
- Ladda ner en grundläggande AI-modell

### Manuell installation

<details>
<summary>Klicka för att visa manuella steg</summary>

```bash
# 1. Installera beroenden
brew install sox
pip3 install pynput

# 2. Installera whisper.cpp
cd ~
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp
make

# 3. Ladda ner en modell
bash ./models/download-ggml-model.sh base

# 4. Klona detta repo
cd ~
git clone https://github.com/DIN-ANVÄNDARNAMN/whisper-dictation-mac.git
cd whisper-dictation-mac
chmod +x start-dictation.sh
```
</details>

## 🎯 Användning

### Starta diktering

```bash
cd ~/whisper-dictation-mac
./start-dictation.sh
```

### Tangentkommandon

#### Push-to-talk läge (standard)
- **Option+Space** (⌥ + Space):
  - Tryck en gång för att börja spela in
  - Tryck igen för att stoppa och transkribera
  - Bäst för korta inspelningar (5-30 sekunder)

#### Live läge
- **Command+Option+D** (⌘ + ⌥ + D):
  - Tryck för att aktivera kontinuerlig lyssning
  - Prata naturligt, systemet transkriberar när du pausar
  - Tryck igen för att stänga av live läge
  - Bäst för längre diktering

## 🔐 Behörigheter

Första gången du kör programmet kommer macOS att be om behörigheter:

### 1. Accessibility (Tillgänglighet)
macOS kommer visa en dialogruta om att "Terminal" eller "Python" vill styra datorn.

**Så här godkänner du:**
1. Öppna **Systeminställningar**
2. Gå till **Integritet & Säkerhet** → **Tillgänglighet**
3. Klicka på låset och ange ditt lösenord
4. Aktivera **Terminal** och/eller **Python**

### 2. Mikrofonåtkomst
macOS kommer fråga om mikrofontillgång.

**Så här godkänner du:**
1. Klicka på **OK** när dialogrutan visas
2. Eller gå till **Systeminställningar** → **Integritet & Säkerhet** → **Mikrofon**
3. Aktivera **Terminal**

## 💡 Tips för bästa resultat

- **Optimal inspelningstid**: 5-30 sekunder per inspelning i push-to-talk läge
- **Tala tydligt**: Normal hastighet och tydligt uttal
- **Tyst miljö**: Minska bakgrundsljud för bättre noggrannhet
- **Bra mikrofon**: Använd en extern mikrofon för ännu bättre kvalitet

## 🇸🇪 Bättre svenska med KB-Whisper

För betydligt bättre svensk transkribering kan du installera KB-Whisper, som är tränad på 50 000 timmar svensk audio:

```bash
cd ~/whisper.cpp
bash ./models/download-ggml-model.sh large-v3-turbo-q5_0
```

Denna modell är ca 1.6 GB men ger mycket bättre resultat för svenska!

## 🔧 Anpassa tangentkommandon

Vill du använda andra tangentkommandon? Redigera `voice_dictation.py`:

```python
# Hitta denna sektion längst ner i filen:
with keyboard.GlobalHotKeys({
    '<alt>+<space>': on_activate_push_to_talk,
    '<cmd>+<alt>+d': on_activate_toggle_live
}) as listener:
```

**Exempel på alternativ:**
```python
# Control+Shift+Space
'<ctrl>+<shift>+<space>': on_activate_push_to_talk

# Command+D
'<cmd>+d': on_activate_push_to_talk

# F1
'<f1>': on_activate_push_to_talk
```

**Tillgängliga tangenter:**
- `<ctrl>` - Control
- `<cmd>` - Command (⌘)
- `<alt>` / `<option>` - Option (⌥)
- `<shift>` - Shift (⇧)
- `<space>` - Mellanslag
- `<f1>`, `<f2>`, etc. - Funktionstangenter
- Bokstäver: `'a'`, `'b'`, etc.

## 🚀 Starta automatiskt vid uppstart (valfritt)

Om du vill att diktering ska vara alltid tillgänglig:

### Skapa LaunchAgent

1. Skapa filen `~/Library/LaunchAgents/com.voicedictation.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voicedictation</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/DITT-ANVÄNDARNAMN/whisper-dictation-mac/voice_dictation.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/voice-dictation.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/voice-dictation-error.log</string>
</dict>
</plist>
```

2. Byt ut `DITT-ANVÄNDARNAMN` mot ditt riktiga användarnamn

3. Ladda LaunchAgent:
```bash
launchctl load ~/Library/LaunchAgents/com.voicedictation.plist
```

4. För att ta bort auto-start:
```bash
launchctl unload ~/Library/LaunchAgents/com.voicedictation.plist
```

## 🐛 Felsökning

### "sox not found"
Sox saknas. Installera med:
```bash
brew install sox
```

### "No module named 'pynput'"
Pynput saknas. Installera med:
```bash
pip3 install pynput
```

### Hotkey fungerar inte
1. Kontrollera att du har gett **Tillgänglighet**-behörighet i Systeminställningar
2. Starta om Terminal
3. Kör `./start-dictation.sh` igen

### Inget ljud spelas in
1. Kontrollera mikrofontillgång: **Systeminställningar** → **Integritet & Säkerhet** → **Mikrofon**
2. Testa mikrofonen: `rec test.wav` (tryck Ctrl+C för att stoppa, sedan `play test.wav`)

### Transkriberingen är felaktig
- Försök med kortare inspelningar (5-15 sekunder)
- Prata tydligare och långsammare
- Testa i en tystare miljö
- Uppgradera till en större modell (se nedan)

### "whisper.cpp not found"
Installera whisper.cpp:
```bash
cd ~
git clone https://github.com/ggml-org/whisper.cpp.git
cd whisper.cpp
make
bash ./models/download-ggml-model.sh base
```

## 📊 Modellstorlekar och kvalitet

| Modell | Storlek | Hastighet | Kvalitet | Bäst för |
|--------|---------|-----------|----------|----------|
| base | ~150 MB | Mycket snabb | OK | Snabba tester |
| small | ~500 MB | Snabb | Bra | Daglig användning |
| medium | ~1.5 GB | Medel | Mycket bra | Hög noggrannhet |
| large-v3-turbo-q5_0 | ~1.6 GB | Snabb | Utmärkt | Svenska & engelska |

### Byta modell

```bash
# Ladda ner önskad modell
cd ~/whisper.cpp
bash ./models/download-ggml-model.sh [MODELL]

# Exempel:
bash ./models/download-ggml-model.sh small
bash ./models/download-ggml-model.sh medium
bash ./models/download-ggml-model.sh large-v3-turbo-q5_0
```

Skriptet hittar automatiskt den bästa tillgängliga modellen i denna prioritetsordning:
1. KB-Whisper large (bäst för svenska)
2. Large-v3-turbo
3. Medium
4. Small
5. Base

## 📝 Hur det fungerar

1. **Inspelning**: Sox spelar in ljud från mikrofonen som WAV-fil
2. **Transkribering**: Whisper AI transkriberar ljudet lokalt på din Mac
3. **Textinmatning**: Python's pynput skriver texten där din cursor är

Allt körs lokalt - ingen data lämnar din dator!

## 🤝 Bidra

Pull requests är välkomna! För större ändringar, öppna gärna en issue först.

## 📄 Licens

MIT License - se [LICENSE](LICENSE) för detaljer

## 🙏 Erkännanden

- [whisper.cpp](https://github.com/ggml-org/whisper.cpp) - Effektiv C++ implementation av Whisper
- [OpenAI Whisper](https://github.com/openai/whisper) - Den ursprungliga Whisper-modellen
- [KB-Whisper](https://huggingface.co/KBLab) - Svenskoptimerad Whisper från Kungliga Biblioteket

## 💬 Support

Om du stöter på problem:
1. Kolla [Felsökning](#-felsökning) ovan
2. Sök bland [Issues](https://github.com/DIN-ANVÄNDARNAMN/whisper-dictation-mac/issues)
3. Skapa en ny issue med:
   - Vilken macOS-version du kör
   - Felmeddelanden från terminalen
   - Vad du försökte göra

---

**Lycka till med dikteringen!** 🎉
