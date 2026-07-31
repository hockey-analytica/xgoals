CREATE TABLE IF NOT EXISTS nhl.schedules (
    "season_uid" INTEGER,
    "season_type" INTEGER,
    "game_uid" INTEGER,
    "team_uid" INTEGER,
    "home" BOOLEAN,
    "schedule_state" TEXT,
    "game_state" TEXT,
    "start_time" TIMESTAMPTZ,
    "created_source" VARCHAR(255) NOT NULL,
    "created_timestamp" TIMESTAMPTZ NOT NULL,
    "modified_source" VARCHAR(255) NOT NULL,
    "modified_timestamp" TIMESTAMPTZ NOT NULL,

    PRIMARY KEY ("game_uid", "season_uid", "season_type", "team_uid")
);