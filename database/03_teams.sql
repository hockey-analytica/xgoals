CREATE TABLE IF NOT EXISTS nhl.teams (
    "team_uid" INTEGER,
    "franchise_uid" INTEGER,
    "name" TEXT,
    "code" CHAR(3),
    "color" CHAR(7),
    "created_source" VARCHAR(255) NOT NULL,
    "created_timestamp" TIMESTAMPTZ NOT NULL,
    "modified_source" VARCHAR(255) NOT NULL,
    "modified_timestamp" TIMESTAMPTZ NOT NULL,

    PRIMARY KEY ("team_uid")
);