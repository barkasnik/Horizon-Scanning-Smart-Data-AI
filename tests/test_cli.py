from datetime import datetime, timezone

from smart_data_radar.cli import MONTHLY_MIN_ARTICLES, select_candidates_for_analysis
from smart_data_radar.models import Article


def article(number: int, score: float) -> Article:
    topics = [
        "Open finance regulation",
        "Energy consumer portability",
        "Digital identity governance",
        "Property data standards",
        "Transport interoperability",
        "AI delegated consent",
        "Retail competition policy",
        "Trade provenance systems",
        "Fraud prevention framework",
        "Banking API reform",
        "Telecoms switching rules",
        "Critical minerals tracking",
        "Data protection enforcement",
        "International CDR review",
        "Supply chain assurance",
    ]
    return Article(
        url=f"https://example.com/{number}",
        canonical_url=f"https://example.com/{number}",
        title=topics[number],
        discovered_at=datetime.now(timezone.utc),
        discovery_method="test",
        heuristic_score=score,
    )


def test_monthly_selection_keeps_at_least_ten_best_candidates():
    scored = [article(number, 50 - number * 3) for number in range(15)]
    selected = select_candidates_for_analysis(
        scored,
        mode="monthly",
        min_score=35,
        candidate_limit=50,
    )
    assert len(selected) == MONTHLY_MIN_ARTICLES
    assert [item.heuristic_score for item in selected] == sorted(
        (item.heuristic_score for item in selected), reverse=True
    )


def test_weekly_selection_keeps_normal_relevance_threshold():
    scored = [article(number, 50 - number * 3) for number in range(15)]
    selected = select_candidates_for_analysis(
        scored,
        mode="weekly",
        min_score=35,
        candidate_limit=50,
    )
    assert len(selected) < MONTHLY_MIN_ARTICLES
    assert all(item.heuristic_score >= 35 for item in selected)
