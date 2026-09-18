# BLACKMAMBA INPUT

> **A programmable input system that begins as a keyboard assistant and can grow into its own hardware.**

BLACKMAMBA INPUT is the evolution of this repository from a keyboard diagnostic utility into a local-first, context-aware input platform.

The immediate goal is simple and concrete:

**help the user write better, faster, with less friction.**

The long-term goal is larger:

**turn the keyboard into a programmable, adaptive interface between a person and any machine.**

---

## Current status

This repository already contains a working diagnostic base:

- keyboard event capture with `pynput`
- guided key testing
- automatic key detection
- typing simulation
- Tkinter keyboard visualization
- CSV monitoring/export
- macOS `hidutil` helper scripts for remapping

Those tools remain useful and become the **diagnostics layer** of BLACKMAMBA INPUT.

Everything described below is divided into two categories:

- **Implemented now** — functionality already present in this repository.
- **Roadmap** — planned architecture and product direction.

---

# 1. The product starts with writing

The first version must not try to do everything.

It must first become an excellent writing assistant.

The user begins typing:

```text
pro
```

and immediately receives candidates:

```text
programación
programar
programa
proyecto
proceso
producción
```

Navigation should require no mouse:

- `↑ / ↓` — move through candidates
- `Tab` or `Enter` — accept
- `Esc` — dismiss

The system then grows progressively:

```text
letters
  ↓
word completion
  ↓
next-word prediction
  ↓
compound terms
  ↓
phrase completion
  ↓
sentence completion
  ↓
context-aware response assistance
```

The objective is not to replace writing.

The objective is to **reduce the distance between intention and final text**.

---

# 2. Local-first architecture

The fast path must remain local.

A keystroke should never wait for a remote AI model.

```text
PHYSICAL KEYBOARD
       │
       ▼
INPUT LAYER
       │
       ▼
LOCAL PREDICTOR
       │
       ├── prefix completion
       ├── personal dictionary
       ├── frequency
       ├── recency
       ├── context
       └── acceptance history
       │
       ▼
CANDIDATE UI
       │
       ▼
ACTIVE APPLICATION
```

Remote AI can exist as a secondary worker for heavier transformations, but it must never be required for ordinary typing.

---

# 3. BLACKMAMBA TYPE

BLACKMAMBA TYPE is the writing module inside BLACKMAMBA INPUT.

## Core writing features — roadmap

### L1 — Word completion

Fast local prefix completion.

Example:

```text
pro
```

becomes:

```text
1. proyecto
2. programación
3. programar
4. proceso
```

Candidate ordering is personal and changes with use.

---

### L2 — Next-word prediction

Example:

```text
necesitamos un
```

could suggest:

```text
sistema
motor
modelo
pipeline
prototipo
```

---

### L3 — Compound terms

Example:

```text
realidad
```

could suggest:

```text
realidad aumentada
realidad virtual
realidad mixta
```

---

### L4 — Phrase completion

Example:

```text
quiero hacer una interfaz
```

could suggest:

```text
nativa en Python
para el teclado
que funcione completamente local
```

---

### L5 — Sentence completion

Longer contextual predictions appear only when confidence is high enough.

The system should prefer silence over bad predictions.

---

# 4. Personal ranking engine

Candidates should not be ordered by a generic dictionary alone.

A first scoring model can combine:

```text
score =
    prefix_match
  + personal_frequency
  + recent_frequency
  + current_application
  + previous_word
  + phrase_frequency
  + acceptance_history
  - rejection_history
```

The same prefix can therefore produce different rankings depending on context.

Example:

```text
pro
```

while writing software:

```text
programación
proyecto
proceso
programa
```

while working on music:

```text
producción
proyecto
programación
proceso
```

---

# 5. RAW must never be destroyed

BLACKMAMBA INPUT should distinguish between what the user physically typed and what the system ultimately produced.

Example:

```text
RAW
progrmacion

NORMALIZED
programación

FINAL
programación
```

This makes possible:

- typo analysis
- personalized lessons
- correction quality measurement
- keystroke savings
- prediction accuracy
- recovery of the exact original input

The original signal is evidence.

Do not destroy it.

---

# 6. Writing memory

The system should eventually preserve writing as structured data rather than as one enormous text file.

```text
EVENT
  ↓
TOKEN
  ↓
SENTENCE
  ↓
PARAGRAPH
  ↓
SESSION
  ↓
TOPIC / PROJECT
```

A local store can track:

- timestamp
- physical input
- accepted completion
- normalized text
- application
- session
- topic
- project
- prediction confidence
- accepted/rejected candidate
- typing speed

Suggested storage direction:

- SQLite
- WAL mode
- FTS5 for full-text search
- local indexes
- optional encrypted vault for sensitive history

---

# 7. Analytics

The keyboard should measure its own usefulness.

Planned metrics include:

- words per minute
- characters per second
- words per day
- words per week
- words per month
- session duration
- correction count
- omission rate
- repeated-key errors
- transition errors
- accepted suggestions
- rejected suggestions
- saved keystrokes
- generated characters vs physical keystrokes
- typing speed by application
- typing speed by time of day
- accuracy over time

Example:

```text
Physical keystrokes:      14
Final characters:         22
Saved keystrokes:          8
Suggestions accepted:      2
WPM:                      74
```

---

# 8. Personalized typing lessons

Lessons should emerge from the user's own mistakes.

Instead of generic exercises:

```text
asdf jkl;
```

the system can identify patterns such as:

```text
Most difficult transitions this week:

gr → a
qu → e
ció → n
pr → o
```

Then generate exercises specifically for those patterns.

The keyboard becomes both tool and coach.

---

# 9. Confidence-aware assistance

The system should not interrupt continuously.

A prediction should have confidence.

Conceptually:

```text
●●●●  strong prediction
●●●○  useful suggestion
●●○○  uncertain
●○○○  stay quiet
```

This can later become a subtle **confidence halo** around the active writing area.

A smart input system is not one that constantly speaks.

It is one that knows when it has enough evidence to help.

---

# 10. Context-aware reply assistance

A later stage can read available context from the active application and assist with replies.

Example incoming message:

```text
Could you confirm whether this can be reviewed tomorrow?
```

The user types only:

```text
si mañana
```

The system can offer:

```text
Sí, claro. Mañana lo reviso y te confirmo los siguientes pasos.
```

The essential rule:

## Intent Lock

The system may improve presentation, but it must not invent commitments.

If the user writes:

```text
mañana
```

it must not invent:

```text
mañana a las 8:00
```

If the user writes:

```text
lo reviso
```

it must not claim:

```text
ya lo revisé
```

**Style may change. Meaning may not.**

---

# 11. Multiple languages and dynamic layouts

BLACKMAMBA INPUT should support multiple writing systems and layouts.

Planned capabilities:

- Spanish
- English
- French
- Portuguese
- additional alphabets/layouts
- per-language dictionaries
- per-language prediction
- automatic or manual language switching
- dynamic key remapping
- symbols and Unicode layers

The physical keyboard does not have to represent one permanent layout.

---

# 12. Key Worlds

A key should not be limited to one fixed function.

Example:

```text
A
├── normal typing → a
├── Shift → A
├── CODE mode → snippet / symbol / command
├── MUSIC mode → note / control
├── SSH mode → remote macro
├── SYSTEM mode → operating-system action
└── long press → action menu
```

This concept is called a **Key World**.

Different worlds can completely reinterpret the same physical controls.

Planned worlds:

- TYPE
- CODE
- TERMINAL
- SSH
- MUSIC
- 3D
- SYSTEM
- GAMING
- SYMBOLS
- EMOJI
- REMOTE
- CUSTOM

---

# 13. Programming mode

Programming mode can prioritize:

- `()`
- `[]`
- `{}`
- `<>`
- `=>`
- `::`
- `&&`
- `||`
- snippets
- project-specific commands
- language-specific completions
- terminal shortcuts

The active application and project can influence ranking.

---

# 14. SSH and device awareness

BLACKMAMBA INPUT can eventually understand not only what application is active, but what machine or session the user is controlling.

Example:

```text
DEVICE: Mac mini
APP: Terminal
REMOTE HOST: Raspberry Pi
MODE: SSH / Python
LANGUAGE: EN
```

Then:

```text
system
```

might prioritize:

```text
systemctl
systemctl status
systemctl restart
```

Context becomes operational, not only linguistic.

---

# 15. Universal input

The project should support multiple input sources.

```text
KEYBOARD ─────┐
              │
MOUSE ────────┤
              ▼
TOUCH ───→ INPUT ENGINE
              ▲
VOICE ────────┤
              │
REMOTE ───────┘
```

Text input and command input should remain distinguishable.

Examples:

```text
"mañana revisamos esto"
```

is text.

```text
"abre SSH al servidor de pruebas"
```

can become a proposed command.

---

# 16. Remote keyboard and QR pairing

If a machine has no useful keyboard, another device can become the keyboard.

Concept:

```text
NO KEYBOARD
    ↓
SHOW QR
    ↓
PAIR DEVICE
    ↓
PHONE / TABLET
    ↓
KEYBOARD + TOUCHPAD + VOICE + MACROS
```

Possible transports:

- USB
- Bluetooth
- Wi-Fi LAN
- SSH
- temporary QR-paired session

QR pairing should authorize a session, not become the entire protocol.

---

# 17. Physical control surface

BLACKMAMBA INPUT can outgrow a normal keyboard.

The software can eventually drive a custom physical surface containing:

- mechanical switches
- hot-swappable keys
- RGB
- rotary encoders
- sliders
- potentiometers
- extra buttons
- small displays
- Raspberry Pi
- microcontrollers
- modular side panels

The same hardware changes meaning by mode.

Example:

### MUSIC

```text
Slider 1 → volume
Slider 2 → filter
Knob 1   → reverb
Knob 2   → delay
```

### 3D

```text
Slider 1 → X
Slider 2 → Y
Knob 1   → zoom
Knob 2   → rotation
```

### TYPE

```text
Knob 1   → assistance level
Knob 2   → prediction length
Button A → accept
Button B → undo AI action
```

### SSH

```text
Button A → status
Button B → logs
Button C → restart
Button D → deploy
```

---

# 18. Hardware generated from usage

A long-term principle:

> **The software can become good enough to define the hardware it needs.**

The system can observe usage and identify controls that deserve physical embodiment.

Examples:

```text
"This action is used constantly."
→ it deserves a button.

"These two parameters are adjusted continuously."
→ they deserve encoders or sliders.

"This mode needs six high-frequency actions."
→ it may deserve a dedicated module.
```

Potential generated design artifacts:

- control layout
- key map
- knob/slider assignment
- firmware configuration
- Raspberry Pi bridge configuration
- BOM
- enclosure requirements
- hardware profile

The software does not physically manufacture itself.

It can, however, **specify its own next control surface**.

---

# 19. RGB as information

RGB should not exist only as decoration.

It can become system feedback:

- active mode
- active layer
- device connection
- SSH host/session
- suggestion available
- programmed macro
- music channel
- game profile
- warning state

The keyboard can visually reveal its current function.

---

# 20. Product design direction

BLACKMAMBA INPUT should remain desirable even before the user understands every capability.

Physical editions can eventually include:

- Concept Edition
- Toy Edition
- Creator Edition
- Code Edition
- Studio / Pro Edition
- Mobile / Remote Edition

Design directions may include:

- toy-futurist
- industrial premium
- cyber-lab
- retro-future
- gaming
- aviation-inspired
- musical-instrument inspired
- modular BlackMamba

Core product qualities remain:

- good switches
- satisfying feel
- ergonomics
- RGB
- gaming performance
- strong industrial identity
- modularity
- software intelligence

The objective is simple:

> A user should recognize it from across the room and say:  
> **"That is a Mamba."**

---

# 21. Automation philosophy

BLACKMAMBA INPUT should automate aggressively **without becoming annoying**.

The user should discover useful features by experiencing them.

A good automation pattern:

```text
OBSERVE
   ↓
UNDERSTAND
   ↓
PREPARE
   ↓
SHOW WHEN USEFUL
   ↓
USER ACCEPTS
```

The user should not have to configure twenty settings before the system becomes useful.

The target experience is:

> "I didn't ask it to do that… but it did exactly what I needed."

---

# 22. BLACKMAMBA SHADOW

A secondary roadmap system can maintain two timelines.

```text
MAIN
│
└── real user state

SHADOW
│
└── speculative, reversible work
```

The main timeline remains untouched.

The shadow branch can:

- clean
- organize
- classify
- analyze
- prepare
- render
- generate drafts
- create alternatives

Then validators decide whether the result is worth surfacing.

The core rule:

> **Explore much. Interrupt little. Change nothing irreversible without approval.**

---

# 23. Shadow briefs

When the shadow process finds something useful, it can prepare a concise brief.

Example:

```text
BLACKMAMBA SHADOW

Found:
- 3 improvements

Prepared:
- cleaned structure
- alternate version
- metadata draft

Risk:
- low

Original:
- untouched

Next permission required:
- promote generated result
```

Possible actions:

- VIEW
- APPROVE
- DISCARD
- APPROVE THIS ONCE
- APPROVE THIS ACTION
- DO NOT SUGGEST AGAIN

Approval should always have scope.

A simple "yes" must never imply unlimited permission.

---

# 24. Return Brief

One of the most valuable automation patterns is continuity.

When the user returns after hours or days:

```text
WELCOME BACK

While you were away:
- 3 shadow tasks advanced
- 1 useful improvement found
- 2 decisions remain
- production was not modified

Last active point:
"finish phrase predictor"

Next:
RESUME
```

The system should reduce the mental cost of returning to a project.

The continuity loop becomes:

```text
SHADOW
   ↓
BRIEF
   ↓
RECALL
   ↓
RESUME
```

---

# 25. Creative workers

Creative generation is a secondary process, not the critical typing path.

A paragraph can become input for optional workers:

- SONG
- HOOK
- VERSE
- RAP
- REGGAE
- TRANSLATE
- README
- MESSAGE
- SUMMARY
- TITLE
- IMAGE BRIEF
- HASHTAGS

Example:

```text
paragraph
   ↓
creative worker
   ↓
lyrics
   ↓
cover brief
   ↓
metadata
   ↓
hashtags
   ↓
package ready for external music generation
```

The user should not need to stop writing while this happens.

---

# 26. Security and privacy

A system that can observe typing must be built with explicit privacy boundaries.

Required design principles:

- local-first processing
- visible capture state
- instant pause shortcut
- excluded applications
- excluded fields
- never store password fields
- encrypted history option
- retention controls
- raw/generated distinction
- audit log for autonomous actions
- explicit approval boundaries
- no silent destructive remote actions

Privacy is architecture, not a settings page added later.

---

# 27. macOS architecture direction

The current repository uses `pynput`, which remains useful for:

- diagnostics
- telemetry
- prototyping
- key-event experiments

The final macOS input path should evaluate a native input-method layer rather than depending entirely on simulated keystrokes.

Target separation:

```text
Native input layer
        │
        ▼
Python prediction engine
        │
        ▼
candidate UI
        │
        ▼
application
```

Potential responsibilities:

### Native layer

- composition
- candidate presentation
- active input session
- text commit
- cursor integration

### Python engine

- prediction
- ranking
- memory
- analytics
- lessons
- context
- creative workers

### UI layer

- dashboard
- graphs
- settings
- hardware mapping
- history
- Shadow / Return Brief

No HTTP server is required for the core system.

---

# 28. Proposed repository structure

```text
keyboard_tester/
│
├── diagnostics/
│   ├── guided_test.py
│   ├── monitor.py
│   └── remap/
│
├── engine/
│   ├── tokenizer.py
│   ├── predictor.py
│   ├── ranking.py
│   ├── personal_lexicon.py
│   └── context.py
│
├── memory/
│   ├── store.py
│   ├── segmentation.py
│   └── search.py
│
├── analytics/
│   ├── speed.py
│   ├── errors.py
│   ├── savings.py
│   └── lessons.py
│
├── native/
│   └── macos_input_method/
│
├── worlds/
│   ├── type/
│   ├── code/
│   ├── ssh/
│   ├── music/
│   ├── gaming/
│   └── custom/
│
├── remote/
│   ├── pairing/
│   └── transports/
│
├── hardware/
│   ├── profiles/
│   ├── firmware/
│   └── generated/
│
├── shadow/
│   ├── planner.py
│   ├── validator.py
│   └── brief.py
│
├── ui/
│   ├── overlay/
│   └── dashboard/
│
└── tests/
```

This is a target layout, not the current filesystem.

---

# 29. Development roadmap

## Phase 0 — Preserve and isolate diagnostics

- keep current keyboard tester working
- move diagnostic logic behind stable interfaces
- add tests for key normalization
- define event schema

## Phase 1 — Local writing memory

- SQLite event store
- RAW preservation
- sessions
- tokens
- sentences
- paragraphs
- basic FTS search
- daily / weekly / monthly statistics

## Phase 2 — Prefix completion

Milestone:

```text
pro
↓
programación
programar
proyecto
proceso
```

Requirements:

- local
- fast
- keyboard navigable
- adaptive ranking
- persistent learning

## Phase 3 — Typing analytics

- WPM
- characters/sec
- keystroke savings
- acceptance rate
- error transitions
- heatmaps
- personalized lessons

## Phase 4 — Phrase prediction

- next word
- compound terms
- short phrases
- ghost text
- confidence threshold

## Phase 5 — Native macOS input integration

- candidate UI
- text commit
- cursor-aware positioning
- application compatibility matrix

## Phase 6 — Context

- app-aware ranking
- project-aware ranking
- language profiles
- response assistance
- Intent Lock

## Phase 7 — Key Worlds

- CODE
- SSH
- MUSIC
- SYSTEM
- SYMBOLS
- EMOJI
- custom layers

## Phase 8 — Remote input

- QR pairing
- phone keyboard
- touchpad
- dictation
- LAN transport
- Bluetooth / USB research

## Phase 9 — Physical surface

- sliders
- encoders
- extra keys
- RGB feedback
- Raspberry Pi bridge
- generated hardware profiles

## Phase 10 — Shadow autonomy

- speculative branches
- validators
- Return Brief
- scoped approval
- promotion to main timeline

## Phase 11 — Creative workers

- lyrics
- structured song drafts
- image briefs
- metadata
- hashtags
- external-tool handoff

---

# 30. First serious acceptance test

Before advanced AI, hardware or creative automation, the project must pass one simple test extremely well.

```text
Type:

pro
```

Within an imperceptible interaction delay, show:

```text
proyecto
programación
programar
proceso
```

Then:

```text
↓
TAB
```

produces:

```text
programación
```

The user closes the system.

The next day:

```text
pro
```

and the ranking remembers what the user tends to select.

At the same time, analytics correctly report:

- physical keystrokes
- produced characters
- saved keystrokes
- completion accepted
- typing speed

If this feels excellent, the foundation is correct.

---

# 31. Design doctrine

BLACKMAMBA INPUT follows a few non-negotiable principles.

### 1. Writing comes first

If it does not help the user write, the core product has failed.

### 2. Fast path stays local

No remote model should block ordinary typing.

### 3. RAW is evidence

Never destroy the original input.

### 4. Context changes meaning

The same key, prefix or control may behave differently depending on the active world.

### 5. Complexity stays inside

The system may be sophisticated internally while remaining obvious to use.

### 6. Automation should surprise positively

Do useful reversible work before asking unnecessary questions.

### 7. Permission has scope

Approval for one action is not approval for everything.

### 8. Hardware follows behavior

Physical controls should emerge from demonstrated need.

### 9. The system should grow with the user

Vocabulary, layout, shortcuts, lessons and hardware can all evolve.

### 10. The keyboard is only the beginning

BLACKMAMBA INPUT is an interface system.

---

# 32. Vision

A traditional keyboard maps one key to one symbol.

BLACKMAMBA INPUT maps intention, context, history, hardware and software into the fastest useful action.

It begins by helping complete:

```text
pro
```

It can eventually understand:

- what the user is writing
- where they are writing it
- what machine they are controlling
- which language they are using
- which tools they need
- what they repeatedly do
- which controls deserve physical form
- what can be prepared automatically
- when to stay quiet
- when to ask for permission

The long-term idea can be summarized in one sentence:

> **BLACKMAMBA INPUT is software capable of outgrowing the keyboard that runs it. When software needs more controls, the system defines its own hardware surface.**

---

## Existing quick start

The current diagnostic tools remain available.

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run guided testing:

```bash
python3 main.py guiado
```

Run the current GUI:

```bash
python3 gui.py
```

Monitor events:

```bash
python3 monitor.py --out keyboard_log.csv --duration 60
```

On macOS, Input Monitoring / Accessibility permissions may be required for the existing `pynput` tools.

---

## Project identity

**BLACKMAMBA INPUT**

**TYPE is the first module.**

The immediate mission:

> **Make writing feel augmented.**

The larger mission:

> **Build a universal programmable interface between the user and any machine.**
