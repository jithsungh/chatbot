--
-- PostgreSQL database dump
--

\restrict c4eJ4Ai3j34wwPsJudMlCXjkpk04r56m4JwQDbd9JcgeOgeDknGXKe95Y4lIeXQ

-- Dumped from database version 14.19
-- Dumped by pg_dump version 14.19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: admin_question_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.admin_question_status AS ENUM (
    'pending',
    'processed'
);


ALTER TYPE public.admin_question_status OWNER TO postgres;

--
-- Name: admin_role; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.admin_role AS ENUM (
    'super_admin',
    'admin',
    'read_only'
);


ALTER TYPE public.admin_role OWNER TO postgres;

--
-- Name: dept_failure_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.dept_failure_status AS ENUM (
    'pending',
    'processed',
    'discarded'
);


ALTER TYPE public.dept_failure_status OWNER TO postgres;

--
-- Name: dept_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.dept_type AS ENUM (
    'HR',
    'IT',
    'Security'
);


ALTER TYPE public.dept_type OWNER TO postgres;

--
-- Name: query_source; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.query_source AS ENUM (
    'user',
    'context'
);


ALTER TYPE public.query_source OWNER TO postgres;

--
-- Name: user_question_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_question_status AS ENUM (
    'pending',
    'processed'
);


ALTER TYPE public.user_question_status OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admin_questions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    adminid uuid,
    question text NOT NULL,
    answer text,
    status public.admin_question_status DEFAULT 'pending'::public.admin_question_status,
    dept public.dept_type,
    frequency integer DEFAULT 0,
    vectordbid uuid,
    createdat timestamp with time zone DEFAULT now()
);


ALTER TABLE public.admin_questions OWNER TO postgres;

--
-- Name: admins; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admins (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name text NOT NULL,
    email text NOT NULL,
    password text NOT NULL,
    enabled boolean DEFAULT false,
    last_login timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    verified boolean DEFAULT false,
    verification_token text,
    role public.admin_role DEFAULT 'admin'::public.admin_role NOT NULL
);


ALTER TABLE public.admins OWNER TO postgres;

--
-- Name: departments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.departments (
    id integer NOT NULL,
    name public.dept_type NOT NULL,
    description text NOT NULL,
    createdat timestamp with time zone DEFAULT now()
);


ALTER TABLE public.departments OWNER TO postgres;

--
-- Name: departments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.departments_id_seq OWNER TO postgres;

--
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.departments_id_seq OWNED BY public.departments.id;


--
-- Name: dept_failures; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dept_failures (
    id uuid DEFAULT public.uuid_generate_v4(),
    query text NOT NULL,
    adminid uuid,
    comments text,
    detected public.dept_type NOT NULL,
    expected public.dept_type NOT NULL,
    status public.dept_failure_status DEFAULT 'pending'::public.dept_failure_status,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.dept_failures OWNER TO postgres;

--
-- Name: dept_keywords; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dept_keywords (
    id integer NOT NULL,
    dept_id integer,
    keyword text NOT NULL
);


ALTER TABLE public.dept_keywords OWNER TO postgres;

--
-- Name: dept_keywords_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dept_keywords_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dept_keywords_id_seq OWNER TO postgres;

--
-- Name: dept_keywords_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dept_keywords_id_seq OWNED BY public.dept_keywords.id;


--
-- Name: file_knowledge; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.file_knowledge (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    adminid uuid NOT NULL,
    file_name text NOT NULL,
    file_path text NOT NULL,
    createdat timestamp with time zone DEFAULT now()
    dept public.dept_type NOT NULL,
);


ALTER TABLE public.file_knowledge OWNER TO postgres;

--
-- Name: response_times; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.response_times (
    id integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    avg_response_time double precision,
    requests_count integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.response_times OWNER TO postgres;

--
-- Name: response_times_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.response_times_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.response_times_id_seq OWNER TO postgres;

--
-- Name: response_times_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.response_times_id_seq OWNED BY public.response_times.id;


--
-- Name: text_knowledge; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.text_knowledge (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    adminid uuid NOT NULL,
    title text NOT NULL,
    text text NOT NULL,
    dept public.dept_type NOT NULL,
    createdat timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.text_knowledge OWNER TO postgres;

--
-- Name: user_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_questions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    userid uuid NOT NULL,
    query text NOT NULL,
    answer text,
    context text,
    status public.user_question_status DEFAULT 'pending'::public.user_question_status,
    dept public.dept_type,
    createdat timestamp with time zone DEFAULT now(),
    source public.query_source DEFAULT 'user'::public.query_source NOT NULL
);


ALTER TABLE public.user_questions OWNER TO postgres;

--
-- Name: departments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments ALTER COLUMN id SET DEFAULT nextval('public.departments_id_seq'::regclass);


--
-- Name: dept_keywords id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dept_keywords ALTER COLUMN id SET DEFAULT nextval('public.dept_keywords_id_seq'::regclass);


--
-- Name: response_times id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.response_times ALTER COLUMN id SET DEFAULT nextval('public.response_times_id_seq'::regclass);


--
-- Name: admin_questions admin_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_questions
    ADD CONSTRAINT admin_questions_pkey PRIMARY KEY (id);


--
-- Name: admins admins_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_email_key UNIQUE (email);


--
-- Name: admins admins_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (id);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: dept_keywords dept_keywords_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dept_keywords
    ADD CONSTRAINT dept_keywords_pkey PRIMARY KEY (id);


--
-- Name: file_knowledge file_knowledge_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_knowledge
    ADD CONSTRAINT file_knowledge_pkey PRIMARY KEY (id);


--
-- Name: response_times response_times_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.response_times
    ADD CONSTRAINT response_times_pkey PRIMARY KEY (id);


--
-- Name: text_knowledge text_knowledge_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.text_knowledge
    ADD CONSTRAINT text_knowledge_pkey PRIMARY KEY (id);


--
-- Name: user_questions user_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_questions
    ADD CONSTRAINT user_questions_pkey PRIMARY KEY (id);


--
-- Name: idx_response_times_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_response_times_timestamp ON public.response_times USING btree ("timestamp");


--
-- Name: dept_keywords dept_keywords_dept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dept_keywords
    ADD CONSTRAINT dept_keywords_dept_id_fkey FOREIGN KEY (dept_id) REFERENCES public.departments(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict c4eJ4Ai3j34wwPsJudMlCXjkpk04r56m4JwQDbd9JcgeOgeDknGXKe95Y4lIeXQ

