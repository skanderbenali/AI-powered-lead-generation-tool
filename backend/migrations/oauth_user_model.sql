-- Migration to add OAuth columns to users table

-- Add auth_provider enum type
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'authprovider') THEN
        CREATE TYPE authprovider AS ENUM ('local', 'google', 'github');
    END IF;
END
$$;

-- Add columns to users table
ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS auth_provider authprovider NOT NULL DEFAULT 'local',
    ADD COLUMN IF NOT EXISTS provider_user_id VARCHAR,
    ADD COLUMN IF NOT EXISTS avatar_url VARCHAR;

-- Update existing users to set auth_provider to 'local'
UPDATE users SET auth_provider = 'local' WHERE auth_provider IS NULL;

-- Make hashed_password nullable for OAuth users
ALTER TABLE users 
    ALTER COLUMN hashed_password DROP NOT NULL;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_users_auth_provider ON users (auth_provider);
CREATE INDEX IF NOT EXISTS idx_users_provider_user_id ON users (provider_user_id) WHERE provider_user_id IS NOT NULL;
