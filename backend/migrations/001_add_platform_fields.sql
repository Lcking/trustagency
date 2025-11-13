-- Migration: 001_add_platform_fields
-- Description: Add new fields to platforms table for Bug fixes (Bug001, Bug002, Bug005)
-- Created: 2024-01-01
-- Status: Pending

-- Note: This migration adds the following fields to the platforms table:
-- Bug001 fixes: introduction, main_features, fee_structure, account_opening_link
-- Bug005 fixes: safety_rating, founded_year, fee_rate
-- Bug002 fixes: is_recommended
-- Improvement: slug (for URL-friendly identifiers)

-- Add new columns to platforms table
-- These columns are added with default values to avoid breaking existing data

-- Bug001: Platform introduction and details
ALTER TABLE platforms ADD COLUMN introduction TEXT;
ALTER TABLE platforms ADD COLUMN main_features TEXT;
ALTER TABLE platforms ADD COLUMN fee_structure TEXT;
ALTER TABLE platforms ADD COLUMN account_opening_link VARCHAR(500);

-- Bug005: Safety and history info
ALTER TABLE platforms ADD COLUMN safety_rating VARCHAR(10) DEFAULT 'B' NOT NULL;
ALTER TABLE platforms ADD COLUMN founded_year INTEGER;
ALTER TABLE platforms ADD COLUMN fee_rate FLOAT;

-- Bug002: Recommendation flag
ALTER TABLE platforms ADD COLUMN is_recommended BOOLEAN DEFAULT FALSE NOT NULL;

-- Improvement: URL-friendly slug for better routing
ALTER TABLE platforms ADD COLUMN slug VARCHAR(255) UNIQUE;

-- Create index on frequently queried fields
CREATE INDEX idx_platforms_slug ON platforms(slug);
CREATE INDEX idx_platforms_is_recommended ON platforms(is_recommended);
CREATE INDEX idx_platforms_safety_rating ON platforms(safety_rating);
