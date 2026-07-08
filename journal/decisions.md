Project Roadmap

Stage 1 — Static World Cup Winner Prediction 

Predict the champion before the tournament using historical data (2006–2022).

Features: Elo, qualification stats, host, confederation, previous WC progress
Models: Logistic Regression, Random Forest, XGBoost
Evaluation: Leave-One-World-Cup-Out CV
Output: Pre-tournament champion probabilities for all 2026 qualified teams

Stage 2A — Live Data Pipeline 

Build the infrastructure to update team state after every match.

Create: update_after_match.py

Input example: Brazil 2-1 Serbia

Updates:

Goals scored / conceded (in tournament)
Goal difference (in tournament)
Dynamic Elo (winner +K, loser −K)
Tournament form (last N matches: win %, goals for/against)
Match log in tournament state
Output: updated feature file (e.g. updated_worldcup2026.csv) + tournament_state.json

Tournament state tracks:

Completed matches
Eliminated teams
Current round (group / R16 / QF / SF / Final)

Stage 2B — Dynamic Re-Prediction + Timeline

Re-run the same Stage 1 model on updated features after each match or round.

Pipeline:

Load updated feature CSV
Run existing predict logic (XGBoost / RF / LR)
Apply elimination filter (eliminated teams → 0%)
Renormalize probabilities to sum to 100%
Save timestamped snapshot
Output example:

predictions/snapshots/
  pre_tournament.csv
  after_group_stage.csv
  after_r16.csv
  after_qf.csv
  ...
Champion probability timeline example:

Argentina: 18% → 26% → 41% → 63% → 82%
Important constraints:

Dynamic Elo is the safest feature to feed the existing model (trained on pre-tournament Elo)
Tournament form: track now, use cautiously until model is retrained on similar data
Elimination filter is mandatory — without it, eliminated teams still get non-zero champion probability
Optional: store both model_probability (raw) and live_probability (after elimination + renormalize)

Stage 2C — Visualization

Graph champion probability over time per team, and top-10 favorites after each round.

Stage 3 — Match-Level Prediction

Predict individual match outcomes instead of only the tournament winner.

Input: Team A vs Team B (+ Elo diff, home advantage, rest days, form, etc.)

Output:

P(Team A win), P(draw), P(Team B win)
Expected goals (optional, Poisson model)
Start simple: Elo-based win probability, then logistic/XGBoost on international match history (results.csv).

Stage 4 — Monte Carlo Tournament Simulation + Bracket

Simulate the full 2026 tournament (groups + knockout) 10,000–100,000 times.

Uses:

Match model from Stage 3
Bracket / advancement rules from tournament engine
Live state from Stage 2A (fixed results for completed matches)
Outputs:

Champion probability
Reach Final / Semi / Quarter / R16 probability
This replaces re-running the classifier as the primary champion probability engine. Stage 2 update pipeline is kept; Monte Carlo consumes it.

Stage 5 — AI Explanation Layer (LLM / RAG)

Natural-language Q&A over model outputs and retrieved facts.

Example:

Q: "Why is Spain the favorite?"
A: Retrieves Elo, qualification PPG, previous WC progress, simulated championship probability → generates explanation
The LLM does not predict; it interprets questions and fetches from our models and data.

Stage 6 — Web Dashboard / Deployment

Interactive UI: winner probabilities, round progression, match predictions, player pages (later), live updates after each match.

Deferred (research backlog — not now):

Bayesian Elo (upgrade to Stage 2A Elo later)
Deep learning / neural networks (insufficient WC sample size)
Graph neural networks
Reinforcement learning (tactics, not winner prediction)
Player-level models (Golden Boot, cards, etc.)

Decision 001:
Stage 1 will predict the FIFA World Cup winner using only data available before the tournament starts.

Reason:
- Avoids data leakage.
- Simpler to validate.
- Serves as the foundation for the live model in Stage 2.

Decision 002:
The initial dataset will contain 13 predictive features together with:
Year
Team
Winner (target)

All predictive features must represent information available before the tournament starts.

Categorical information (such as Confederation) will be encoded numerically for machine learning compatibility.

Selected Features:-

1. Elo Rating
Reason:
Measures the overall strength of a national team.

2. FIFA Ranking
Reason:
Official FIFA assessment of team performance.

3. Qualification Stats (Matches, Win Rate, Draw Rate, Loss Rate, Goals For Per Game, Goals Against Per Game, Goal Difference Per Game, Points Per Game)
Reason:
Performance of the national team before the World Cup.

4. Host 
Reason:
Hosting the World Cup historically matters.

5. Confederation
Reason:
Historically, UEFA and CONMEBOL dominate World Cups. The model should know that.

6. Previous World Cup Finish
Reason:
How well the team performed in the previous World Cup

Decision 003:
The initial model will be trained on the five most recent World Cups (2006–2022), each featuring 32 teams, resulting in 160 training samples.
The trained model will later be applied to the 48-team 2026 World Cup. 
Will this cause an issue?
NO, the model isnt learning that there are 32 teams, we have many features which still apply regardless there are 32 or 48 teams. 

Decision 004:
Separately build the list of teams that played in each World Cup. If we only use the 2026-qualified dataset that will ignore many historical World Cup teams. 

For example:- Italy would be missing... But Italy won the 2006 World Cup. Imagine teaching a child to recognize animals, but every picture of a tiger is removed from the training set. Then you ask the child to identify tigers later. The model has never seen one. That's exactly what would happen here. The model would never learn that the 2006 champion existed.

If a team played in the World Cup, it must appear in the training dataset—even if it didn't qualify for 2026.

Decision 005:
Should we pick the goals scored/conceded during the World Cup?
NO, using future information to predict the past (data leakage). We should use the data during the qualification stage because we are standing at the point where the event is going to begin.

"Could someone have known this on the morning before the first World Cup match?"

If yes, it's a valid feature.
If no, it's future information and must not be used.

Decision 006:
Methods to extract or scrape data:-

1. BeautifulSoup + requests:
Suitable for static HTML pages.

2. Selenium / Playwright:
Suitable for JavaScript-rendered websites.

3. Use the underlying data source directly:
The frontend is a thin SPA over TSV files, It means the webpage is not the real data. The webpage simply loads those files and displays them. Many websites expose the data used to render their tables through downloadable files or APIs.

For Elo Rating we pick method 3 as it is most cleaniest and easiest! Method 2 also works but method 3 is direct and simple.

Decision 007:
Use the official JSON endpoint for FIFA Rankings instead of web scraping. The endpoint returns structured data including team names, ranks, points, confederation, and more. 

Decision 008:
To use Previous World Cup Progress instead of Previous World Cup Finish.

Progress = 1 - (remaining teams -1)/(total teams - 1)  

In this way we can train for any world cup even if a new round is introduced due to increase or decrease in tournament size. Then it doesnt matter whether there are 32 or 48 teams.. This only tracks how much % far did they reach in the tournament.

Decision 009:
Chosen models :- 

1. Logistic Regression
Reason:
Simple baseline model.
Fast to train.
Highly interpretable.
Produces calibrated probabilities after feature scaling.

2. Random Forest
Reason:
Captures nonlinear feature interactions.
Naturally handles mixed feature types.
Robust to noise and outliers.
Provides feature importance scores.

3. XGBoost
Reason:
State-of-the-art gradient boosting algorithm.
Excellent predictive performance on structured/tabular datasets.
Handles complex nonlinear relationships.
Frequently achieves the highest accuracy in machine learning competitions involving tabular data.

With this we are **DONE** with *Stage 1* 

Decision 010: 
Generic Live Tournament Architecture
Decided to build a YAML file that acts like the brain (Football knowledge). Which can be later read by config file and used in Python language.

Decision 011:
Decided which features are going to be updated during the tournament (Match after Match).
Made just a single update pipeline which is called from the CLI and is used by every input source.

Decision 012:
Also planned on marking teams as eliminated in knockout rounds and basically planned on advancement through the tournament.

Decision 013:
This architecture allows future World Cups (2030, 2034, etc.) to be supported primarily through new configuration files instead of modifying the update engine.

Decision 014:
Planned on writing unit and integration test cases
Unit test verifies that one small unit of code behaves exactly as expected.

The "unit" is usually:

one function
one method
sometimes one class

They don't test - "Does the whole application work?"
They only test - "Does THIS function behave correctly?"

Which files should be tested?
A simple rule - If a file contains logic, test it.
Integration test verifies that an entire workflow or pipeline is working together collectively as expected.

