CREATE TABLE IF NOT EXISTS public.logs (
    "execution" TEXT,
    "target" TEXT,
    "date" DATE,
    "status" INTEGER,
    "start" TIMESTAMPTZ,
    "end" TIMESTAMPTZ,
    "created_source" VARCHAR(255) NOT NULL,
    "created_timestamp" TIMESTAMPTZ NOT NULL,
    "modified_source" VARCHAR(255) NOT NULL,
    "modified_timestamp" TIMESTAMPTZ NOT NULL,

    PRIMARY KEY ("execution", "date")
);