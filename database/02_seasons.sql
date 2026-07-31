CREATE TABLE IF NOT EXISTS nhl.seasons (
    "season_uid" INTEGER,
    "start" DATE,
    "end" DATE,
    "games" INTEGER,
    "post_start" DATE,
    "created_source" VARCHAR(255) NOT NULL,
    "created_timestamp" TIMESTAMPTZ NOT NULL,
    "modified_source" VARCHAR(255) NOT NULL,
    "modified_timestamp" TIMESTAMPTZ NOT NULL,

    PRIMARY KEY ("season_uid")
);