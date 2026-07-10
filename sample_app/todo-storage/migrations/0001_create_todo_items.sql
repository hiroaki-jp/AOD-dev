-- migration_version: 0001
-- Creates the todo_items table for TODO management.

CREATE TABLE todo_items (
    id          uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
    title       varchar(255) NOT NULL,
    description text        NULL,
    is_completed boolean    NOT NULL DEFAULT FALSE,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT chk_todo_items_title_not_empty CHECK (char_length(title) > 0)
);

CREATE INDEX idx_todo_items_is_completed ON todo_items (is_completed);
