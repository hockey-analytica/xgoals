WITH src AS (
  SELECT
    season_uid,
	strength,
	class,
    CASE WHEN class = 'goal' THEN 1 ELSE 0 END AS target,
	xgoals AS prediction,
	RANK() OVER(PARTITION BY season_uid ORDER BY xgoals ASC) AS record -- Remove "PARTITION BY season_uid" when aggregating metrics across all seasons
  FROM nhl.shots
  WHERE class NOT IN ('blocked-shot')
  -- AND strength = '1551' -- Full Strength Filter
  -- AND SUBSTRING(strength, 4, 1) = '1' AND strength <> '1551' -- Special Teams Filter
  -- AND SUBSTRING(strength, 4, 1) = '0' -- Empty Net Filter
), staged AS (
  SELECT
    season_uid,
	class,
	target,
	prediction,
	AVG(record) OVER(PARTITION BY season_uid, prediction) AS record
  FROM src
), seasons AS (
  SELECT
    season_uid,
    SUM(prediction) - COUNT(*) FILTER(WHERE class = 'goal') AS difference,
    (100.0 * SUM(prediction) / COUNT(*) FILTER(WHERE class = 'goal')) - 100 AS calibration,
    -AVG(
      CASE WHEN class = 'goal' THEN 1 ELSE 0 END * LN(GREATEST(prediction, 1e-15)) +
      CASE WHEN class = 'goal' THEN 0 ELSE 1 END * LN(GREATEST(1 - prediction, 1e-15))
    ) AS logloss,
    SUM(CASE WHEN target = 1 THEN record ELSE 0 END) AS total,
    COUNT(*) FILTER(WHERE target = 1) AS positive,
    COUNT(*) FILTER(WHERE target = 0) AS negative
  FROM staged
  GROUP BY season_uid
)

SELECT
  season_uid,
  ROUND(difference, 2) AS difference, 
  ROUND(calibration, 2) AS calibration,
  ROUND(logloss, 3) AS logloss,
  ROUND((total - (positive * (positive + 1) / 2.0)) / (positive * negative), 3) AS auc
FROM seasons
ORDER BY season_uid DESC;