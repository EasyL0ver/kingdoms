# Kingdoms — AI-Driven Simulation (v2)
# Script is a dumb state database. AI makes ALL decisions and resolves ALL game logic.
# AI returns structured operations; script applies them and tracks state.
# Usage: .\run-sim-ai.ps1 [-Turns 30] [-Players 3] [-OutFile "simulation-13.md"]

param(
    [string]$ApiKey = "",
    [int]$Turns = 30,
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
        $c = $Piles[$deck][$idx]
        $t = if ($c.Tags.Count -gt 0) { " [$($c.Tags -join '][')]" } else { "" }
        $result += "$($c.Name)$t"
    }
    return $result
}

function CardLabel($c) {
    if (-not $c) { return "?" }
    $t = if ($c.Tags.Count -gt 0) { " [$($c.Tags -join '][')]" } else { "" }
    "$($c.Name)$t"
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
Structured commands the script will execute. Available operations:

  DRAW {deck} {count} {player}        — draw top N from pile, add to player's Domain
  DRAW_DISCARD {deck} {count} {player} — draw top N from pile, add to player's Discard
  TAKE_SEASON {cardname} {player}     — move named card from Season to player's Domain
  TAKE_SEASON_DISCARD {cardname} {player} — move from Season to player's Discard
  TAKE_FIELDS {cardname} {player}     — move named card from Fields to player's Domain
  TAKE_FIELDS_DISCARD {cardname} {player} — move from Fields to player's Discard
  MOVE {player} {cardname} DISCARD    — move card from player's Domain to their Discard
  MOVE {player} {cardname} DOMAIN {other_player} — move card from player's Domain to another's
  MOVE_DISCARD {player} {cardname} DOMAIN — move card from player's Discard to their Domain
  REFILL_SEASON                       — draw 4 from Tree to Season (when Season is empty)
  REFILL_FIELDS {count}               — draw N from Wheat to Fields (caps at 7 total)
  REMOVE_GAME {player} {cardname}     — remove card from game entirely (not to discard)

CRITICAL RULES:
- Drawn cards with Drafted keyword must be resolved immediately (check the card text!)
- When cards are Drafted and say "move to discard", use DRAW_DISCARD not DRAW
- Event chains: if a card triggers an event, check ALL Domains for On {event} cards and resolve them
- [Mob] cards in a Domain fight for the ATTACKER during Brawl, not the owner
- Domain holds max 1 [Culture], 1 [Allegiance], 1 [Religion] — if gaining a second, discard the existing one
- REFILL_SEASON only when Season reaches 0 cards
- REFILL_FIELDS only when Harvest event fires. Fields max is always 7. Use count = (7 minus current Fields count)
- Wheat zone: player takes cards from Fields (NOT the pile), and draws 1 Claw per card taken as tax. Use TAKE_FIELDS for each card, then DRAW claw N for the tax. Reasonable to take 1-3 cards, not all of them.
- Activating Sowing itself is NOT a valid action. Sowing passively grants Wheat access if you have 2+ [Nature]. The action is activating the Wheat zone.
- Play strategically but differently for each player — varied strategies make better playtests
- You know the top cards of each pile — use this to inform decisions but play as if each player doesn't know
- A player does ONE action per turn: take from Season, draw from Claw, activate a card, or activate Wheat zone
- Only cards with "Activate —" text can be activated. Cards with only "On [Event]" or "Drafted" or passive text CANNOT be activated as an action. They trigger automatically when their condition is met.
- Poach has a global hunt limit: only 1 [Hunt] card can work across ALL Domains per round. Each Pasture the activating player has increases this by 1. If the limit is reached, Poach does nothing.

Example output:
**T5 — Bob:** Takes **Harvest** from Season. *Need to refill Fields early while Wheat pile is full.* Harvest is Drafted — triggers Harvest globally. Fields refill from 3 to 7. Alice's Plough responds: On Harvest triggers Feast in Alice's Domain. Alice's Tavern responds: discards Raid [Discontent].

OPS:
TAKE_SEASON_DISCARD Harvest Bob
REFILL_FIELDS 4
MOVE Alice Raid DISCARD
"@
    }
)

# ── Apply operations to game state ──
function ApplyOps($opsText) {
    $lines = $opsText -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -and $_ -ne "OPS:" }

    foreach ($line in $lines) {
        $parts = $line -split '\s+'
        if ($parts.Count -lt 2) { continue }

        try {
            switch ($parts[0]) {
                "DRAW" {
                    $deck = $parts[1].ToLower(); $count = [int]$parts[2]; $player = $parts[3]
                    for ($i = 0; $i -lt $count; $i++) {
                        if ($Ptrs[$deck] -lt $Piles[$deck].Count) {
                            $card = $Piles[$deck][$Ptrs[$deck]]; $Ptrs[$deck]++
                            $null = $Domains[$player].Add($card)
                        }
                    }
                }
                "DRAW_DISCARD" {
                    $deck = $parts[1].ToLower(); $count = [int]$parts[2]; $player = $parts[3]
                    for ($i = 0; $i -lt $count; $i++) {
                        if ($Ptrs[$deck] -lt $Piles[$deck].Count) {
                            $card = $Piles[$deck][$Ptrs[$deck]]; $Ptrs[$deck]++
                            $null = $Discards[$player].Add($card)
                        }
                    }
                }
                "TAKE_SEASON" {
                    $cardName = $parts[1]; $player = $parts[2]
                    $card = $Season | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) { $null = $Season.Remove($card); $null = $Domains[$player].Add($card) }
                }
                "TAKE_SEASON_DISCARD" {
                    $cardName = $parts[1]; $player = $parts[2]
                    $card = $Season | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) { $null = $Season.Remove($card); $null = $Discards[$player].Add($card) }
                }
                "TAKE_FIELDS" {
                    $cardName = $parts[1]; $player = $parts[2]
                    $card = $Fields | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) { $null = $Fields.Remove($card); $null = $Domains[$player].Add($card) }
                }
                "TAKE_FIELDS_DISCARD" {
                    $cardName = $parts[1]; $player = $parts[2]
                    $card = $Fields | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) { $null = $Fields.Remove($card); $null = $Discards[$player].Add($card) }
                }
                "MOVE" {
                    $player = $parts[1]; $cardName = $parts[2]; $dest = $parts[3]
                    $card = $Domains[$player] | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) {
                        $null = $Domains[$player].Remove($card)
                        if ($dest -eq "DISCARD") {
                            $null = $Discards[$player].Add($card)
                        } elseif ($parts.Count -ge 5) {
                            $targetPlayer = $parts[4]
                            $null = $Domains[$targetPlayer].Add($card)
                        }
                    }
                }
                "MOVE_DISCARD" {
                    $player = $parts[1]; $cardName = $parts[2]
                    $card = $Discards[$player] | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) { $null = $Discards[$player].Remove($card); $null = $Domains[$player].Add($card) }
                }
                "REFILL_SEASON" {
                    for ($i = 0; $i -lt 4; $i++) {
                        if ($Ptrs["tree"] -lt $Piles["tree"].Count) {
                            $null = $Season.Add($Piles["tree"][$Ptrs["tree"]])
                            $Ptrs["tree"]++
                        }
                    }
                }
                "REFILL_FIELDS" {
                    $count = [int]$parts[1]
                    for ($i = 0; $i -lt $count; $i++) {
                        if ($Fields.Count -ge 7) { break }
                        if ($Ptrs["wheat"] -lt $Piles["wheat"].Count) {
                            $null = $Fields.Add($Piles["wheat"][$Ptrs["wheat"]])
                            $Ptrs["wheat"]++
                        }
                    }
                }
                "REMOVE_GAME" {
                    $player = $parts[1]; $cardName = $parts[2]
                    $card = $Domains[$player] | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
                    if ($card) { $null = $Domains[$player].Remove($card) }
                }
            }
        } catch {
            Write-Warning "Failed to apply op: $line — $_"
        }
    }
}

# ── Check if any pile is empty (game end) ──
function CheckGameEnd {
    foreach ($deck in @("claw", "tree", "wheat", "coin", "candle")) {
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

    # Apply operations
    if ($opsPart) {
        ApplyOps $opsPart
    }

    # Console output
    $firstLine = ($narrativePart -split "`n")[0]
    if ($firstLine.Length -gt 120) { $firstLine = $firstLine.Substring(0, 120) + "..." }
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

    # Check game end
    $depleted = CheckGameEnd
    if ($depleted) {
        $gameEnded = $true
        Log "### GAME ENDS — $depleted pile depleted!`n"
    }
}

# ── Epilogue ──
Log "---`n"
Log "## Epilogue`n"

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

Log "### Stats"
Log "API calls: $apiCalls | Piles: Claw $(PileLeft 'claw'), Tree $(PileLeft 'tree'), Wheat $(PileLeft 'wheat'), Coin $(PileLeft 'coin'), Candle $(PileLeft 'candle')"

# Write output
$output = $Log -join "`n"
$outPath = if ($OutFile) { $OutFile } else { "$PSScriptRoot\simulation-latest.md" }
$output | Set-Content $outPath -Encoding UTF8
Write-Host "`nSimulation written to $outPath ($apiCalls API calls)" -ForegroundColor Green
