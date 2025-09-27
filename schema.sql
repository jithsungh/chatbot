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
    createdat TIMESTAMPTZ DEFAULT NOW()
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
    createdat TIMESTAMPTZ DEFAULT NOW()
);

-- Table: admins
CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    enabled BOOLEAN DEFAULT FALSE,
    verified BOOLEAN DEFAULT FALSE,
    verification_token TEXT,
    last_login TIMESTAMPTZ,
    createdat TIMESTAMPTZ DEFAULT NOW()
);

-- Table: text_knowledge
CREATE TABLE text_knowledge (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    adminid UUID NOT NULL,
    admin_name TEXT NOT NULL,
    text TEXT NOT NULL,
    dept dept_type NOT NULL,
    createdat TIMESTAMPTZ DEFAULT NOW()
);

-- Table: file_knowledge
CREATE TABLE file_knowledge(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    adminid UUID NOT NULL,
    admin_name TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    createdat TIMESTAMPTZ DEFAULT NOW()
);

CREATE TYPE dept_failure_status AS ENUM ('pending', 'processed', 'discarded');

-- Table: dept_failures
CREATE TABLE dept_failures (
    id UUID DEFAULT uuid_generate_v4(),
    query TEXT NOT NULL,
    adminid UUID,
    comments TEXT,
    detected dept_type NOT NULL,
    expected dept_type NOT NULL,
    status dept_failure_status DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table: response_times
CREATE TABLE response_times(
id SERIAL PRIMARY KEY,
timestamp TIMESTAMPTZ NOT NULL,
avg_response_time DOUBLE PRECISION,
requests_count INT NOT NULL DEFAULT 0
);

CREATE INDEX idx_response_times_timestamp ON response_times(timestamp);
