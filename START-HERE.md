# START HERE — Version 5

This is the complete Smart Data & AI Horizon Scanner.

## What you should see on the public site

A visual dashboard with:

- Weekly / Monthly tabs
- summary metric boxes
- ranked policy-intelligence cards
- search, hashtag, relevance and sort controls
- policy priority scores
- links to every original source article
- human-written-style bottom lines
- Government / Smart Data PESTLE analysis
- UK Smart Data programme SWOT analysis
- policy implications, tensions and questions to pursue
- hashtags such as `#PolicyGap`, `#Opportunity`, `#Threat`, `#Monitor`, `#AIxSmartData`

The public dashboard **does not republish scraped article bodies**.

## Safest way to replace the earlier broken upload

The earlier browser upload flattened the folders. Version 5 must keep its folders.

1. Download and unzip `Smart-Data-Horizon-Scanner-v5.zip`.
2. Open your GitHub repository.
3. Delete the old incorrectly uploaded files if you are replacing the current repository, or create a fresh repository.
4. Choose **Add file → Upload files**.
5. Drag the **contents of the `Smart-Data-Horizon-Scanner-v5` folder**, including the folders themselves, into the upload area. Modern Chrome/Edge will retain the folder paths when a folder tree is dropped.
6. Before committing, check GitHub shows paths such as:
   - `.github/workflows/radar.yml`
   - `config/interest_profile.yml`
   - `src/smart_data_radar/cli.py`
   - `tests/test_dashboard.py`
   - `index.html`
7. Commit the upload.
8. In **Settings → Pages**, publish from the `main` branch `/ (root)` if your Pages site is not already configured.
9. In **Actions**, open **Smart Data AI Radar**, choose **Run workflow**, then choose `weekly`.
10. Run it again with `monthly` if you want both tabs populated immediately.

## What happens automatically

- Weekly run: Monday 07:10 UTC
- Monthly run: first day of each month 07:30 UTC
- Google News RSS provides credential-free broad discovery.
- GOV.UK Smart Data and Raidiam Insights are directly monitored.
- Articles are extracted where permitted by robots.txt.
- The radar ranks candidates before LLM analysis.
- Ollama + `qwen2.5:1.5b-instruct` performs the default no-paid-API analysis.
- The workflow writes `output/weekly-latest.json` / `output/monthly-latest.json` and related Markdown/HTML files.
- `index.html` reads those JSON files automatically and turns them into the dashboard.

## If the dashboard says “No weekly data file found yet”

That is expected before the first successful workflow. Run the weekly Action once.

## If the Action cannot push the report

Go to **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**, then rerun it.

## Important

Do not move `radar.yml` out of `.github/workflows/`. GitHub will not recognise it as an Action anywhere else.
