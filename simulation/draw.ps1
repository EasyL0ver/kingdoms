# Kingdoms — Deck Shuffler
# Usage: . .\draw.ps1
# Loads decks.json, shuffles each deck, prints the order. That's it.

$DeckData = Get-Content "$PSScriptRoot\decks.json" -Raw | ConvertFrom-Json

foreach ($deckName in $DeckData.PSObject.Properties.Name | Sort-Object) {
    $cards = @()
    foreach ($card in $DeckData.$deckName) {
        for ($i = 0; $i -lt $card.count; $i++) {
            $tags = if ($card.tags.Count -gt 0) { " [$($card.tags -join '] [')]" } else { "" }
            $cards += "$($card.name)$tags"
        }
    }
    $shuffled = $cards | Get-Random -Count $cards.Count

    Write-Host "`n=== $($deckName.ToUpper()) ($($shuffled.Count) cards) ===" -ForegroundColor Yellow
    for ($i = 0; $i -lt $shuffled.Count; $i++) {
        Write-Host "  $($i + 1). $($shuffled[$i])"
    }
}
