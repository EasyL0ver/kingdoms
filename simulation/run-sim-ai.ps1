# Kingdoms — AI-Driven Simulation (v2)
# Script is a dumb state database. AI makes ALL decisions and resolves ALL game logic.
# AI returns structured operations; script applies them and tracks state.
# Usage: .\run-sim-ai.ps1 [-Turns 30] [-Players 3] [-OutFile "simulation-13.md"]

param(
    [string]$ApiKey = "",
    [int]$Turns = 100,
    [int]$Players = 3,
    [string]$OutFile = "",
    [string]$Model = "claude-sonnet-4-20250514"
)

# Load API key from file if not passed
if (-not $ApiKey) {
    $keyFile = "$PSScriptRoot\api-key.txt"
    if (Test-Path $keyFile) {
        $ApiKey = (Get-Content $keyFile -Raw).Trim()
    } else {
        throw "No -ApiKey provided and no api-key.txt found in $PSScriptRoot"
    }
}

$ErrorActionPreference = "Stop"
$PlayerNames = @("Alice", "Bob", "Charlie", "Dave", "Eve")[0..($Players - 1)]

# ── Load and shuffle decks ──
$DeckData = Get-Content "$PSScriptRoot\decks.json" -Raw | ConvertFrom-Json

$Piles = @{}
foreach ($deckName in $DeckData.PSObject.Properties.Name) {
    $cards = [System.Collections.ArrayList]@()
    foreach ($card in $DeckData.$deckName) {
        for ($i = 0; $i -lt $card.count; $i++) {
            $null = $cards.Add([PSCustomObject]@{
                Name = $card.name
                Tags = [string[]]@($card.tags)
                Deck = $deckName
            })
        }
    }
    $Piles[$deckName] = [System.Collections.ArrayList]@($cards | Get-Random -Count $cards.Count)
}

# ── Game state ──
$Ptrs = @{ claw = 0; tree = 0; wheat = 0; coin = 0; candle = 0 }
$Season = [System.Collections.ArrayList]@()
$Fields = [System.Collections.ArrayList]@()
$Domains = @{}
$Discards = @{}

foreach ($p in $PlayerNames) {
    $Domains[$p] = [System.Collections.ArrayList]@()
    $Discards[$p] = [System.Collections.ArrayList]@()
}

$Log = [System.Collections.ArrayList]@()
function Log($msg) { $null = $Log.Add($msg) }

function PileLeft($deck) { return $Piles[$deck].Count - $Ptrs[$deck] }

function PileTop($deck, $n) {
    $result = @()
    for ($i = 0; $i -lt $n; $i++) {
        $idx = $Ptrs[$deck] + $i
        if ($idx -ge $Piles[$deck].Count) { break }
        $result += $Piles[$deck][$idx].Name
    }
    return $result
}

function CardLabel($c) {
    if (-not $c) { return "?" }
    $c.Name
}

# Setup Season (4 from Tree)
for ($i = 0; $i -lt 4; $i++) {
    if ($Ptrs["tree"] -lt $Piles["tree"].Count) {
        $null = $Season.Add($Piles["tree"][$Ptrs["tree"]])
        $Ptrs["tree"]++
    }
}

# Setup Fields (7 from Wheat)
for ($i = 0; $i -lt 7; $i++) {
    if ($Ptrs["wheat"] -lt $Piles["wheat"].Count) {
        $null = $Fields.Add($Piles["wheat"][$Ptrs["wheat"]])
        $Ptrs["wheat"]++
    }
}

# ── Build state snapshot for AI ──
function BuildStatePrompt($currentPlayer, $turnNum) {
    $sb = [System.Text.StringBuilder]::new()
    $null = $sb.AppendLine("TURN $turnNum — $currentPlayer's turn.")
    $null = $sb.AppendLine("")

    foreach ($pl in $PlayerNames) {
        $marker = if ($pl -eq $currentPlayer) { " (ACTIVE)" } else { "" }
        $dom = if ($Domains[$pl].Count -eq 0) { "*(empty)*" } else { ($Domains[$pl] | ForEach-Object { CardLabel $_ }) -join ", " }
        $null = $sb.AppendLine("${pl}${marker} Domain: $dom")
        $disc = ($Discards[$pl] | ForEach-Object { $_.Name }) -join ", "
        if ($disc) { $null = $sb.AppendLine("  Discard: $disc") }
    }

    $null = $sb.AppendLine("")
    $null = $sb.AppendLine("Season: $(($Season | ForEach-Object { CardLabel $_ }) -join ', ')")
    $null = $sb.AppendLine("Fields: $(($Fields | ForEach-Object { CardLabel $_ }) -join ', ')")
    foreach ($deck in @("claw", "tree", "wheat", "coin", "candle")) {
        $left = PileLeft $deck
        $top = (PileTop $deck 3) -join ", "
        if ($left -gt 0) {
            $null = $sb.AppendLine("${deck} pile ($left remaining), top 3: $top")
        } else {
            $null = $sb.AppendLine("${deck} pile: EMPTY")
        }
    }

    return $sb.ToString()
}

# ── Call Claude API ──
function AskClaude($systemBlocks, $userPrompt, $maxTokens) {
    if (-not $maxTokens) { $maxTokens = 800 }
    $body = @{
        model = $Model
        max_tokens = $maxTokens
        system = $systemBlocks
        messages = @(
            @{ role = "user"; content = $userPrompt }
        )
    } | ConvertTo-Json -Depth 5

    $headers = @{
        "x-api-key" = $ApiKey
        "anthropic-version" = "2023-06-01"
        "content-type" = "application/json"
    }

    try {
        for ($attempt = 1; $attempt -le 3; $attempt++) {
            try {
                $resp = Invoke-RestMethod -Uri "https://api.anthropic.com/v1/messages" -Method POST -Headers $headers -Body $body -TimeoutSec 60
                if ($script:showCacheStats) {
                    $u = $resp.usage
                    Write-Host "  cache: created=$($u.cache_creation_input_tokens) read=$($u.cache_read_input_tokens) new=$($u.input_tokens)" -ForegroundColor DarkGray
                    $script:showCacheStats = $false
                }
                return $resp.content[0].text
            } catch {
                $errText = "$_"
                if ($errText -match "rate_limit" -and $attempt -lt 3) {
                    Write-Host "  (rate limited, waiting 15s...)" -ForegroundColor Yellow
                    Start-Sleep -Seconds 15
                } else {
                    throw
                }
            }
        }
    } catch {
        Write-Warning "API call failed: $_"
        return $null
    }
}

$script:showCacheStats = $true

# ── Load full game knowledge into system prompt (cached) ──
$GameRules = Get-Content "$PSScriptRoot\..\game-rules.md" -Raw
$GameCards = Get-Content "$PSScriptRoot\..\game-cards.md" -Raw
$SimGuide  = Get-Content "$PSScriptRoot\simulation-guide.md" -Raw

$GameKnowledge = @"
You are simulating a medieval card game called Kingdoms. Each call is ONE player's turn. You make the active player's decision, resolve all mechanics (events, chains, Drafted effects), and also decide for OTHER players when their cards require a response (e.g. Racketeering forces target to offer a card, Eldership lets defender cancel a Brawl). Play to win — make the best move given the board state.

=== GAME RULES ===
$GameRules

=== ALL CARDS ===
$GameCards

=== SIMULATION GUIDE ===
$SimGuide
"@

$SystemPrompt = @(
    @{
        type = "text"
        text = $GameKnowledge
        cache_control = @{ type = "ephemeral" }
    },
    @{
        type = "text"
        text = @"
=== OUTPUT FORMAT ===
You must return EXACTLY two sections. Nothing else.

SECTION 1 — NARRATIVE (one short paragraph):
Describe what happens this turn in plain English. Include the decision, reasoning (1 sentence), and full resolution of any events/chains. Write as: "**T{n} — {Player}:** {action}. {resolution}. {reasoning in italics}"

SECTION 2 — OPERATIONS (one per line, after a line that says "OPS:"):
Structured commands using PIPE-DELIMITED format. Each field separated by |. Available operations:

  DRAW|{deck}|{count}|{player}                — draw top N from pile to Domain
  DRAW_DISCARD|{deck}|{count}|{player}        — draw top N from pile to Discard
  TAKE_SEASON|{cardname}|{player}             — Season card to Domain
  TAKE_SEASON_DISCARD|{cardname}|{player}     — Season card to Discard
  TAKE_FIELDS|{cardname}|{player}             — Fields card to Domain
  TAKE_FIELDS_DISCARD|{cardname}|{player}     — Fields card to Discard
  MOVE|{player}|{cardname}|DISCARD            — Domain to own Discard
  MOVE|{player}|{cardname}|DOMAIN|{other}     — Domain to another player's Domain
  MOVE_DISCARD|{player}|{cardname}            — own Discard to own Domain
  REFILL_FIELDS|{count}                       — draw N from Wheat to Fields (max 7)
  REMOVE_GAME|{player}|{cardname}             — remove card from game entirely

Card names must match EXACTLY as shown in the state (e.g. "Animal Husbandry" not "Animal"). Do NOT include tags like [Culture] in card names.

CRITICAL RULES:
- Drawn cards with Drafted keyword must be resolved immediately (check the card text!)
- When cards are Drafted and say "move to discard", use DRAW_DISCARD not DRAW
- Event chains: if a card triggers an event, check ALL Domains for On {event} cards and resolve them
- [Mob] cards in a Domain fight for the ATTACKER during Brawl, not the owner
- Domain holds max 1 [Culture], 1 [Allegiance], 1 [Religion] — if gaining a second, discard the existing one
- Season auto-refills when it reaches 0 cards — do NOT emit any refill ops for Season
- REFILL_FIELDS only when Harvest event fires. Fields max is always 7. Use count = (7 minus current Fields count)
- Wheat zone: player takes cards from Fields (NOT the pile), and draws 1 Claw per card taken as tax. Use TAKE_FIELDS for each card, then DRAW claw N for the tax. Reasonable to take 1-3 cards, not all of them.
- Activating Sowing itself is NOT a valid action. Sowing passively grants Wheat access if you have 2+ [Nature]. The action is activating the Wheat zone.
- Play strategically but differently for each player — varied strategies make better playtests
- WIN CONDITIONS: The game ends when any zone is fully depleted (pile empty AND face-up cards gone for Tree/Wheat). Tree depleted → most [Nature] wins. Claw depleted → most [Trophy] wins. Wheat depleted → most [Amenity] wins. Players should pursue tags matching their strategy and race/block pile depletion accordingly.
- STRATEGY HEURISTICS:
  - Early game: acquire cards that give you winning tags AND useful abilities — don't grab dead tags
  - Mid game: commit to a win axis. If you're ahead on [Nature], accelerate Tree depletion. If ahead on [Trophy], race Claw.
  - Track who's winning each axis. The player with the most of a winning tag is the biggest threat if that pile depletes — attack them with Brawl/Racketeering/Incite to strip their key cards
  - If you can't win the current race, slow it down (stop drawing from that pile) and pivot to a different axis
  - Depleting a pile is a deliberate choice — don't accidentally end the game when you're behind
- You know the top cards of each pile — use this to inform decisions but play as if each player doesn't know
- A player does ONE action per turn: take from Season, draw from Claw, activate a card, or activate Wheat zone
- Only cards with "Activate —" text can be activated. Cards with only "On [Event]" or "Drafted" or passive text CANNOT be activated as an action. They trigger automatically when their condition is met.
- EVENT RESOLUTION: When an event fires (Rite, Brawl, Feast, Harvest, Rumour), scan ALL Domains for "On [Event]" cards and resolve them. If NO cards respond, the event does NOTHING — no state changes, no OPS. Do NOT repeatedly trigger events with no responders — it wastes turns. Choose a different action instead.
- Events that produce state changes MUST have corresponding OPS. If an event has no responders and no state changes, the activation was pointless.
- Poach has a global hunt limit: only 1 [Hunt] card can work across ALL Domains per round. Each Pasture the activating player has increases this by 1. If the limit is reached, Poach does nothing.

Example output:
**T5 — Bob:** Takes **Harvest** from Season. *Need to refill Fields early while Wheat pile is full.* Harvest is Drafted — triggers Harvest globally. Fields refill from 3 to 7. Alice's Plough responds: On Harvest triggers Feast in Alice's Domain. Alice's Tavern responds: discards Raid [Discontent].

OPS:
TAKE_SEASON_DISCARD|Harvest|Bob
REFILL_FIELDS|4
MOVE|Alice|Raid|DISCARD
"@
    }
)

# ── Check if player has access to a deck ──
# Claw & Tree: always. Wheat: needs Sowing, Withered Crop, Plough, or Animal Husbandry.
# Coin: needs Mill, Apprenticeship, or Animal Husbandry. Candle: needs Oral Tradition.
# $preOpsSnapshot: optional list of card names player had at start of ops batch
function CheckDeckAccess($deck, $player, $preOpsSnapshot) {
    if ($deck -eq "claw" -or $deck -eq "tree") { return $true }
    $domainNames = @($Domains[$player] | ForEach-Object { $_.Name })
    # Also check pre-ops snapshot (card may have been discarded earlier in same ops batch)
    if ($preOpsSnapshot) { $domainNames = @($domainNames + $preOpsSnapshot) | Select-Object -Unique }
    switch ($deck) {
        "wheat" {
            $gateways = @("Sowing", "Withered Crop", "Plough", "Animal Husbandry")
            foreach ($g in $gateways) { if ($domainNames -contains $g) { return $true } }
            return $false
        }
        "coin" {
            $gateways = @("Mill", "Apprenticeship", "Animal Husbandry", "Ingenuity")
            foreach ($g in $gateways) { if ($domainNames -contains $g) { return $true } }
            # Mill's card text says "draw 1 from Coin" — it IS the access
            return $false
        }
        "candle" {
            return ($domainNames -contains "Oral Tradition")
        }
    }
    return $false
}

# ── Apply operations to game state ──
function ApplyOps($opsText) {
    $violations = [System.Collections.ArrayList]@()
    $applied = [System.Collections.ArrayList]@()
    $script:gameEndedInOps = $null
    # Snapshot each player's domain before ops (for access checks on cards discarded mid-batch)
    $preOps = @{}
    foreach ($pl in $script:PlayerNames) { $preOps[$pl] = @($Domains[$pl] | ForEach-Object { $_.Name }) }
    $lines = $opsText -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -and $_ -ne "OPS:" }

    foreach ($line in $lines) {
        # Pipe-delimited is primary; fall back to space-delimited if no pipes
        if ($line -match '\|') {
            $parts = $line -split '\|' | ForEach-Object { $_.Trim() }
        } else {
            $parts = @($line -split '\s+')
        }
        if ($parts.Count -lt 1) { continue }

        try {
            switch ($parts[0]) {
                "DRAW" {
                    $deck = $parts[1].ToLower(); $count = [int]$parts[2]; $player = $parts[3]
                    if (-not (CheckDeckAccess $deck $player $preOps[$player])) {
                        $null = $violations.Add("ILLEGAL: $player has no gateway for $deck deck")
                    } else {
                        for ($i = 0; $i -lt $count; $i++) {
                            if ($Ptrs[$deck] -lt $Piles[$deck].Count) {
                                $card = $Piles[$deck][$Ptrs[$deck]]; $Ptrs[$deck]++
                                $null = $Domains[$player].Add($card)
                                $null = $applied.Add("✅ DRAW $deck → $($card.Name) → ${player}'s Domain")
                            } else {
                                $null = $violations.Add("ILLEGAL: $deck pile is empty, cannot draw")
                            }
                        }
                    }
                }
                "DRAW_DISCARD" {
                    $deck = $parts[1].ToLower(); $count = [int]$parts[2]; $player = $parts[3]
                    if (-not (CheckDeckAccess $deck $player $preOps[$player])) {
                        $null = $violations.Add("ILLEGAL: $player has no gateway for $deck deck")
                    } else {
                        for ($i = 0; $i -lt $count; $i++) {
                            if ($Ptrs[$deck] -lt $Piles[$deck].Count) {
                                $card = $Piles[$deck][$Ptrs[$deck]]; $Ptrs[$deck]++
                                $null = $Discards[$player].Add($card)
                                $null = $applied.Add("✅ DRAW_DISCARD $deck → $($card.Name) → ${player}'s discard")
                            } else {
                                $null = $violations.Add("ILLEGAL: $deck pile is empty, cannot draw")
                            }
                        }
                    }
                }
                "TAKE_SEASON" {
                    $cardName = $parts[1]; $player = $parts[2]
                    $card = $Season | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) {
                        $null = $Season.Remove($card); $null = $Domains[$player].Add($card)
                        $null = $applied.Add("✅ TAKE_SEASON $cardName → ${player}'s Domain")
                    } else {
                        $avail = ($Season | ForEach-Object { $_.Name }) -join ', '
                        $null = $violations.Add("ILLEGAL: '$cardName' not in Season. Season has: [$avail]")
                    }
                    if ($Season.Count -eq 0) {
                        for ($r = 0; $r -lt 4; $r++) {
                            if ($Ptrs["tree"] -lt $Piles["tree"].Count) {
                                $null = $Season.Add($Piles["tree"][$Ptrs["tree"]])
                                $Ptrs["tree"]++
                            }
                        }
                        if ($Season.Count -gt 0) {
                            $refilled = ($Season | ForEach-Object { $_.Name }) -join ', '
                            $null = $applied.Add("🔄 Season auto-refilled: [$refilled]")
                        }
                    }
                }
                "TAKE_SEASON_DISCARD" {
                    $cardName = $parts[1]; $player = $parts[2]
                    $card = $Season | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) {
                        $null = $Season.Remove($card); $null = $Discards[$player].Add($card)
                        $null = $applied.Add("✅ TAKE_SEASON_DISCARD $cardName → ${player}'s discard")
                    } else {
                        $avail = ($Season | ForEach-Object { $_.Name }) -join ', '
                        $null = $violations.Add("ILLEGAL: '$cardName' not in Season. Season has: [$avail]")
                    }
                    if ($Season.Count -eq 0) {
                        for ($r = 0; $r -lt 4; $r++) {
                            if ($Ptrs["tree"] -lt $Piles["tree"].Count) {
                                $null = $Season.Add($Piles["tree"][$Ptrs["tree"]])
                                $Ptrs["tree"]++
                            }
                        }
                        if ($Season.Count -gt 0) {
                            $refilled = ($Season | ForEach-Object { $_.Name }) -join ', '
                            $null = $applied.Add("🔄 Season auto-refilled: [$refilled]")
                        }
                    }
                }
                "TAKE_FIELDS" {
                    $cardName = $parts[1]; $player = $parts[2]
                    $card = $Fields | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) {
                        $null = $Fields.Remove($card); $null = $Domains[$player].Add($card)
                        $null = $applied.Add("✅ TAKE_FIELDS $cardName → ${player}'s Domain")
                    } else {
                        $avail = ($Fields | ForEach-Object { $_.Name }) -join ', '
                        $null = $violations.Add("ILLEGAL: '$cardName' not in Fields. Fields has: [$avail]")
                    }
                }
                "TAKE_FIELDS_DISCARD" {
                    $cardName = $parts[1]; $player = $parts[2]
                    $card = $Fields | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) {
                        $null = $Fields.Remove($card); $null = $Discards[$player].Add($card)
                        $null = $applied.Add("✅ TAKE_FIELDS_DISCARD $cardName → ${player}'s discard")
                    } else {
                        $avail = ($Fields | ForEach-Object { $_.Name }) -join ', '
                        $null = $violations.Add("ILLEGAL: '$cardName' not in Fields. Fields has: [$avail]")
                    }
                }
                "MOVE" {
                    # MOVE|player|card|DISCARD  or  MOVE|player|card|DOMAIN|target
                    $player = $parts[1]; $cardName = $parts[2]; $dest = $parts[3]
                    $card = $Domains[$player] | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) {
                        $null = $Domains[$player].Remove($card)
                        if ($dest -eq "DISCARD") {
                            $null = $Discards[$player].Add($card)
                            $null = $applied.Add("✅ MOVE $cardName ${player}'s Domain → ${player}'s discard")
                        } elseif ($dest -eq "DOMAIN" -and $parts.Count -ge 5) {
                            $targetPlayer = $parts[4]
                            $null = $Domains[$targetPlayer].Add($card)
                            $null = $applied.Add("✅ MOVE $cardName ${player}'s Domain → ${targetPlayer}'s Domain")
                        }
                    } else {
                        $avail = ($Domains[$player] | ForEach-Object { $_.Name }) -join ', '
                        $null = $violations.Add("ILLEGAL: '$cardName' not in ${player}'s Domain. Has: [$avail]")
                    }
                }
                "MOVE_DISCARD" {
                    # MOVE_DISCARD|player|card
                    $player = $parts[1]; $cardName = $parts[2]
                    $card = $Discards[$player] | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) {
                        $null = $Discards[$player].Remove($card); $null = $Domains[$player].Add($card)
                        $null = $applied.Add("✅ MOVE_DISCARD $cardName ${player}'s discard → ${player}'s Domain")
                    } else {
                        $avail = ($Discards[$player] | ForEach-Object { $_.Name }) -join ', '
                        $null = $violations.Add("ILLEGAL: '$cardName' not in ${player}'s discard. Has: [$avail]")
                    }
                }
                "REFILL_SEASON" {
                    # Ignored — Season auto-refills when emptied by TAKE_SEASON ops
                    $null = $applied.Add("⏭️ REFILL_SEASON ignored — auto-refill handles this")
                }
                "REFILL_FIELDS" {
                    $count = [int]$parts[1]
                    $added = [System.Collections.ArrayList]@()
                    for ($i = 0; $i -lt $count; $i++) {
                        if ($Fields.Count -ge 7) { break }
                        if ($Ptrs["wheat"] -lt $Piles["wheat"].Count) {
                            $c = $Piles["wheat"][$Ptrs["wheat"]]
                            $null = $Fields.Add($c)
                            $null = $added.Add($c.Name)
                            $Ptrs["wheat"]++
                        }
                    }
                    $null = $applied.Add("✅ REFILL_FIELDS +$($added.Count): [$($added -join ', ')]")
                }
                "REMOVE_GAME" {
                    $player = $parts[1]; $cardName = $parts[2]
                    $card = $Domains[$player] | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) {
                        $null = $Domains[$player].Remove($card)
                        $null = $applied.Add("✅ REMOVE_GAME $cardName from ${player}")
                    } else {
                        $null = $violations.Add("ILLEGAL: '$cardName' not in ${player}'s Domain for REMOVE_GAME")
                    }
                }
                default {
                    $null = $violations.Add("UNKNOWN OP: $($parts[0]) — full line: $line")
                }
            }
        } catch {
            $null = $violations.Add("PARSE_ERROR: $line — $_")
        }

        # Check for game end after each op
        $depleted = CheckGameEnd
        if ($depleted) {
            $script:gameEndedInOps = $depleted
            $null = $applied.Add("🏁 GAME OVER — $depleted zone fully depleted!")
            break
        }
    }

    # Log the ops trace
    if ($applied.Count -gt 0 -or $violations.Count -gt 0) {
        Log "<details><summary>📋 Ops Trace ($($applied.Count) applied, $($violations.Count) violations)</summary>`n"
        foreach ($a in $applied) { Log "- $a" }
        foreach ($v in $violations) { Log "- ❌ $v" }
        Log "`n</details>`n"
    }

    return $violations
}

# ── Check if any zone is fully depleted (game end) ──
function CheckGameEnd {
    # Tree is depleted when pile AND Season are both empty
    if ((PileLeft "tree") -eq 0 -and $Season.Count -eq 0) { return "tree" }
    # Wheat is depleted when pile AND Fields are both empty
    if ((PileLeft "wheat") -eq 0 -and $Fields.Count -eq 0) { return "wheat" }
    # Other piles just check the draw pile
    foreach ($deck in @("claw", "coin", "candle")) {
        if ((PileLeft $deck) -eq 0) { return $deck }
    }
    return $null
}

# ── MAIN SIMULATION LOOP ──
Log "# Simulation — AI-Driven (v2)`n"
Log "**Players:** $($PlayerNames -join ', ') ($Players players, $([math]::Ceiling($Turns / $Players)) rounds = $Turns turns)`n"
Log "---`n"

# Log initial state
Log "## Initial State`n"
Log "Season: $(($Season | ForEach-Object { CardLabel $_ }) -join ', ')"
Log "Fields ($($Fields.Count)): $(($Fields | ForEach-Object { $_.Name }) -join ', ')"
Log "Piles: Claw $(PileLeft 'claw'), Tree $(PileLeft 'tree'), Wheat $(PileLeft 'wheat'), Coin $(PileLeft 'coin'), Candle $(PileLeft 'candle')"
Log "`n---`n"

$apiCalls = 0
$roundNum = 0
$gameEnded = $false

for ($t = 1; $t -le $Turns; $t++) {
    if ($gameEnded) { break }

    $pIdx = ($t - 1) % $Players
    $p = $PlayerNames[$pIdx]

    # Round header
    if ($pIdx -eq 0) {
        $roundNum++
        Log "## Round $roundNum (Turns $t`u{2013}$([math]::Min($t + $Players - 1, $Turns)))`n"
    }

    # Build state and ask AI
    $statePrompt = BuildStatePrompt $p $t
    $response = AskClaude $SystemPrompt $statePrompt 800
    $apiCalls++

    if (-not $response) {
        Log "**T$t — ${p}:** *(API failed — skipped)*`n"
        Write-Host "T$t $p -> FAILED" -ForegroundColor Red
        continue
    }

    # Split response into narrative and ops
    $narrativePart = ""
    $opsPart = ""
    if ($response -match '(?s)(.+?)OPS:\s*(.+)') {
        $narrativePart = $Matches[1].Trim()
        $opsPart = $Matches[2].Trim()
    } else {
        $narrativePart = $response.Trim()
    }

    # Log narrative
    Log $narrativePart
    Log ""

    # Log raw OPS for debugging
    if ($opsPart) {
        Log "<details><summary>🎯 Raw OPS</summary>`n"
        Log '```'
        Log $opsPart
        Log '```'
        Log "`n</details>`n"
    }

    # Apply operations and check for violations
    $retryCount = 0
    $maxRetries = 2
    $currentNarrative = $narrativePart
    $currentOps = $opsPart

    while ($true) {
        # Snapshot state before applying (so we can rollback on violation)
        $snapDomains = @{}; $snapDiscards = @{}
        foreach ($pl in $PlayerNames) {
            $snapDomains[$pl] = [System.Collections.ArrayList]@($Domains[$pl])
            $snapDiscards[$pl] = [System.Collections.ArrayList]@($Discards[$pl])
        }
        $snapSeason = [System.Collections.ArrayList]@($Season)
        $snapFields = [System.Collections.ArrayList]@($Fields)
        $snapPtrs = @{}; foreach ($k in $Ptrs.Keys) { $snapPtrs[$k] = $Ptrs[$k] }

        $violations = @()
        if ($currentOps) {
            $violations = @(ApplyOps $currentOps)
        }

        if ($violations.Count -eq 0) {
            break  # Clean apply — keep new state
        }

        # Rollback state
        foreach ($pl in $PlayerNames) {
            $Domains[$pl] = $snapDomains[$pl]
            $Discards[$pl] = $snapDiscards[$pl]
        }
        $Season.Clear(); $Season.AddRange($snapSeason)
        $Fields.Clear(); $Fields.AddRange($snapFields)
        foreach ($k in $snapPtrs.Keys) { $Ptrs[$k] = $snapPtrs[$k] }

        if ($retryCount -ge $maxRetries) {
            Log "> ⚠️ Turn had $($violations.Count) illegal action(s) after $maxRetries retries — turn skipped:`n"
            foreach ($v in $violations) { Log "> $v" }
            Log ""
            Write-Host "  !! $($violations.Count) illegal ops stuck after $maxRetries retries" -ForegroundColor Red
            break
        }

        # Retry: re-prompt AI with violation feedback
        $retryCount++
        $violationFeedback = ($violations -join "`n")
        $retryPrompt = $statePrompt + @"

--- RETRY ($retryCount/$maxRetries) ---
Your previous OPS were rejected because of illegal actions:
$violationFeedback

Re-do this turn. Only reference cards that ACTUALLY EXIST in the zones listed above.
"@
        Write-Host "  !! Retry $retryCount — $($violations.Count) illegal ops: $($violations[0])" -ForegroundColor Yellow
        Log "> 🔄 Retry $retryCount — illegal ops detected:`n"
        foreach ($v in $violations) { Log "> $v" }
        Log ""

        $retryResponse = AskClaude $SystemPrompt $retryPrompt 800
        $apiCalls++

        if (-not $retryResponse) { break }

        if ($retryResponse -match '(?s)(.+?)OPS:\s*(.+)') {
            $currentNarrative = $Matches[1].Trim()
            $currentOps = $Matches[2].Trim()
            Log "> **Retry response:**"
            Log $currentNarrative
            Log ""
        } else {
            break
        }
    }

    # Console output
    $firstLine = ($narrativePart -split "`n")[0]

    Write-Host "T$t $p -> $firstLine" -ForegroundColor Cyan

    # State snapshot every 10 turns
    if ($t % 10 -eq 0) {
        Log "---`n"
        Log "### === STATE AFTER TURN $t ===`n"
        foreach ($pl in $PlayerNames) {
            $dom = if ($Domains[$pl].Count -eq 0) { "*(empty)*" } else { ($Domains[$pl] | ForEach-Object { CardLabel $_ }) -join ", " }
            Log "**$pl** ($($Domains[$pl].Count) cards): $dom"
            $disc = ($Discards[$pl] | ForEach-Object { $_.Name }) -join ", "
            if ($disc) { Log "  Discard: $disc" }
        }
        Log ""
        Log "Season: $(($Season | ForEach-Object { CardLabel $_ }) -join ', ')"
        Log "Fields ($($Fields.Count)): $(($Fields | ForEach-Object { $_.Name }) -join ', ')"
        Log "Piles: Claw $(PileLeft 'claw'), Tree $(PileLeft 'tree'), Wheat $(PileLeft 'wheat'), Coin $(PileLeft 'coin')"
        Log "`n---`n"
    }

    # Check game end (from mid-ops detection or post-turn)
    $depleted = $script:gameEndedInOps
    if (-not $depleted) { $depleted = CheckGameEnd }
    if ($depleted) {
        $gameEnded = $true
        Log "### GAME ENDS — $depleted zone fully depleted!`n"
        Write-Host "GAME OVER — $depleted zone depleted!" -ForegroundColor Magenta
    }
}

# ── Epilogue ──
Log "---`n"
Log "## Epilogue`n"

# Determine winner based on which zone was depleted
$winConditions = @{
    tree   = @{ tag = "Nature";  label = "🌳 Tree depleted — most [Nature] wins" }
    claw   = @{ tag = "Trophy";  label = "🐾 Claw depleted — most [Trophy] wins" }
    wheat  = @{ tag = "Amenity"; label = "🌾 Wheat depleted — most [Amenity] wins" }
}

foreach ($pl in $PlayerNames) {
    $dom = if ($Domains[$pl].Count -eq 0) { "*(empty)*" } else { ($Domains[$pl] | ForEach-Object { CardLabel $_ }) -join ", " }
    Log "**$pl** — $($Domains[$pl].Count) cards"
    Log "  Domain: $dom"
    $tagCounts = @{}
    foreach ($c in $Domains[$pl]) { foreach ($tag in $c.Tags) { $tagCounts[$tag] = ($tagCounts[$tag] ?? 0) + 1 } }
    if ($tagCounts.Count -gt 0) {
        $tagStr = ($tagCounts.GetEnumerator() | Sort-Object Name | ForEach-Object { "[$($_.Name)]`u{00d7}$($_.Value)" }) -join ", "
        Log "  Tags: $tagStr"
    }
    Log ""
}

if ($gameEnded) {
    $depletedZone = $script:gameEndedInOps
    if (-not $depletedZone) { $depletedZone = CheckGameEnd }
    $wc = $winConditions[$depletedZone]
    if ($wc) {
        Log "### Winner`n"
        Log "$($wc.label)`n"
        $winTag = $wc.tag
        $scores = @{}
        foreach ($pl in $PlayerNames) {
            $scores[$pl] = ($Domains[$pl] | ForEach-Object { ($_.Tags | Where-Object { $_ -eq $winTag }).Count } | Measure-Object -Sum).Sum
        }
        $maxScore = ($scores.Values | Measure-Object -Maximum).Maximum
        $winners = @($scores.GetEnumerator() | Where-Object { $_.Value -eq $maxScore } | ForEach-Object { $_.Key })
        foreach ($pl in $PlayerNames) {
            $marker = if ($scores[$pl] -eq $maxScore) { " 👑" } else { "" }
            Log "- **$pl**: $($scores[$pl]) [$winTag]$marker"
        }
        if ($winners.Count -gt 1) {
            Log "`n**Tie between $($winners -join ' and ')!**"
        } else {
            Log "`n**$($winners[0]) wins!**"
        }
        Log ""
    }
}

Log "### Stats"
Log "API calls: $apiCalls | Piles: Claw $(PileLeft 'claw'), Tree $(PileLeft 'tree'), Wheat $(PileLeft 'wheat'), Coin $(PileLeft 'coin'), Candle $(PileLeft 'candle')"

# Write output
$output = $Log -join "`n"
$outPath = if ($OutFile) { $OutFile } else { "$PSScriptRoot\simulation-latest.md" }
$output | Set-Content $outPath -Encoding UTF8
Write-Host "`nSimulation written to $outPath ($apiCalls API calls)" -ForegroundColor Green
