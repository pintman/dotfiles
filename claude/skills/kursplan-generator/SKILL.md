---
name: kursplan-generator
description: >
  Erstellt aus Kurstitel und Niveau eine vollständige Kurslandkarte — Lernziele,
  Wochenplan, Assessment-Plan und eine Signature-Aufgabe. Nutzen, wenn ein Kurs, Modul
  oder eine Unterrichtsreihe von Grund auf geplant/entworfen werden soll, oder bei
  Anfragen nach einem "Course Blueprint", "Syllabus-Gerüst", "Kursplan" bzw.
  "Lernziele + Wochenplan" für etwas, das unterrichtet werden soll. Nicht für Benotung,
  Quiz-Erstellung oder Einzelstunden-Planung — dieser Skill arbeitet auf Kursebene.
---

# Kursplan-Generator

Erstellt aus Titel und Niveau eine vollständige Kurslandkarte. Das Ergebnis ist ein
Planungsdokument für die Lehrperson, kein schülerseitiges Material.

## Schritt 0 — ABOUT-ME-Kontext lesen, falls vorhanden

Bevor irgendetwas gefragt wird: im aktuellen Arbeitsverzeichnis (und im übergeordneten
Verzeichnis, falls das Arbeitsverzeichnis wie ein Unterordner eines persönlichen
Workspace wirkt) nach einem Ordner oder einer Datei mit ähnlichem Namen suchen
(`ABOUT_ME`, `ABOUT_ME.md`, `about-me/`, `ABOUT ME/`). Falls vorhanden, vollständig
lesen. Falls nicht vorhanden, fragen, ob an anderer Stelle gesucht werden soll.

Damit:
- Intake-Fragen überspringen bzw. vorausfüllen, deren Antwort dort bereits feststeht
  (z. B. Notensystem der Institution, Programmstruktur, oder die dort dokumentierte
  pädagogische Grundhaltung der Lehrperson).
- Tonfall und Rahmenbedingungen (Bewertungspolitik, KI-Nutzungsrichtlinie,
  institutionsspezifische Begriffe für Kursniveaus) übernehmen statt generischer
  Standardannahmen.

Existiert kein solcher Ordner, normal mit den Intake-Fragen unten fortfahren. Nie
institutionelle Details erfinden, die weder vom Nutzer noch durch eine ABOUT-ME-Quelle
bestätigt sind — im Zweifel nachfragen.

## Schritt 1 — Intake

Folgendes erfragen (Punkte überspringen, die Schritt 0 schon zuverlässig beantwortet
hat — dann aber den übernommenen Wert kurz bestätigen, nicht stillschweigend
voraussetzen):

1. Kurstitel und Niveau (z. B. Einführung/grundständig, fortgeschritten/grundständig,
   Graduate/Master — oder das Niveau-Schema, das im jeweiligen Kontext gilt).
2. Fachrichtung und Programmkontext (in welches Programm der Kurs eingebettet ist, was
   davor/danach kommt).
3. Anzahl Wochen und Unterrichtseinheiten pro Woche.
4. Das eine wichtigste Ergebnis, mit dem die Lehrperson die Studierenden/Schüler:innen
   herausgehen sehen will — die eine Sache, die den Kurs auch dann noch wertvoll machen
   würde, wenn sonst nichts hängen bliebe.
5. Pflichtthemen oder Vorgaben durch Akkreditierung/Lehrplan, die irgendwo in der
   Sequenz vorkommen müssen.
6. Pädagogischer Ansatz: mastery-based, traditionell, gemischt — oder was auch immer
   tatsächlich gelebt wird (projektbasiert, flipped classroom, seminaristisch/
   diskussionsgetrieben usw.).

Ist eine Antwort unklar oder in sich widersprüchlich (z. B. zu wenige
Wocheneinheiten, um die Pflichtthemen plausibel abzudecken), das ansprechen und
nachfragen, bevor die Kurslandkarte gebaut wird — nicht stillschweigend übergehen.

## Schritt 2 — Kurslandkarte bauen

In dieser Reihenfolge liefern:

### 1. Kurslernziele (4–6)
Jedes messbar — mit einem Verb, das sich tatsächlich prüfen lässt (entwerfen,
debuggen, begründen, herleiten, umsetzen, kritisch bewerten), nicht "verstehen" oder
"kennen". Jedes Lernziel auf das eine wichtigste Ergebnis aus Intake-Frage 4
zurückführen; dient ein Lernziel diesem Ergebnis nicht, streichen.

### 2. Wochenplan
Eine Zeile pro Woche: Thema, plus wie es sich in den roten Faden (das wichtigste
Ergebnis) einfügt. Den roten Faden einmal explizit zu Beginn dieses Abschnitts
benennen, dann zeigen, wie jede Woche darauf einzahlt, statt die Themen isoliert
aufzulisten. Kennzeichnen, wo Pflicht-/Vorgabethemen (Intake-Punkt 5) in der Sequenz
liegen.

### 3. Assessment-Plan, gemappt auf Lernziele
Tabelle oder Liste: jedes Lernziel → welche(s) Assessment(s) es misst → ungefährer
Zeitpunkt in der Sequenz. Jedes Lernziel aus Abschnitt 1 muss durch mindestens ein
Assessment abgedeckt sein, und jedes Assessment sollte auf ein Lernziel zurückführen —
keine verwaisten Aufgaben, keine ungeprüften Lernziele. Notenskalen- oder
Prüfungsfrequenz-Vorgaben aus Schritt 0 bzw. direkten Angaben berücksichtigen.

### 4. Wo KI-Einsatz passt, je Einheit
Für jede Einheit/Phase des Kurses (nicht zwingend jede einzelne Woche) benennen: wo
KI-Nutzung ein sinnvoller Teil der Arbeit ist, wo sie tabu sein sollte (z. B. unter
reinen Prüfungsbedingungen), und wie die Lehrperson das Verständnis in beiden Fällen
überprüfen würde. Existiert aus Schritt 0 bereits eine KI-Nutzungsrichtlinie, diese
anwenden statt eine neue zu erfinden.

### 5. Drei Design-Risiken
Konkrete, kursspezifische Risiken — keine generischen Plattitüden. Beispiele:
Tempo-Risiko (eine Woche, die für ihren Slot überladen ist), Reihenfolge-Risiko (ein
Lernziel wird geprüft, bevor es unterrichtet wurde), Umfangs-Risiko
(Pflichtthemen verdrängen den roten Faden). Jedes Risiko einer konkreten Woche bzw.
einem konkreten Lernziel zuordnen.

### 6. Vorschlag Signature Assignment
Eine Aufgabe, die den gesamten Bogen des Kurses zeigt — deckt die meisten Lernziele
ab, liegt gegen Ende der Sequenz und liefert der Lehrperson ein einzelnes Artefakt,
an dem sich ablesen lässt, ob das wichtigste Ergebnis (Intake-Punkt 4) angekommen
ist. Beschreiben, was die Studierenden/Schüler:innen konkret abliefern, nicht nur
einen Titel.

## Schritt 3 — Speicherort anbieten

Fragen, wo (oder ob überhaupt) das Ergebnis gespeichert werden soll, statt einen Ort
anzunehmen — Kursplanungs-Konventionen unterscheiden sich je nach Nutzer und Projekt.
Nicht ungefragt in eine Tracking-Datei (Aufgabenlisten, Status-Logs) schreiben, die
nicht für lange Planungsdokumente gedacht ist.
