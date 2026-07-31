CREATE TABLE IF NOT EXISTS nhl.bios (
    "athlete_uid" INTEGER,
    "full_name" TEXT,
    "last_name" TEXT,
    "birth_date" DATE,
    "birth_city" TEXT,
    "birth_state" TEXT,
    "birth_country" TEXT,
    "nationality" TEXT,
    "draft_year" INTEGER,
    "draft_round" INTEGER,
    "draft_pick" INTEGER,
    "position" TEXT,
    "handedness" TEXT,
    "height" INTEGER,
    "weight" INTEGER,
    "created_source" VARCHAR(255) NOT NULL,
    "created_timestamp" TIMESTAMPTZ NOT NULL,
    "modified_source" VARCHAR(255) NOT NULL,
    "modified_timestamp" TIMESTAMPTZ NOT NULL,

    PRIMARY KEY ("athlete_uid")
);