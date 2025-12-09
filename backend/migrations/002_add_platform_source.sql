-- Migration: 002_add_platform_source
-- Description: Add platform_source field to distinguish broker/private/blacklist platforms
-- Created: 2024-12-09
-- Status: Pending

-- Note: This migration adds the platform_source field for categorizing platforms:
-- - 券商平台: Regulated broker platforms (securities firms with margin trading)
-- - 民间平台: Private/third-party platforms
-- - 黑名单: Blacklisted/risky platforms (with warning indicators)

-- Add platform_source column with default value
ALTER TABLE platforms ADD COLUMN platform_source VARCHAR(50) DEFAULT '民间平台' NOT NULL;

-- Create index for filtering by platform source
CREATE INDEX idx_platforms_platform_source ON platforms(platform_source);

-- Update comment (SQLite doesn't support comments, this is for documentation)
-- The platform_source field accepts: '券商平台', '民间平台', '黑名单'

