# 0002: Matt-Pocock-Skills bleiben lose Skill-Ordner statt Plugin

## Status
Angenommen (2026-07-25)

## Kontext
Die Engineering-Skills von Matt Pocock (`to-tickets`, `to-spec`, `teach`,
`implement`, `tdd`, `grilling`/`grill-me`, `setup-matt-pocock-skills`) lagen
als einzelne, manuell kopierte Ordner unter `claude/skills/`. Matt Pocock
bietet dieselben Skills mittlerweile als installierbares Claude-Code-Plugin
an (`mattpocock/skills`, Marketplace `mattpocock-skills`).

Geprüfte Fragen (Issue #4):

- **Funktionsumfang:** Das Plugin bündelt 22 Skills, darunter die 8 bereits
  importierten sowie 14 weitere (u. a. `triage`, `code-review`,
  `domain-modeling`, `wayfinder`). Voller Funktionsumfang wäre also gegeben.
- **Updates:** `mattpocock/skills` ist ein Drittanbieter-Marketplace. Laut
  Claude-Code-Doku ist Auto-Update dafür **nicht** aktiv (nur bei offiziellen
  Anthropic-Marketplaces) – Updates erfordern weiterhin einen manuellen
  Trigger (`/plugin marketplace update`).
- **Token-Kosten:** Skills laden laut Doku immer lazy (nur Name + description
  im Kontext, voller Body erst bei Aufruf). Das gilt für lose Ordner und
  Plugin-Skills gleichermaßen – die Kosten hängen an der Anzahl installierter
  Skills, nicht am Installationsmechanismus.
- **Architektur:** Dieses Repo symlinkt `claude/skills/` komplett nach
  `~/.claude/skills` – alles git-versioniert, offline verfügbar, über einen
  Klon reproduzierbar. Ein Plugin würde stattdessen über den
  Claude-Code-eigenen Plugin-Manager nach `~/.claude/plugins/...` installiert,
  außerhalb dieses Repos und außerhalb der Git-Historie.
- **Bestandsaufnahme der Kopien:** Ein direkter Diff gegen Upstream zeigte,
  dass die vorhandenen Kopien an mehreren Stellen durch den Copy-Paste-Import
  korrumpiert waren (Em-Dash → Bindestrich, Tabellenausrichtung, ein Tippfehler
  "demoapable"/"demoable"), aber inhaltlich sonst identisch mit Upstream –
  kein verpasstes Upstream-Update, reines Encoding-Problem.

## Entscheidung
Kein Umstieg auf das Plugin. Die Skills bleiben lose, git-versionierte Ordner
unter `claude/skills/`, konsistent mit allen anderen Skills in diesem Repo.

Begründung: Die vermeintlichen Plugin-Vorteile (Aktualität, weniger
Pflegeaufwand) tragen nicht – Updates sind auch beim Plugin ein manueller
Schritt, und die Token-Kosten unterscheiden sich nicht vom aktuellen Ansatz.
Dagegen würde ein Plugin die Skill-Konfiguration aus der Git-Historie und dem
Symlink-Modell dieses Repos herausnehmen, das für alle anderen Konfigurationen
(Emacs, Shell, restliche Skills) gilt.

Umgesetzte Maßnahmen:

- Die 8 bestehenden Skills wurden sauber aus `mattpocock/skills` neu gezogen
  (`curl` statt Copy-Paste), um die Encoding-Korruption zu beheben.
- Zusätzlich importiert: `mp-code-review` (Upstream: `engineering/code-review`).
  Umbenannt, weil `implement` und `tdd` aktiv auf einen `code-review`-Skill
  verweisen, dieser Name aber mit dem eingebauten (kostenpflichtigen)
  `/code-review`-Befehl dieser Umgebung kollidiert. Referenzen in
  `implement/SKILL.md` und `tdd/SKILL.md` zeigen jetzt auf `/mp-code-review`.
- Die übrigen 14 Upstream-Skills wurden bewusst **nicht** mit importiert –
  bedarfsgetrieben wie der Rest des Repos, nicht auf Vorrat.
- Ein On-Demand-Sync-Skript (`claude/scripts/sync-matt-pocock-skills.sh`)
  diffed die importierten Dateien gegen Upstream und zeigt Abweichungen an,
  ohne automatisch zu überschreiben. Kein Scheduling – die Prüfung ist
  niedrigprioritäre Wartung, kein zeitkritischer Vorgang.

## Konsequenzen
- Skill-Updates von Matt Pocock werden nicht automatisch übernommen; sie
  bleiben so lange unbemerkt, bis `sync-matt-pocock-skills.sh` manuell
  ausgeführt wird.
- Neue relevante Skills aus dem Upstream-Bundle (z. B. `triage`,
  `code-review`) müssen bei Bedarf einzeln nachgezogen werden, inklusive
  Prüfung auf Namenskollisionen mit eingebauten Befehlen.
- Die Skill-Konfiguration bleibt vollständig im dotfiles-Repo nachvollziehbar
  und über einen Klon + Symlink reproduzierbar.
