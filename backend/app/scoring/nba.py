from app.models import Game, NBAGameStats

PLAYOFF_MULTIPLIERS = {
    "finals": 1.3,
    "conference_finals": 1.2,
    "semifinals": 1.1,
    "first_round": 1.05,
}


def calculate_nba_game_score(game: Game, stats: NBAGameStats) -> tuple[float, list[str]]:
    score = 5.0
    breakdown: list[str] = []

    margin = abs(game.home_score - game.away_score)
    if margin <= 3:
        pts, reason = 2.0, "Decided by a last-second play"
    elif margin <= 8:
        pts, reason = 1.5, "Came down to the wire"
    elif margin <= 15:
        pts, reason = 1.0, "Competitive throughout"
    else:
        pts, reason = 0.0, "Comfortable victory"
    score += pts
    breakdown.append(reason)

    ot = stats.overtime_periods
    if ot >= 2:
        score += 1.5
        breakdown.append(f"{ot}OT thriller")
    elif ot == 1:
        score += 1.0
        breakdown.append("Went to overtime")

    deficit = stats.largest_deficit_overcome or 0
    if deficit >= 20:
        score += 1.0
        breakdown.append(f"Massive {deficit}-point comeback")
    elif deficit >= 12:
        score += 0.5
        breakdown.append(f"Overcame {deficit}-point deficit")

    if (stats.lead_changes or 0) >= 20:
        score += 0.5
        breakdown.append("Back and forth all game")

    if game.is_playoff:
        multiplier = PLAYOFF_MULTIPLIERS.get(game.playoff_round or "", 1.0)
        if multiplier > 1.0:
            score *= multiplier
            breakdown.append(f"High-stakes {(game.playoff_round or '').replace('_', ' ')}")

    return min(round(score, 1), 10.0), breakdown
