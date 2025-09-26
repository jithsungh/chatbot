-- Enable UUID generation extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum types for status and dept
CREATE TYPE user_question_status AS ENUM ('pending', 'processed');
CREATE TYPE dept_type AS ENUM ('HR', 'IT', 'Security');

-- Table: user_questions
CREATE TABLE user_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    userid UUID NOT NULL,
    query TEXT NOT NULL,
    answer TEXT,
    context TEXT,
    status user_question_status DEFAULT 'pending',
    dept dept_type,
    createdAt TIMESTAMPTZ DEFAULT NOW()
);

-- Enum type for admin question status
CREATE TYPE admin_question_status AS ENUM ('pending', 'processed');

-- Table: admin_questions
CREATE TABLE admin_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    adminid UUID NOT NULL,
    question TEXT NOT NULL,
    answer TEXT,
    status admin_question_status DEFAULT 'pending',
    dept dept_type,
    frequency INT DEFAULT 0,
    vectordbid UUID,
    createdAt TIMESTAMPTZ DEFAULT NOW()
);
