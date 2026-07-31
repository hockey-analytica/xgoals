CREATE TABLE IF NOT EXISTS nhl.shifts (
    "game_uid" INTEGER,
    "athlete_uid" INTEGER,
    "team_uid" INTEGER,
    "period" INTEGER,
    "start" TEXT,
    "end" TEXT,
    "duration" TEXT,
    "shift" INTEGER,
    "created_source" VARCHAR(255) NOT NULL,
    "created_timestamp" TIMESTAMPTZ NOT NULL,
    "modified_source" VARCHAR(255) NOT NULL,
    "modified_timestamp" TIMESTAMPTZ NOT NULL,

    PRIMARY KEY ("game_uid", "athlete_uid", "period", "shift")
);