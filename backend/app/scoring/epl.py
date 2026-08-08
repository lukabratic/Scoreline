from app.models import EPLGameEvent, Game, Team

# Well-known rivalries only — title/relegation-decider detection needs point-in-time standings
# and is deliberately out of scope for now (see CLAUDE.md). Matched on Team.short_name pairs.
DERBIES = {
    frozenset({"Arsenal", "Tottenham"}),
    frozenset({"Man City", "Man United"}),
    frozenset({"Liverpool", "Everton"}),
    frozenset({"Chelsea", "Tottenham"}),
    frozenset({"Chelsea", "Arsenal"}),
    frozenset({"West Ham", "Tottenham"}),
    frozenset({"Crystal Palace", "Brighton Hove"}),
}


def _is_derby(home_team: Team, away_team: Team) -> bool:
    return frozenset({home_team.short_name, away_team.short_name}) in DERBIES


def calculate_epl_game_score(
    game: Game, events: list[EPLGameEvent], home_team: Team, away_team: Team
) -> tuple[float, list[str]]:
    score = 5.0
    breakdown: list[str] = []

    total_goals = game.home_score + game.away_score
    if total_goals >= 6:
        score += 1.5
        breakdown.append(f"Goal fest — {total_goals} goals")
    elif total_goals >= 4:
        score += 1.0
        breakdown.append("High-scoring affair")
    elif total_goals >= 2:
        score += 0.5
        breakdown.append("Goals at both ends")

    margin = abs(game.home_score - game.away_score)
    if margin == 0:
        score += 1.5
        breakdown.append("Ended all square")
    elif margin == 1:
        score += 1.0
        breakdown.append("Tight result")

    late_goals = [
        e for e in events if e.event_type in ("goal", "penalty") and e.minute >= 85
    ]
    if len(late_goals) >= 2:
        score += 1.5
        breakdown.append("Multiple late drama goals")
    elif len(late_goals) == 1:
        score += 1.0
        breakdown.append(f"Late goal in the {late_goals[0].minute}th minute")

    if any(e.event_type == "red_card" for e in events):
        score += 0.5
        breakdown.append("Red card controversy")

    if _is_derby(home_team, away_team):
        score *= 1.15
        breakdown.append("Local derby")

    return min(round(score, 1), 10.0), breakdown
