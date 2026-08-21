# Portfolio Tracker für Home Assistant

[English](README.md) | [Deutsch](README.de.md)

[![GitHub Release](https://img.shields.io/github/v/release/DjangoToni/home-assistant-portfolio-tracker)](https://github.com/DjangoToni/home-assistant-portfolio-tracker/releases)
[![HACS-Prüfung](https://github.com/DjangoToni/home-assistant-portfolio-tracker/actions/workflows/validate.yml/badge.svg)](https://github.com/DjangoToni/home-assistant-portfolio-tracker/actions/workflows/validate.yml)
[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-yellow.svg)](LICENSE)

Eine benutzerdefinierte Home-Assistant-Integration zur Überwachung von Anlageportfolios, Transaktionen, Marktindizes, beobachteten Assets, Kursalarmen und Portfolio-Performance.

Portfolio Tracker stellt native Home-Assistant-Entitäten und zwei automatisch registrierte Dashboard-Karten bereit. Aktive Assets fließen in die Portfolioberechnung ein. Beobachtete Assets bleiben vollständig von Portfoliowert und Performance getrennt.

## Funktionsumfang

- Aktien, ETFs, Fonds, Kryptowährungen, Währungen, Warrants und weitere Yahoo-Finance-Symbole
- Warrants wahlweise mit Yahoo Finance oder einem vorhandenen numerischen Home-Assistant-Sensor als Kursquelle
- Erweiterte CoinGecko-Marktdaten für Kryptowährungen
- Aktive Positionen und separate Beobachtungsliste
- Obere und untere Kursalarme mit Binärsensoren und dauerhaften Benachrichtigungen
- Bearbeitbares Transaktionsjournal für Käufe, Verkäufe und Anfangsbestände
- Einstandswert, realisierte und unrealisierte Gewinne, Gebühren, Steuern, Gesamtrendite und zeitgewichtete Rendite
- Performancevergleich mit konfigurierbaren Marktindizes
- Detaillierte 30-Tage-Diagramme mit Kursraster, Datums-/Zeitachse und Marktkennzahlen
- Professioneller Performanceverlauf mit täglichem Raster
- Mehrsprachige Oberfläche: Deutsch, Englisch, Französisch und Italienisch
- Robuste Kursaktualisierung, damit das Dashboard bei vorübergehenden Ausfällen verfügbar bleibt

## Installation

### HACS

[![Repository in HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=DjangoToni&repository=home-assistant-portfolio-tracker&category=integration)

1. Öffne **HACS** in Home Assistant.
2. Öffne oben rechts das Menü und wähle **Benutzerdefinierte Repositories**.
3. Füge `https://github.com/DjangoToni/home-assistant-portfolio-tracker` mit der Kategorie **Integration** hinzu.
4. Suche nach **Portfolio Tracker** und wähle **Herunterladen**.
5. Starte Home Assistant neu.
6. Öffne **Einstellungen > Geräte & Dienste > Integration hinzufügen** und suche nach **Portfolio Tracker**.

### Manuelle Installation

1. Kopiere `custom_components/portfolio_tracker` nach `custom_components/portfolio_tracker` im Home-Assistant-Konfigurationsverzeichnis.
2. Starte Home Assistant neu.
3. Füge **Portfolio Tracker** unter **Einstellungen > Geräte & Dienste** hinzu.

## Ersteinrichtung

Bei der Ersteinrichtung werden folgende Angaben abgefragt:

- **Portfolio-Name**: wird für das Portfolio-Gerät und den Dashboard-Titel verwendet.
- **Basiswährung**: Währung für zusammengefasste Werte, beispielsweise `CHF`, `EUR` oder `USD`.
- **Aktualisierungsintervall**: bestimmt, wie oft die Marktdaten aktualisiert werden.

Öffne anschließend beim Integrationseintrag **Konfigurieren**. Die Verwaltung ist in vier Bereiche gegliedert:

- **Assets**: aktive und beobachtete Assets hinzufügen, bearbeiten oder entfernen.
- **Transaktionen**: Käufe, Verkäufe und Anfangsbestände verwalten.
- **Markt & Vergleich**: Marktindizes und Performance-Vergleichsindex festlegen.
- **Allgemeine Einstellungen**: Basiswährung und Aktualisierungsintervall ändern.

Die Dashboard-Karte enthält den Button **Portfolio verwalten**, der direkt zum passenden Portfolio-Tracker-Eintrag führt.

## Assets

### Aktive Positionen

Aktive Positionen beeinflussen Portfoliowert, Aufteilung, Gewinn und Performance. Das Symbol muss der Schreibweise von Yahoo Finance entsprechen, zum Beispiel:

- `NOVN.SW` für Novartis an der SIX
- `AAPL` für Apple
- `BTC-USD` für Bitcoin in USD

Stückzahl und Kaufpreis bei der Erstellung erzeugen eine Anfangstransaktion. Weitere Käufe und Verkäufe werden über das Transaktionsjournal gepflegt. Untere und obere Alarmgrenzen sowie ihr aktueller Status werden direkt in der Tabelle **Aktive Assets** angezeigt.

### Beobachtete Assets

Beobachtete Assets erhalten Kurse, Marktdetails, Verlauf und Alarme, beeinflussen aber niemals die Portfoliowerte. Im Dashboard werden sie in einer separaten Tabelle mit Alarmgrenzen und aktuellem Status angezeigt.

### Warrants

Unter **Konfigurieren > Assets > Warrant hinzufügen** kann ein Warrant als aktive Position oder nur zur Beobachtung angelegt werden. Die Eingabemaske speichert die relevanten Produktdaten: ISIN, WKN, Valorennummer, Emittent, Basiswert, Call/Put-Typ, Ausübungspreis, Bezugsverhältnis und Verfallsdatum. Bis auf Typ, Ausübungspreis, Bezugsverhältnis und Verfallsdatum sind diese Angaben optional.

Es stehen zwei Kursquellen zur Verfügung:

- **Yahoo Finance**: Das exakte Yahoo-Symbol eingeben. Kurswährung und 30-Tage-Verlauf werden automatisch geladen, sofern Yahoo das Produkt bereitstellt.
- **Home-Assistant-Sensor**: Einen vorhandenen Sensor mit numerischem Kurszustand auswählen, eine eindeutige Kurzbezeichnung angeben und die Kurswährung festlegen. Damit lassen sich Broker-Integrationen, REST-, MQTT- und Template-Sensoren verwenden, wenn Yahoo den Warrant nicht kennt.

Das optionale Attribut `previous_close` am externen Kurssensor aktiviert die Tagesveränderung in Prozent. Die Historie eines externen Sensors wird nicht in das 30-Tage-Diagramm oder die professionelle Performanceberechnung übernommen, da Home-Assistant-Sensoren keine einheitliche Schnittstelle für historische Kurse besitzen. Aktueller Wert, Gewinn, Transaktionen, Stammdaten und Alarme stehen vollständig zur Verfügung.

## Transaktionen

Unterstützt werden Anfangsbestand, Kauf und Verkauf. Eine Transaktion kann enthalten:

- Handelsdatum und Stückzahl
- Einzelpreis oder vollständiger Betrag
- Handelswährung und Währung des Marktkurses
- Gebühren und Steuern
- Börse oder Broker
- Optionale Notiz

Portfolio Tracker verhindert Verkäufe, die zu einem historisch negativen Bestand führen würden.

## Kursalarme

Für jedes Asset können eine untere Grenze, eine obere Grenze oder beide Grenzen festgelegt werden. Portfolio Tracker erstellt dafür Binärsensoren und sendet einmalig eine dauerhafte Home-Assistant-Benachrichtigung, sobald eine Grenze aktiv wird. Verlässt der Kurs den Alarmbereich und tritt später erneut ein, kann eine neue Benachrichtigung ausgelöst werden.

## Dashboard-Karten

Die Integration registriert das Frontend-Modul automatisch. Die Karten können über die Kartenauswahl des Home-Assistant-Dashboards hinzugefügt werden.

### Portfolioübersicht

```yaml
type: custom:portfolio-overview-card
entity: sensor.mein_portfolio_wert
view_mode: table
```

Mit `view_mode: overview` wird die Aufteilung stärker hervorgehoben. `view_mode: table` zeigt die detaillierte Tabelle der aktiven Assets.

### Asset-Detailkarte

```yaml
type: custom:portfolio-asset-card
entity: sensor.apple_kurs
```

Zeilen in den Tabellen für aktive und beobachtete Assets lassen sich außerdem direkt zur gleichen Detailansicht aufklappen.

## Datenquellen

- [Yahoo Finance](https://finance.yahoo.com/) liefert Kurse, Wechselkurse, Aktiendetails, Marktindizes und Aktienverläufe.
- [CoinGecko](https://www.coingecko.com/) liefert erweiterte Kryptomarktdaten und Verläufe.
- Vorhandene numerische Home-Assistant-Sensoren können Warrant-Kurse aus einer anderen Integration, einem Broker, REST-Endpunkt, MQTT-Topic oder Template liefern.

Öffentliche Anbieter-Endpunkte können vorübergehend nicht erreichbar oder begrenzt sein. Nach dem ersten erfolgreichen Laden behält Portfolio Tracker die letzten gültigen Daten und versucht es beim nächsten Intervall erneut.

## Fehlerbehebung

### Das Dashboard meldet „Konfigurationsfehler“

1. Prüfe, ob Home Assistant nach Installation oder Aktualisierung neu gestartet wurde.
2. Prüfe unter **Einstellungen > Geräte & Dienste**, ob Portfolio Tracker geladen ist.
3. Lade das Dashboard einmal neu. Die Karten-URL enthält eine Versionskennung gegen veraltete Frontend-Dateien.
4. Prüfe unter **Einstellungen > System > Protokolle** nach `custom_components.portfolio_tracker`.

### Es werden keine Kurse geliefert

Vorübergehende Yahoo-Finance-Ausfälle entfernen keine bestehenden Entitäten. Sobald zuvor Daten geladen wurden, bleiben die letzten erfolgreichen Werte bis zur nächsten erfolgreichen Aktualisierung erhalten.

### Die Integration erscheint nach der HACS-Installation nicht

Starte Home Assistant neu und aktualisiere anschließend den Browser. HACS installiert die Dateien unter `custom_components`; neue benutzerdefinierte Integrationen werden von Home Assistant erst beim Start erkannt.

## Datenschutz und Haftungsausschluss

Symbole, Portfolio-Konfiguration und Transaktionen bleiben im Home-Assistant-Konfigurationseintrag. Für Marktdatenanfragen werden ausschließlich die benötigten Symbole beziehungsweise CoinGecko-IDs an die jeweiligen Anbieter übertragen.

Portfolio Tracker ist ein Informationswerkzeug und keine Finanzberatung. Marktdaten können verzögert, unvollständig oder fehlerhaft sein und dürfen nicht alleinige Grundlage einer Anlageentscheidung sein.

## Support und Entwicklung

- Fehler und Funktionswünsche können über [GitHub Issues](https://github.com/DjangoToni/home-assistant-portfolio-tracker/issues) gemeldet werden.
- Vor Änderungen bitte [CONTRIBUTING.md](CONTRIBUTING.md) lesen.
- Sicherheitshinweise stehen in [SECURITY.md](SECURITY.md).
- Die Versionshistorie steht in [CHANGELOG.md](CHANGELOG.md).

## Lizenz

Veröffentlicht unter der [MIT-Lizenz](LICENSE).
