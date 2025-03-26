-- Add created_at column to collections table
ALTER TABLE collections 
ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create questions table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    collection_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    example_answer TEXT NOT NULL,
    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
);

-- Create indexes
CREATE INDEX idx_questions_collection_id ON questions(collection_id);

-- Create students table
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    school_id INTEGER NOT NULL,
    student_name VARCHAR(255) NOT NULL
);

-- Create student_answers table
CREATE TABLE student_answers (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    answer_text TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
);

-- Create indexes for student_answers
CREATE INDEX idx_student_answers_student_id ON student_answers(student_id);
CREATE INDEX idx_student_answers_question_id ON student_answers(question_id);
