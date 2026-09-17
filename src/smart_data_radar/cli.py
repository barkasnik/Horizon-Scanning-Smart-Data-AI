from __future__ import annotations

import os
from datetime import timedelta, timezone
from pathlib import Path
import typer

from .config import load_default_config
from .dedupe import dedupe_articles, dedupe_candidates
from .digest import write_outputs
from .discover import discover_index_sources, discover_search
from .extract import RobotsCache, extract_candidate
from .llm import analyse_article, analyse_digest
from .models import AnalysedArticle, Article
from .prioritise import final_rank_score, normalise_hashtags, priority_score
from .score import heuristic_score
from .storage import Store
from .utils import utcnow

app = typer.Typer(add_completion=False, help="Smart Data & AI news intelligence radar")
MONTHLY_MIN_ARTICLES = 10


def select_candidates_for_analysis(
    scored_articles: list[Article],
    *,
    mode: str,
    min_score: float,
    candidate_limit: int,
) -> list[Article]:
    """Select relevant candidates while preserving a 10-item monthly floor.

    Monthly briefings may use the strongest below-threshold items when fewer
    than ten articles clear the normal heuristic threshold. The items remain
    ranked by relevance and still undergo full LLM analysis.
    """
    ranked = dedupe_articles(scored_articles)
    selected = [article for article in ranked if article.heuristic_score >= min_score]
    if mode == "monthly" and len(selected) < MONTHLY_MIN_ARTICLES:
        selected = ranked[:MONTHLY_MIN_ARTICLES]
    return selected[:candidate_limit]


@app.command()
def run(
    mode: str = typer.Option("weekly", help="Weekly or monthly intelligence mode"),
    days: int | None = typer.Option(None, help="Override recency window; defaults to 7 weekly / 30 monthly"),
    candidate_limit: int = typer.Option(int(os.getenv("RADAR_CANDIDATE_LIMIT", "50"))),
    analyse_limit: int | None = typer.Option(None, help="Override successful LLM analyses; defaults to 8 weekly / 12 monthly"),
    min_score: float = typer.Option(float(os.getenv("RADAR_MIN_SCORE", "35")), help="Minimum heuristic score before LLM analysis"),
    backend: str = typer.Option(os.getenv("SEARCH_BACKEND", "google_news")),
    db: Path = typer.Option(Path("radar.db")),
    out_dir: Path = typer.Option(Path("output")),
    no_llm: bool = typer.Option(False, help="Discover/rank only; do not call the LLM"),
    no_synthesis: bool = typer.Option(False, help="Skip cross-article synthesis"),
) -> None:
    if mode not in {"weekly", "monthly"}:
        raise typer.BadParameter("--mode must be weekly or monthly")
    profile, sources = load_default_config()
    days = days if days is not None else (7 if mode == "weekly" else 30)
    if analyse_limit is None:
        env_limit = os.getenv("RADAR_ANALYSE_LIMIT")
        analyse_limit = int(env_limit) if env_limit else (8 if mode == "weekly" else 12)
    if mode == "monthly" and candidate_limit < MONTHLY_MIN_ARTICLES:
        raise typer.BadParameter(f"Monthly candidate limit must be at least {MONTHLY_MIN_ARTICLES}")
    if mode == "monthly" and analyse_limit < MONTHLY_MIN_ARTICLES:
        raise typer.BadParameter(f"Monthly analysis limit must be at least {MONTHLY_MIN_ARTICLES}")

    typer.echo(f"Mode: {mode} · window: {days} days · discovery backend: {backend}")

    candidates = []
    try:
        candidates.extend(discover_search(profile, backend=backend, days=days))
    except Exception as exc:
        typer.echo(f"Search discovery warning: {exc}")
    candidates.extend(discover_index_sources(sources))
    candidates = dedupe_candidates(candidates)
    typer.echo(f"Discovered {len(candidates)} unique candidates")

    robots = RobotsCache()
    scored_articles = []
    cutoff = utcnow() - timedelta(days=days)
    for candidate in candidates:
        try:
            article = extract_candidate(candidate, robots)
        except Exception:
            continue
        if article.published_at:
            pub = article.published_at
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            if pub < cutoff and "index:" not in article.discovery_method:
                continue
        score, matched = heuristic_score(article, profile, sources)
        article.heuristic_score = score
        article.matched_terms = matched
        scored_articles.append(article)

    articles = select_candidates_for_analysis(
        scored_articles,
        mode=mode,
        min_score=min_score,
        candidate_limit=candidate_limit,
    )
    typer.echo(f"{len(articles)} candidates passed heuristic relevance")

    store = Store(db)
    for article in articles:
        store.save_article(article)

    if no_llm:
        typer.echo("LLM analysis skipped (--no-llm). Ranked articles saved to SQLite.")
        store.close()
        return

    analysed: list[AnalysedArticle] = []
    attempt_limit = analyse_limit if mode == "weekly" else max(analyse_limit, MONTHLY_MIN_ARTICLES * 2)
    for article in articles[:attempt_limit]:
        try:
            analysis = analyse_article(article, profile, mode=mode)
            analysis.hashtags = normalise_hashtags(analysis, article.matched_terms)
        except Exception as exc:
            typer.echo(f"LLM skip: {article.title[:70]} ({exc})")
            continue
        pscore = priority_score(analysis, mode)
        final = final_rank_score(
            heuristic=article.heuristic_score,
            relevance=analysis.relevance_score,
            priority=pscore,
        )
        item = AnalysedArticle(
            article=article,
            analysis=analysis,
            final_score=final,
            priority_score=pscore,
            mode=mode,
        )
        analysed.append(item)
        store.save_analysis(item)
        if len(analysed) >= analyse_limit:
            break

    analysed.sort(key=lambda x: x.final_score, reverse=True)

    if mode == "monthly" and len(analysed) < MONTHLY_MIN_ARTICLES:
        store.close()
        raise RuntimeError(
            f"Monthly briefing requires at least {MONTHLY_MIN_ARTICLES} successfully analysed articles; "
            f"only {len(analysed)} were available. No monthly output was published."
        )

    synthesis = None
    if analysed and not no_synthesis:
        try:
            synthesis = analyse_digest([
                {
                    "title": i.article.title,
                    "source": i.article.source_name,
                    "priority_score": i.priority_score,
                    "bottom_line": i.analysis.bottom_line,
                    "why_it_matters": i.analysis.government_smart_data_perspective,
                    "hashtags": i.analysis.hashtags,
                }
                for i in analysed
            ], mode=mode)
        except Exception as exc:
            typer.echo(f"Synthesis warning: {exc}")

    store.close()
    md, js, ht = write_outputs(analysed, out_dir, synthesis, mode=mode)
    typer.echo(f"Wrote {md}, {js} and {ht}")


@app.command("show-profile")
def show_profile() -> None:
    profile, _ = load_default_config()
    typer.echo(profile.get("mission", ""))
    typer.echo("\nPrimary search phrases:")
    for phrase in profile.get("primary", {}).get("phrases", []):
        typer.echo(f"- {phrase}")


if __name__ == "__main__":
    app()
