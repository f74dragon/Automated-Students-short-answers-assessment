-- Add created_at to collections table
ALTER TABLE collections ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create questions table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    collection_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    example_answer TEXT NOT NULL,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

-- Create index on collection_id for better query performance
CREATE INDEX idx_questions_collection_id ON questions(collection_id);
