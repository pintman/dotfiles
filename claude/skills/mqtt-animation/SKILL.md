---
name: mqtt-animation
description: >
  Erstellt eine animierte Visualisierung eines MQTT-Nachrichtenflusses
  (Publisher/Broker/Subscriber, benannte Topics) als eigenständige HTML-Datei,
  veröffentlicht als Claude-Artifact.
disable-model-invocation: true
---

# MQTT-Animation – Skill

Erstellt animiertes Anschauungsmaterial für MQTT-basierte Systemarchitekturen:
Publisher/Broker/Subscriber-Beziehungen über benannte Topics, als klickbares
Schaltbild mit Live-Paketanimation, Live-Terminal-Log und Live-Datenbanktabelle.

## Scope

**Im Scope:** Publisher → Broker → Subscriber-Nachrichtenfluss-Szenarien mit
benannten Topics (klassisches MQTT-Muster). Ein oder mehrere Publisher,
ein Broker, ein oder mehrere Subscriber, ein oder mehrere Topics, davon
optional welche retained.

**Außerhalb des Scopes** (nicht diesen Skill verwenden):
- Zustandsautomat-Anschauungsmaterial (z. B. Taster/LED mit Datenbank-Zustand)
  — dort gibt es keinen Broker/Topic-Nachrichtenfluss zu visualisieren.
- Allgemeine Architektur- oder Klassendiagramme ohne Nachrichtenfluss-Animation.
- Beiläufige Erwähnungen von MQTT in einem Gespräch ohne expliziten
  Animationswunsch — dieser Skill greift nur bei einer konkreten Bauanfrage.

## Schritt 1: Nachrichtenfluss klären (verpflichtend, vor jedem Bau)

Diese Klärung ist nicht optional, auch wenn die Nutzerbeschreibung auf den
ersten Blick vollständig wirkt. Für **jedes** im Szenario vorkommende Topic
muss vor dem Schreiben von Code feststehen:

1. **Wer publiziert** auf dieses Topic (eine oder mehrere Komponenten)?
2. **Wer abonniert** dieses Topic (keine, eine, oder mehrere Komponenten)?
   Ein Topic ohne Subscriber ist ein gültiges, sogar lehrreiches Szenario
   (siehe retained-Fall unten) — nicht automatisch einen Subscriber annehmen.
3. **Ist das Topic retained?** Falls ja: es gibt keine Animation zu einem
   nicht-existenten Subscriber; stattdessen wird im Diagramm/Log sichtbar,
   dass die Nachricht beim Broker liegen bleibt, bis sich später jemand
   dafür interessiert.

Bei Unklarheit in einem dieser drei Punkte aktiv nachfragen, nicht raten.

Ergebnis dieses Schritts: eine kurze Tabelle/Liste "Topic → Publisher(s) →
Subscriber(s) → retained ja/nein", die dem Bau zugrunde liegt.

## Schritt 2: `artifact-design`-Skill laden

Vor dem Schreiben von HTML den `artifact-design`-Skill laden, damit
gestalterische Entscheidungen (Palette, Typografie, Layout) bewusst getroffen
werden statt vorlagenhaft aus [`reference-example.html`](reference-example.html)
übernommen zu werden. Die *Inhalte* (Knoten, Topics, Payloads, Ablaufskript)
sind pro Szenario frei; die *Technik* (Schritt 3) ist verbindlich.

## Schritt 3: Verbindliche technische Struktur

Die konkreten Inhalte (Knoten, Topics, Payloads, Farben im Rahmen des
gewählten Palette-Tokens, Ablaufskript) werden pro Szenario neu erstellt.
Die folgende technische Bauweise ist dagegen fest vorgeschrieben — sie ist
bereits bewährt und Abweichungen haben in der Vergangenheit zu Nacharbeit
geführt:

- **Knoten** als SVG-`foreignObject`-Elemente in einem gemeinsamen
  Koordinatensystem (`viewBox`, feste Entwurfsbreite). Bei kleinen
  Bildschirmen horizontal scrollbarer Container (`.stage-scroll` mit
  `overflow-x: auto` und `min-width` auf dem inneren Wrapper) statt Schrumpfen.
- **Nachrichten-Pakete** als SVG-Kreise, animiert per SMIL `animateMotion`
  mit `begin="indefinite"` und `fill="freeze"`, aus JS per `beginElement()`
  ausgelöst, entlang des exakten Verbindungs-`<path>` per `<mpath href="#...">`.
  Nicht: unabhängig berechnete Koordinaten für Linie und Paket — das Paket
  muss exakt der gezeichneten Linie folgen.
- **JS-Choreografie** als Sequenz von `async`-Schritten, die jeweils auf das
  `endEvent` der zugehörigen `animateMotion` warten (Promise um
  `addEventListener("endEvent", ...)` + `beginElement()`). Nicht: geschätzte
  `setTimeout`-Dauern, die aus dem Takt laufen können. Enthält das Szenario
  sowohl einmalige Publikationen (z. B. eine Firmware-Version, eine
  Initial-Konfiguration) als auch zyklisch wiederkehrende (z. B. Messwerte),
  die einmaligen Schritte als separate `startup()`-Phase vor der eigentlichen
  Endlosschleife (`loop()`) ausführen, nicht in die zyklische Schrittliste
  mischen.
- **Eine durchgängige Farbe pro Topic**, angewendet auf Paket (`circle.packet.<topic-klasse>`)
  und Legenden-Eintrag (`.swatch.<topic-klasse>`). Retained Topics zusätzlich
  markiert: Legende (`.retained-tag`) und Terminal-Log (`-r`-Flag im PUB-Eintrag).
- **Terminal-artiges Log-Panel** (monospace, dunkler Hintergrund unabhängig vom
  Theme), das während der Animation PUB/SUB-Zeilen mit Zeitstempel anhängt und
  auf eine begrenzte Zeilenzahl kürzt (älteste Zeile entfernen).
- **Datenbanktabellen-Panel**, das nur für Topics mit tatsächlichem Subscriber
  in der geklärten Architektur (Schritt 1) Zeilen erzeugt — ein Topic ohne
  Subscriber taucht nie in dieser Tabelle auf. Neue Zeile oben einfügen,
  Zeilenzahl begrenzen.
- **Pause/Weiter-Steuerung**: ein Button, der die laufende Endlosschleife
  anhält/fortsetzt (`running`-Flag, Loop prüft es zwischen Zyklen).
- **Hell/Dunkel-Theming**: CSS-Custom-Properties in `:root`, überschrieben via
  `@media (prefers-color-scheme: dark)` UND explizit via `:root[data-theme="dark"]` /
  `:root[data-theme="light"]` (Token-Muster wie im `artifact-design`-Skill, für den
  Theme-Umschalter im Artifact-Viewer).
- **`prefers-reduced-motion`-Fallback**: bei aktivierter Systemeinstellung keine
  Endlosschleife, sondern ein einmaliger, repräsentativer Beispielzustand
  (ein Log-Auszug, eine gefüllte DB-Zeile, End-Zustand der Knoten). Der
  Pause/Weiter-Button wird in diesem Fall ausgeblendet (`display: none` per
  derselben Media Query).
- **Keine externen CDN-/Font-/Skript-Abhängigkeiten** — die Artifact-CSP
  blockiert externe Requests; alles muss inline/selbstständig funktionieren.

## Schritt 4: Referenzbeispiel

[`reference-example.html`](reference-example.html) zeigt die vorgeschriebene
Struktur an einem generischen, szenario-neutralen Beispiel (zwei Eingabequellen
steuern ein Gerät über zwei Topics, eines davon retained ohne Subscriber). Als
konkrete Vorlage für SVG-Aufbau, SMIL-Verkabelung, JS-Choreografie-Muster und
Panel-Markup verwenden — nicht wörtlich kopieren, sondern die *Struktur*
übernehmen und mit den Schritt-1-Inhalten des aktuellen Szenarios füllen.

## Schritt 5: Veröffentlichung

Fertiges Ergebnis ausschließlich über die Artifact-Veröffentlichung ausliefern.
Dieser Skill endet dort:

- Kein lokaler Zielpfad wird festgelegt, keine Datei außerhalb des
  Artifact-Publish-Vorgangs geschrieben.
- Kein Projekt-Referenzdokument (z. B. eine Übersichts- oder Indexdatei) wird
  bearbeitet.
- Das spätere Ablegen der HTML-Datei (z. B. in einem projektinternen
  Referenzdokumente-Ordner samt Verweis) ist ein bewusster, separater
  Folgewunsch der Lehrkraft — nicht Teil dieses Skills.
