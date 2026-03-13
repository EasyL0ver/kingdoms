# Kingdoms — Simulation Runner
# Loads decks, shuffles, runs 30 turns with simple AI, outputs compact log.
# Usage: . .\run-sim.ps1

param(
    [int]$Turns = 30,
    [int]$Players = 3,
    [string]$OutFile = ""
)

$PlayerNames = @("Alice", "Bob", "Charlie", "Dave", "Eve")[0..($Players - 1)]

# --- Load and shuffle decks ---
$DeckData = Get-Content "$PSScriptRoot\decks.json" -Raw | ConvertFrom-Json

$Decks = @{}
foreach ($deckName in $DeckData.PSObject.Properties.Name) {
    $cards = @()
    foreach ($card in $DeckData.$deckName) {
        for ($i = 0; $i -lt $card.count; $i++) {
            $cards += [PSCustomObject]@{
                Name = $card.name
                Tags = @($card.tags)
                Deck = $deckName
            }
        }
    }
    $Decks[$deckName] = @($cards | Get-Random -Count $cards.Count)
}

# --- Game state ---
$State = @{
    Piles = @{}
    Season = @()
    Fields = @()
    Wares = @()
    Domains = @{}
    Discards = @{}
    Access = @{}
    SeasonIdx = 0
    ClawPtr = 0
    CoinPtr = 0
    WheatPtr = 0
    TreePtr = 0
    Log = [System.Collections.ArrayList]@()
    TurnNum = 0
}

foreach ($p in $PlayerNames) {
    $State.Domains[$p] = [System.Collections.ArrayList]@()
    $State.Discards[$p] = [System.Collections.ArrayList]@()
    $State.Access[$p] = [System.Collections.ArrayList]@("claw", "tree")
}

# Set up piles
$State.Piles["claw"] = [System.Collections.ArrayList]@($Decks["claw"])
$State.Piles["tree"] = [System.Collections.ArrayList]@($Decks["tree"])
$State.Piles["wheat"] = [System.Collections.ArrayList]@($Decks["wheat"])
$State.Piles["coin"] = [System.Collections.ArrayList]@($Decks["coin"])
$State.Piles["candle"] = [System.Collections.ArrayList]@($Decks["candle"])

$State.ClawPtr = 0
$State.TreePtr = 0
$State.WheatPtr = 0
$State.CoinPtr = 0

function Log($msg) {
    $null = $State.Log.Add($msg)
}

function DrawFromPile($deckName) {
    $pile = $State.Piles[$deckName]
    $ptr = switch ($deckName) {
        "claw" { $State.ClawPtr }
        "tree" { $State.TreePtr }
        "wheat" { $State.WheatPtr }
        "coin" { $State.CoinPtr }
        default { 0 }
    }
    if ($ptr -ge $pile.Count) { return $null }
    $card = $pile[$ptr]
    switch ($deckName) {
        "claw" { $State.ClawPtr++ }
        "tree" { $State.TreePtr++ }
        "wheat" { $State.WheatPtr++ }
        "coin" { $State.CoinPtr++ }
    }
    return $card
}

function PileRemaining($deckName) {
    $pile = $State.Piles[$deckName]
    $ptr = switch ($deckName) {
        "claw" { $State.ClawPtr }
        "tree" { $State.TreePtr }
        "wheat" { $State.WheatPtr }
        "coin" { $State.CoinPtr }
        default { 0 }
    }
    return $pile.Count - $ptr
}

# Set up Season (4 from Tree)
for ($i = 0; $i -lt 4; $i++) {
    $c = DrawFromPile "tree"
    if ($c) { $State.Season += $c }
}

# Set up Fields (7 from Wheat)
for ($i = 0; $i -lt 7; $i++) {
    $c = DrawFromPile "wheat"
    if ($c) { $State.Fields += $c }
}

function CardStr($card) {
    if (-not $card) { return "(none)" }
    $tags = if ($card.Tags.Count -gt 0) { " [$($card.Tags -join '][')]" } else { "" }
    return "**$($card.Name)**$tags"
}

function DomainStr($player) {
    $cards = $State.Domains[$player]
    if ($cards.Count -eq 0) { return "*(empty)*" }
    return ($cards | ForEach-Object { $_.Name }) -join ", "
}

function DiscardStr($player) {
    $cards = $State.Discards[$player]
    if ($cards.Count -eq 0) { return "*(empty)*" }
    return ($cards | ForEach-Object { $_.Name }) -join ", "
}

function HasTag($card, $tag) {
    return $card.Tags -contains $tag
}

function PlayerHasTag($player, $tag) {
    foreach ($c in $State.Domains[$player]) {
        if ($c.Tags -contains $tag) { return $true }
    }
    return $false
}

function CountTag($player, $tag) {
    $count = 0
    foreach ($c in $State.Domains[$player]) {
        if ($c.Tags -contains $tag) { $count++ }
    }
    return $count
}

function HasCardNamed($player, $name) {
    foreach ($c in $State.Domains[$player]) {
        if ($c.Name -eq $name) { return $true }
    }
    return $false
}

function HasDiscardNamed($player, $name) {
    foreach ($c in $State.Discards[$player]) {
        if ($c.Name -eq $name) { return $true }
    }
    return $false
}

function HasWheatAccess($player) {
    # Sowing: 2+ Nature
    if ((HasCardNamed $player "Sowing") -and (CountTag $player "Nature") -ge 2) { return $true }
    # Withered Crop: Harvest in discard
    if ((HasCardNamed $player "Withered Crop") -and (HasDiscardNamed $player "Harvest")) { return $true }
    # Animal Husbandry grants activate Wheat
    if (HasCardNamed $player "Animal Husbandry") { return $true }
    return $false
}

function AddToDomain($player, $card) {
    # Check single-slot limits: Culture, Allegiance
    if (HasTag $card "Culture") {
        $existing = $State.Domains[$player] | Where-Object { $_.Tags -contains "Culture" }
        if ($existing) {
            $null = $State.Domains[$player].Remove($existing)
            $null = $State.Discards[$player].Add($existing)
            Log "  → Replaces existing culture $($existing.Name)"
        }
    }
    if (HasTag $card "Allegiance") {
        $existing = $State.Domains[$player] | Where-Object { $_.Tags -contains "Allegiance" }
        if ($existing) {
            $null = $State.Domains[$player].Remove($existing)
            $null = $State.Discards[$player].Add($existing)
            Log "  → Replaces existing allegiance $($existing.Name)"
        }
    }
    $null = $State.Domains[$player].Add($card)
}

function RemoveFromDomain($player, $cardName) {
    $card = $State.Domains[$player] | Where-Object { $_.Name -eq $cardName } | Select-Object -First 1
    if ($card) {
        $null = $State.Domains[$player].Remove($card)
        return $card
    }
    return $null
}

function DiscardFromDomain($player, $cardName) {
    $card = RemoveFromDomain $player $cardName
    if ($card) { $null = $State.Discards[$player].Add($card) }
    return $card
}

# --- Resolve Drafted effects ---
function ResolveDrafted($player, $card) {
    switch ($card.Name) {
        "Harvest" {
            Log "  → Drafted: triggers **Harvest** globally!"
            # Refill Fields to 7
            while ($State.Fields.Count -lt 7) {
                $c = DrawFromPile "wheat"
                if (-not $c) { break }
                $State.Fields += $c
            }
            Log "  → Fields refilled to $($State.Fields.Count)"
            # On Harvest responses
            foreach ($p in $PlayerNames) {
                foreach ($c in @($State.Domains[$p])) {
                    if ($c.Name -eq "Plough") {
                        Log "  → $p's Plough fires On Harvest → triggers Feast"
                        ResolveFeast $p
                    }
                    if ($c.Name -eq "Solstice") {
                        Log "  → $p's Solstice fires On Harvest"
                    }
                }
            }
            $null = $State.Discards[$player].Add($card)
            return $false  # don't add to domain
        }
        "Gathering" {
            Log "  → Drafted: **Gathering** — chooses Rite locally"
            # Simple: trigger Rite in own domain
            foreach ($c in @($State.Domains[$player])) {
                if ($c.Tags -contains "Spiritual" -and $c.Name -like "Worship*") {
                    Log "  → $($c.Name) responds to Rite"
                }
            }
            $null = $State.Discards[$player].Add($card)
            return $false
        }
        "Uprising" {
            Log "  → Drafted: **Uprising** — Brawl in own Domain, no benefits (spoils discarded)"
            return $true  # stays in domain
        }
        "Incite" {
            # Move up to 3 Mob from own domain to others
            $mobs = @($State.Domains[$player] | Where-Object { $_.Tags -contains "Mob" })
            $moved = 0
            $targets = $PlayerNames | Where-Object { $_ -ne $player }
            foreach ($mob in $mobs) {
                if ($moved -ge 3) { break }
                $target = $targets[$moved % $targets.Count]
                $null = $State.Domains[$player].Remove($mob)
                AddToDomain $target $mob
                Log "  → Incite: moves $($mob.Name) to $target's Domain"
                $moved++
            }
            $null = $State.Discards[$player].Add($card)
            return $false
        }
        "Ingenuity" {
            $coinCard = DrawFromPile "coin"
            if ($coinCard) {
                Log "  → Drafted: draws $(CardStr $coinCard) from Coin"
                if ($coinCard.Name -eq "Rumour") {
                    Log "  → Rumour triggers Rumour globally → to discard"
                    $null = $State.Discards[$player].Add($coinCard)
                } else {
                    $drafted = ResolveDrafted $player $coinCard
                    if ($drafted) { AddToDomain $player $coinCard }
                }
            }
            return $true  # Ingenuity stays
        }
        "Highlander" {
            if (-not (HasCardNamed $player "Crags")) {
                Log "  → Drafted: no Crags → Highlander to discard"
                $null = $State.Discards[$player].Add($card)
                return $false
            }
            return $true
        }
        "Nomad" {
            if (-not (HasCardNamed $player "Pasture")) {
                Log "  → Drafted: no Pasture → Nomad to discard"
                $null = $State.Discards[$player].Add($card)
                return $false
            }
            return $true
        }
        "Regrowth" {
            # Return all Pastures from all discards
            foreach ($p in $PlayerNames) {
                $pastures = @($State.Discards[$p] | Where-Object { $_.Name -eq "Pasture" })
                foreach ($pas in $pastures) {
                    $null = $State.Discards[$p].Remove($pas)
                    AddToDomain $p $pas
                    Log "  → Regrowth returns Pasture to $p"
                }
            }
            $null = $State.Discards[$player].Add($card)
            return $false
        }
        "Feed the Commoners" {
            $discontent = @($State.Domains[$player] | Where-Object { $_.Tags -contains "Discontent" })
            $removed = 0
            foreach ($dc in $discontent) {
                if ($removed -ge 3) { break }
                DiscardFromDomain $player $dc.Name | Out-Null
                Log "  → Feed the Commoners discards $($dc.Name)"
                $removed++
            }
            return $true
        }
        "Plough" {
            if (HasCardNamed $player "Pasture") {
                Log "  → Drafted: discards a Pasture to keep Plough"
                DiscardFromDomain $player "Pasture" | Out-Null
                return $true
            } else {
                Log "  → Drafted: no Pasture → Plough to discard"
                $null = $State.Discards[$player].Add($card)
                return $false
            }
        }
        "Animal Husbandry" {
            if (HasCardNamed $player "Pasture") {
                Log "  → Drafted: discards a Pasture to keep Animal Husbandry"
                DiscardFromDomain $player "Pasture" | Out-Null
                return $true
            } else {
                Log "  → Drafted: no Pasture → AH to discard"
                $null = $State.Discards[$player].Add($card)
                return $false
            }
        }
        "Mine" {
            if (HasCardNamed $player "Crags") {
                Log "  → Drafted: discards a Crags to keep Mine"
                DiscardFromDomain $player "Crags" | Out-Null
                return $true
            } else {
                Log "  → Drafted: no Crags → Mine to discard"
                $null = $State.Discards[$player].Add($card)
                return $false
            }
        }
        "Famine" {
            $targets = $PlayerNames | Where-Object { $_ -ne $player }
            foreach ($t in $targets) {
                $wheat = $State.Domains[$t] | Where-Object { $_.Deck -eq "wheat" } | Select-Object -First 1
                if ($wheat) {
                    DiscardFromDomain $t $wheat.Name | Out-Null
                    Log "  → Famine: $t discards $($wheat.Name)"
                    break
                }
            }
            $null = $State.Discards[$player].Add($card)
            return $false
        }
        "Rumour" {
            Log "  → Drafted: triggers **Rumour** globally → to discard"
            $null = $State.Discards[$player].Add($card)
            return $false
        }
        "Solstice" {
            Log "  → Drafted: returns Pastures from discard"
            foreach ($p in $PlayerNames) {
                $pastures = @($State.Discards[$p] | Where-Object { $_.Name -eq "Pasture" })
                foreach ($pas in $pastures) {
                    $null = $State.Discards[$p].Remove($pas)
                    AddToDomain $p $pas
                    Log "  → Solstice returns Pasture to $p"
                }
            }
            $null = $State.Discards[$player].Add($card)
            return $false
        }
        default {
            return $true  # stays in domain
        }
    }
}

function ResolveFeast($player) {
    Log "  → **Feast** in $player's Domain!"
    foreach ($c in @($State.Domains[$player])) {
        if ($c.Name -eq "Tavern") {
            $dc = $State.Domains[$player] | Where-Object { $_.Tags -contains "Discontent" } | Select-Object -First 1
            if ($dc) {
                DiscardFromDomain $player $dc.Name | Out-Null
                Log "    → Tavern clears $($dc.Name)"
            }
        }
        if ($c.Name -eq "Share the Spoils") {
            $clawCard = DrawFromPile "claw"
            if ($clawCard) {
                AddToDomain $player $clawCard
                Log "    → Share the Spoils draws $(CardStr $clawCard)"
            }
        }
        if ($c.Name -eq "Marauders") {
            DiscardFromDomain $player "Marauders" | Out-Null
            $clawCard = DrawFromPile "claw"
            if ($clawCard) {
                AddToDomain $player $clawCard
                Log "    → Marauders self-destructs, draws $(CardStr $clawCard)"
            }
        }
    }
}

# --- AI Decision Making ---
function ScoreSeasonCard($player, $card) {
    $score = 0
    $turn = $State.TurnNum
    
    # Land cards are high priority early
    if ($card.Tags -contains "Land") {
        $score += 10
        $landCount = CountTag $player "Land"
        if ($landCount -eq 0) { $score += 3 }
        if ($landCount -ge 3) { $score -= 3 }
    }
    # Nature cards help unlock Wheat
    if ($card.Tags -contains "Nature") { $score += 2 }
    # Culture cards
    if ($card.Tags -contains "Culture") {
        if ($card.Name -eq "Nomad" -and (HasCardNamed $player "Pasture")) { $score += 9 }
        elseif ($card.Name -eq "Highlander" -and (HasCardNamed $player "Crags")) { $score += 9 }
        else { $score -= 3 }
    }
    # Wheat gates
    if ($card.Name -eq "Sowing") { 
        if (-not (HasWheatAccess $player)) { $score += 8 } else { $score += 2 }
    }
    if ($card.Name -eq "Withered Crop") {
        if (-not (HasWheatAccess $player)) { $score += 7 } else { $score += 1 }
    }
    # Spiritual cards
    if ($card.Tags -contains "Spiritual") { $score += 5 }
    # Knowledge
    if ($card.Tags -contains "Knowledge") { $score += 3 }
    # Harvest (Drafted trigger)
    if ($card.Name -eq "Harvest") { $score += 6 }
    # Gathering
    if ($card.Name -eq "Gathering") { $score += 4 }
    # Forage
    if ($card.Name -eq "Forage") { $score += 4 }
    
    # Random variance
    $score += (Get-Random -Minimum -2 -Maximum 3)
    return $score
}

function ChooseAction($player) {
    $turn = $State.TurnNum
    $domain = $State.Domains[$player]
    
    # Option 1: Take from Season
    $bestSeasonScore = -100
    $bestSeasonCard = $null
    $bestSeasonIdx = -1
    for ($i = 0; $i -lt $State.Season.Count; $i++) {
        $s = ScoreSeasonCard $player $State.Season[$i]
        if ($s -gt $bestSeasonScore) {
            $bestSeasonScore = $s
            $bestSeasonCard = $State.Season[$i]
            $bestSeasonIdx = $i
        }
    }
    
    # Option 2: Draw from Claw
    $clawScore = 4 + (Get-Random -Minimum -1 -Maximum 2)
    if ($turn -gt 9) { $clawScore += 3 }
    if ($turn -gt 20) { $clawScore += 2 }
    
    # Option 3: Activate a card in Domain
    $bestActivateScore = -100
    $bestActivateCard = $null
    foreach ($c in $domain) {
        $aScore = -100
        switch ($c.Name) {
            "Poach" {
                $huntCount = CountTag $player "Hunt"
                $pastureCount = ($domain | Where-Object { $_.Name -eq "Pasture" }).Count
                $limit = 1 + $pastureCount
                # Check global hunt usage (simplified: just check own)
                if ($huntCount -le $limit) { $aScore = 6 + (Get-Random -Minimum 0 -Maximum 3) }
            }
            "Warband" {
                $others = $PlayerNames | Where-Object { $_ -ne $player }
                $maxDomain = ($others | ForEach-Object { $State.Domains[$_].Count } | Measure-Object -Maximum).Maximum
                if ($maxDomain -gt 3 -and $turn -gt 12) { $aScore = 7 + $maxDomain }
            }
            "Racketeering" {
                if ($turn -gt 15) { $aScore = 7 + (Get-Random -Minimum 0 -Maximum 3) }
            }
            "Sky Dance" { $aScore = 6 + (CountTag $player "Spiritual") }
            "Sacred Grove" { $aScore = 6 + (Get-Random -Minimum 0 -Maximum 3) }
            "Granary" { 
                $onFeast = ($domain | Where-Object { $_.Name -in @("Tavern", "Share the Spoils", "Marauders") }).Count
                $aScore = 5 + $onFeast * 2
            }
            "Mill" { $aScore = 5 + (Get-Random -Minimum 0 -Maximum 2) }
            "Forage" { $aScore = 5 + (Get-Random -Minimum 0 -Maximum 2) }
            "Pathfinding" { $aScore = 4 + (CountTag $player "Knowledge") }
            "Chiefdom" {
                $mobs = CountTag $player "Mob"
                if ($mobs -gt 0 -and $turn -gt 10) { $aScore = 6 }
            }
            "Crags" { $aScore = 3 }
            "Herbalism" { $aScore = 4 }
            "Outriders" { if ($turn -gt 10) { $aScore = 6 } }
            "Land Grab" {
                $landInSeason = ($State.Season | Where-Object { $_.Tags -contains "Land" }).Count
                if ($landInSeason -gt 0) { $aScore = 9 + $landInSeason }
            }
            "Blood Offering" { 
                if ($domain.Count -gt 3) { $aScore = 5 + (CountTag $player "Spiritual") }
            }
            "Militia" {
                $mobs = CountTag $player "Mob"
                if ($mobs -gt 2) { $aScore = 6 }
            }
        }
        if ($aScore -gt $bestActivateScore) {
            $bestActivateScore = $aScore
            $bestActivateCard = $c
        }
    }
    
    # Option 4: Activate Wheat zone
    $wheatScore = -100
    if (HasWheatAccess $player) {
        $wheatScore = 7 + (Get-Random -Minimum 0 -Maximum 3)
        if ($State.Fields.Count -eq 0) { $wheatScore = -100 }
    }
    
    # Pick best
    $options = @(
        @{ Type = "season"; Score = $bestSeasonScore; Data = @{ Card = $bestSeasonCard; Idx = $bestSeasonIdx } }
        @{ Type = "claw"; Score = $clawScore; Data = $null }
        @{ Type = "activate"; Score = $bestActivateScore; Data = $bestActivateCard }
        @{ Type = "wheat"; Score = $wheatScore; Data = $null }
    )
    
    $best = $options | Sort-Object { $_.Score } -Descending | Select-Object -First 1
    
    # Fallback: if Season is empty and nothing good, draw Claw
    if ($best.Type -eq "season" -and $State.Season.Count -eq 0) {
        $best = @{ Type = "claw"; Score = $clawScore; Data = $null }
    }
    
    return $best
}

# --- Main simulation loop ---
Log "# Simulation 12 — Automated Run"
Log ""
Log "**Players:** $($PlayerNames -join ', ') ($Players players, $([math]::Ceiling($Turns / $Players)) rounds = $Turns turns)"
Log ""
Log "---"
Log ""
Log "## Initial State"
Log ""
Log "Season 1: $(($State.Season | ForEach-Object { CardStr $_ }) -join ', ')"
Log "Fields (7): $(($State.Fields | ForEach-Object { $_.Name }) -join ', ')"
Log "Piles: Claw $(PileRemaining 'claw'), Tree $(PileRemaining 'tree'), Wheat $(PileRemaining 'wheat'), Coin $(PileRemaining 'coin')"
Log ""
Log "---"
Log ""

$roundNum = 0
for ($t = 1; $t -le $Turns; $t++) {
    $State.TurnNum = $t
    $playerIdx = ($t - 1) % $Players
    $player = $PlayerNames[$playerIdx]
    
    # Round header
    if (($t - 1) % $Players -eq 0) {
        $roundNum++
        $endTurn = [math]::Min($t + $Players - 1, $Turns)
        Log "## Round $roundNum (Turns $t–$endTurn)"
        Log ""
    }
    
    $action = ChooseAction $player
    
    switch ($action.Type) {
        "season" {
            $card = $action.Data.Card
            $idx = $action.Data.Idx
            $State.Season = @($State.Season | Where-Object { $_ -ne $card })
            
            Log "**T$t — ${player}:** Takes $(CardStr $card) from Season."
            $stays = ResolveDrafted $player $card
            if ($stays) { AddToDomain $player $card }
            
            # Refill Season if empty
            if ($State.Season.Count -eq 0) {
                $newSeason = @()
                for ($s = 0; $s -lt 4; $s++) {
                    $c = DrawFromPile "tree"
                    if ($c) { $newSeason += $c }
                }
                $State.Season = $newSeason
                if ($newSeason.Count -gt 0) {
                    Log "  → Season empty → New Season: $(($newSeason | ForEach-Object { $_.Name }) -join ', ')"
                }
            }
        }
        "claw" {
            $c1 = DrawFromPile "claw"
            $c2 = DrawFromPile "claw"
            $drawn = @($c1, $c2) | Where-Object { $_ }
            
            Log "**T$t — ${player}:** Draws Claw (2): $(($drawn | ForEach-Object { CardStr $_ }) -join ', ')."
            foreach ($card in $drawn) {
                $stays = ResolveDrafted $player $card
                if ($stays) { AddToDomain $player $card }
            }
        }
        "activate" {
            $card = $action.Data
            Log "**T$t — ${player}:** Activates $(CardStr $card)."
            
            switch ($card.Name) {
                "Poach" {
                    Log "  → Triggers Feast in $player's Domain"
                    ResolveFeast $player
                }
                "Warband" {
                    $others = $PlayerNames | Where-Object { $_ -ne $player }
                    $target = $others | Sort-Object { $State.Domains[$_].Count } -Descending | Select-Object -First 1
                    Log "  → Triggers Brawl in $target's Domain ($($State.Domains[$target].Count) cards)"
                    # Mob cards fight for attacker
                    $mobs = @($State.Domains[$target] | Where-Object { $_.Tags -contains "Mob" })
                    foreach ($mob in $mobs) {
                        if ($mob.Name -eq "Raid") {
                            # Defender gives 1 card
                            $nonMob = $State.Domains[$target] | Where-Object { $_.Tags -notcontains "Mob" } | Select-Object -First 1
                            if ($nonMob) {
                                $null = $State.Domains[$target].Remove($nonMob)
                                AddToDomain $player $nonMob
                                Log "    → Raid: $target gives $($nonMob.Name) to $player"
                            }
                        }
                        if ($mob.Name -eq "Scavenge") {
                            $fromDiscard = $State.Discards[$target] | Select-Object -First 1
                            if ($fromDiscard) {
                                $null = $State.Discards[$target].Remove($fromDiscard)
                                AddToDomain $player $fromDiscard
                                Log "    → Scavenge: $player takes $($fromDiscard.Name) from $target's discard"
                            }
                        }
                    }
                    # Foray responds
                    foreach ($c in @($State.Domains[$target])) {
                        if ($c.Name -eq "Foray") {
                            $treeCard = DrawFromPile "tree"
                            if ($treeCard) {
                                AddToDomain $target $treeCard
                                Log "    → Foray: $target draws $($treeCard.Name) from Tree"
                            }
                        }
                    }
                }
                "Racketeering" {
                    $others = $PlayerNames | Where-Object { $_ -ne $player }
                    $target = $others | Get-Random
                    $offered = $State.Domains[$target] | Where-Object { $_.Tags -contains "Discontent" } | Select-Object -First 1
                    if (-not $offered) { $offered = $State.Domains[$target] | Select-Object -First 1 }
                    if ($offered) {
                        $null = $State.Domains[$target].Remove($offered)
                        AddToDomain $player $offered
                        Log "  → $target offers $($offered.Name) — $player takes it"
                    }
                }
                "Sky Dance" {
                    Log "  → Triggers Rite globally"
                    foreach ($p in $PlayerNames) {
                        foreach ($c in @($State.Domains[$p])) {
                            if ($c.Tags -contains "Spiritual" -and $c.Name -like "Worship*") {
                                Log "    → $p's $($c.Name) responds"
                                if ($c.Name -eq "Worship of Fertility") {
                                    Log "    → Triggers Harvest in $player's Domain"
                                    # Mini harvest for triggerer
                                }
                                if ($c.Name -eq "Worship of the Rain" -and $State.Season.Count -gt 0) {
                                    $replaced = $State.Season[0]
                                    $newCard = DrawFromPile "tree"
                                    if ($newCard) {
                                        $State.Season[0] = $newCard
                                        Log "    → Swaps $($replaced.Name) in Season for $($newCard.Name)"
                                    }
                                }
                                if ($c.Name -eq "Worship of War") {
                                    Log "    → $player may Brawl any Domain (skipped for brevity)"
                                }
                            }
                        }
                    }
                }
                "Granary" {
                    DiscardFromDomain $player "Granary" | Out-Null
                    Log "  → Discards Granary, triggers Feast"
                    ResolveFeast $player
                }
                "Mill" {
                    DiscardFromDomain $player "Mill" | Out-Null
                    $coinCard = DrawFromPile "coin"
                    if ($coinCard) {
                        Log "  → Discards Mill, draws $(CardStr $coinCard) from Coin"
                        $stays = ResolveDrafted $player $coinCard
                        if ($stays) { AddToDomain $player $coinCard }
                    }
                }
                "Forage" {
                    $top3 = @()
                    for ($f = 0; $f -lt 3; $f++) {
                        $c = DrawFromPile "tree"
                        if ($c) { $top3 += $c }
                    }
                    $best = $top3 | Sort-Object { ScoreSeasonCard $player $_ } -Descending | Select-Object -First 1
                    foreach ($c in $top3) {
                        if ($c -eq $best) { continue }
                        $null = $State.Discards[$player].Add($c)
                    }
                    if ($best) {
                        AddToDomain $player $best
                        DiscardFromDomain $player "Forage" | Out-Null
                        Log "  → Top 3: $(($top3 | ForEach-Object { $_.Name }) -join ', '). Takes $($best.Name), discards Forage."
                    }
                }
                "Pathfinding" {
                    $n = CountTag $player "Knowledge"
                    $drawn = @()
                    for ($k = 0; $k -lt $n; $k++) {
                        $c = DrawFromPile "tree"
                        if ($c) { $drawn += $c }
                    }
                    foreach ($c in $drawn) {
                        $stays = ResolveDrafted $player $c
                        if ($stays) { AddToDomain $player $c }
                    }
                    Log "  → Draws $n from Tree: $(($drawn | ForEach-Object { $_.Name }) -join ', ')"
                }
                "Chiefdom" {
                    $mob = $State.Domains[$player] | Where-Object { $_.Tags -contains "Mob" } | Select-Object -First 1
                    if ($mob) {
                        $target = $PlayerNames | Where-Object { $_ -ne $player } | Get-Random
                        $null = $State.Domains[$player].Remove($mob)
                        AddToDomain $target $mob
                        Log "  → Moves $($mob.Name) to $target's Domain"
                    }
                }
                "Outriders" {
                    $drawn = @()
                    for ($o = 0; $o -lt 3; $o++) {
                        $c = DrawFromPile "claw"
                        if ($c) { $drawn += $c }
                    }
                    if ($drawn.Count -gt 0) {
                        # Discard worst (most Discontent-tagged or random)
                        $worst = $drawn | Where-Object { $_.Tags -contains "Discontent" } | Select-Object -First 1
                        if (-not $worst) { $worst = $drawn[-1] }
                        foreach ($c in $drawn) {
                            if ($c -eq $worst) {
                                $null = $State.Discards[$player].Add($c)
                            } else {
                                AddToDomain $player $c
                            }
                        }
                        Log "  → Draws 3 Claw: $(($drawn | ForEach-Object { $_.Name }) -join ', '). Discards $($worst.Name)."
                    }
                }
                "Land Grab" {
                    $lands = @($State.Season | Where-Object { $_.Tags -contains "Land" })
                    foreach ($l in $lands) {
                        $State.Season = @($State.Season | Where-Object { $_ -ne $l })
                        AddToDomain $player $l
                        Log "  → Takes $($l.Name) from Season"
                    }
                    DiscardFromDomain $player "Land Grab" | Out-Null
                    Log "  → Land Grab discarded"
                }
                "Militia" {
                    $mob = $State.Domains[$player] | Where-Object { $_.Tags -contains "Mob" } | Select-Object -First 1
                    if ($mob) {
                        DiscardFromDomain $player $mob.Name | Out-Null
                        Log "  → Discards $($mob.Name)"
                    }
                }
                "Blood Offering" {
                    $sacrifice = $State.Domains[$player] | Where-Object { $_.Tags -contains "Discontent" } | Select-Object -First 1
                    if (-not $sacrifice) { $sacrifice = $State.Domains[$player] | Where-Object { $_.Name -ne "Blood Offering" } | Select-Object -First 1 }
                    if ($sacrifice) {
                        DiscardFromDomain $player $sacrifice.Name | Out-Null
                        Log "  → Sacrifices $($sacrifice.Name), triggers Rite globally"
                    }
                }
                "Herbalism" {
                    $cost = $State.Domains[$player] | Where-Object { $_.Tags -contains "Knowledge" -or $_.Tags -contains "Nature" } | Where-Object { $_.Name -ne "Herbalism" } | Select-Object -First 1
                    $retrieve = $State.Discards[$player] | Select-Object -First 1
                    if ($cost -and $retrieve) {
                        DiscardFromDomain $player $cost.Name | Out-Null
                        $null = $State.Discards[$player].Remove($retrieve)
                        AddToDomain $player $retrieve
                        Log "  → Discards $($cost.Name), retrieves $($retrieve.Name) from discard"
                    }
                }
                "Crags" {
                    Log "  → Peeks at top 3 Claw (intel gathering)"
                }
                "Sacred Grove" {
                    # Choose: Rite locally or scry
                    $spiritualCount = CountTag $player "Spiritual"
                    if ($spiritualCount -gt 1) {
                        Log "  → Triggers Rite in $player's Domain"
                    } else {
                        $top3 = @()
                        # Just peek — don't actually draw (scry)
                        Log "  → Scries top 3 Tree for [Spiritual] cards"
                    }
                }
            }
        }
        "wheat" {
            # Take 1-2 from Fields, draw Claw for each
            $numTake = [math]::Min(2, $State.Fields.Count)
            $taken = @()
            $clawDrawn = @()
            for ($w = 0; $w -lt $numTake; $w++) {
                $best = $State.Fields | Sort-Object { 
                    $s = 0
                    if ($_.Name -eq "Tavern") { $s = 8 }
                    if ($_.Name -eq "Militia") { $s = 7 }
                    if ($_.Name -eq "Animal Husbandry") { $s = 6 }
                    if ($_.Name -eq "Plough") { $s = 5 }
                    if ($_.Name -eq "Granary") { $s = 5 }
                    if ($_.Name -eq "Mill") { $s = 5 }
                    if ($_.Name -eq "Feed the Commoners") { $s = 7 }
                    if ($_.Name -eq "Apprenticeship") { $s = 4 }
                    if ($_.Name -eq "Famine") { $s = 3 }
                    $s
                } -Descending | Select-Object -First 1
                
                if ($best) {
                    $State.Fields = @($State.Fields | Where-Object { $_ -ne $best })
                    $taken += $best
                    $claw = DrawFromPile "claw"
                    if ($claw) { $clawDrawn += $claw }
                }
            }
            
            Log "**T$t — ${player}:** Activates **Wheat**. Takes $(($taken | ForEach-Object { $_.Name }) -join ', ') from Fields."
            if ($clawDrawn.Count -gt 0) {
                Log "  → Claw tax: $(($clawDrawn | ForEach-Object { CardStr $_ }) -join ', ')"
            }
            
            foreach ($card in $taken) {
                $stays = ResolveDrafted $player $card
                if ($stays) { AddToDomain $player $card }
            }
            foreach ($card in $clawDrawn) {
                $stays = ResolveDrafted $player $card
                if ($stays) { AddToDomain $player $card }
            }
            Log "  → Fields remaining: $($State.Fields.Count)"
        }
    }
    
    # Log domain state
    Log "→ Domain: $(DomainStr $player)"
    if ($State.Discards[$player].Count -gt 0) {
        Log "→ Discard: $(DiscardStr $player)"
    }
    Log ""
    
    # State snapshot every 10 turns
    if ($t % 10 -eq 0) {
        Log "---"
        Log ""
        Log "### === STATE AFTER TURN $t ==="
        Log ""
        foreach ($p in $PlayerNames) {
            Log "**$p** ($($State.Domains[$p].Count) cards): $(DomainStr $p)"
            if ($State.Discards[$p].Count -gt 0) { Log "  Discard: $(DiscardStr $p)" }
        }
        Log ""
        Log "Season: $(if ($State.Season.Count -gt 0) { ($State.Season | ForEach-Object { $_.Name }) -join ', ' } else { '(empty)' })"
        Log "Fields ($($State.Fields.Count)): $(if ($State.Fields.Count -gt 0) { ($State.Fields | ForEach-Object { $_.Name }) -join ', ' } else { '(empty)' })"
        Log "Piles remaining: Claw $(PileRemaining 'claw'), Tree $(PileRemaining 'tree'), Wheat $(PileRemaining 'wheat'), Coin $(PileRemaining 'coin')"
        Log ""
        Log "---"
        Log ""
    }
}

# Epilogue
Log "---"
Log ""
Log "## Epilogue"
Log ""
foreach ($p in $PlayerNames) {
    $d = $State.Domains[$p]
    Log "**$p** — $($d.Count) cards in Domain"
    Log "  Domain: $(DomainStr $p)"
    $tags = @{}
    foreach ($c in $d) {
        foreach ($tag in $c.Tags) {
            if (-not $tags[$tag]) { $tags[$tag] = 0 }
            $tags[$tag]++
        }
    }
    if ($tags.Count -gt 0) {
        Log "  Tags: $(($tags.GetEnumerator() | ForEach-Object { "[$($_.Key)]×$($_.Value)" }) -join ', ')"
    }
    Log ""
}
Log "### Pile Status"
Log "Claw: $(PileRemaining 'claw') remaining | Tree: $(PileRemaining 'tree') remaining | Wheat: $(PileRemaining 'wheat') remaining | Coin: $(PileRemaining 'coin') remaining"

# Write output
$output = $State.Log -join "`n"

if ($OutFile) {
    $output | Set-Content $OutFile -Encoding UTF8
    Write-Host "Simulation written to $OutFile"
} else {
    # Auto-name
    $outPath = "$PSScriptRoot\simulation-12.md"
    $output | Set-Content $outPath -Encoding UTF8
    Write-Host "Simulation written to $outPath"
}
