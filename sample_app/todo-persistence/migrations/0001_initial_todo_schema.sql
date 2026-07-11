CREATE TABLE IF NOT EXISTS todos (
    id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT chk_todos_title_not_blank CHECK (length(trim(title)) > 0),
    CONSTRAINT chk_todos_title_length CHECK (char_length(title) <= 255)
);

CREATE INDEX IF NOT EXISTS idx_todos_is_completed ON todos (is_completed);
CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos (created_at);
