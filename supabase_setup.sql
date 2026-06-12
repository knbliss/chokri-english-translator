-- Run this in the Supabase SQL editor (Database → SQL Editor → New query)
-- Creates the contributions table used by the Chokri–English translator app.

CREATE TABLE IF NOT EXISTS contributions (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    chokri        TEXT        NOT NULL,
    english       TEXT        NOT NULL,
    type          TEXT        NOT NULL CHECK (type IN ('correction', 'new_pair')),
    note          TEXT        NOT NULL DEFAULT '',
    submitted_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status        TEXT        NOT NULL DEFAULT 'pending'
                                      CHECK (status IN ('pending', 'verified', 'rejected')),
    reviewed_by   TEXT        NOT NULL DEFAULT '',
    reviewer_notes TEXT       NOT NULL DEFAULT '',
    reviewed_at   TIMESTAMPTZ
);

-- Index for the reviewer queue (pending items, oldest first)
CREATE INDEX IF NOT EXISTS contributions_status_submitted
    ON contributions (status, submitted_at);

-- Row-level security: public can INSERT (submit), only service role can UPDATE (review)
ALTER TABLE contributions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can submit"
    ON contributions FOR INSERT
    TO anon
    WITH CHECK (status = 'pending');

CREATE POLICY "Anyone can view contributions"
    ON contributions FOR SELECT
    TO anon
    USING (true);

-- UPDATE and DELETE require service-role key (the app uses SUPABASE_KEY = service-role key
-- so reviewer actions work; the anon key used by the public cannot update rows).
