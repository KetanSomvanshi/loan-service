CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- public."user" definition

-- Drop table

-- DROP TABLE public."user";

CREATE TABLE public."user" (
	id serial4 NOT NULL,
	created_at timestamptz NOT NULL,
	updated_at timestamptz NOT NULL DEFAULT now(),
	is_deleted bool NOT NULL DEFAULT false,
	uuid uuid NOT NULL DEFAULT uuid_generate_v4(),
	first_name varchar(255) NOT NULL,
	last_name varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
	"role" varchar(20) NOT NULL,
	password_hash varchar(255) NOT NULL,
	CONSTRAINT user_pk PRIMARY KEY (id),
	CONSTRAINT user_un UNIQUE (uuid),
	CONSTRAINT user_unique_email UNIQUE (email)
);


-- public.loan definition

-- Drop table

-- DROP TABLE public.loan;

CREATE TABLE public.loan (
	id serial4 NOT NULL,
	created_at timestamptz NOT NULL,
	updated_at timestamptz NOT NULL DEFAULT now(),
	is_deleted bool NOT NULL DEFAULT false,
	uuid uuid NOT NULL DEFAULT uuid_generate_v4(),
	amount float8 NULL,
	status varchar(20) NULL,
	customer_id int4 NOT NULL,
	"date" date NULL,
	terms int4 NULL,
	CONSTRAINT loan_pk PRIMARY KEY (id),
	CONSTRAINT loan_un UNIQUE (uuid),
	CONSTRAINT loan_fk FOREIGN KEY (customer_id) REFERENCES public."user"(id)
);


-- public.repayment definition

-- Drop table

-- DROP TABLE public.repayment;

CREATE TABLE public.repayment (
	id serial4 NOT NULL,
	created_at timestamptz NOT NULL,
	updated_at timestamptz NOT NULL DEFAULT now(),
	is_deleted bool NOT NULL DEFAULT false,
	uuid uuid NOT NULL DEFAULT uuid_generate_v4(),
	amount float8 NULL,
	status varchar(20) NULL,
	loan_id int4 NOT NULL,
	"date" date NULL,
	CONSTRAINT repayment_pk PRIMARY KEY (id),
	CONSTRAINT repayment_un UNIQUE (uuid),
	CONSTRAINT repayment_fk FOREIGN KEY (loan_id) REFERENCES public.loan(id)
);