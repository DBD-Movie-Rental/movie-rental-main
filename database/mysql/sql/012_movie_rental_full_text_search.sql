USE movie_rental;

-- -----------------------------------------------------
-- Full Text Search (FTS) Indexes
-- Optimization for searching movies
-- -----------------------------------------------------

CREATE FULLTEXT INDEX idx_movie_title_fts ON movie(title);

-- -----------------------------------------------------
-- QUERIES FOR REPORT COMPARISON
-- -----------------------------------------------------

-- 1. The "Naive" Approach (Standard SQL)
-- This forces the database to scan every row (Full Table Scan) to find matches.
-- Run this to see the execution plan and timing:

-- EXPLAIN ANALYZE SELECT * FROM movie WHERE title LIKE '%Godfather%';

-- 2. The "Optimized" Approach (Full Text Search)
-- This uses the index to jump directly to the results.
-- Run this to see the execution plan and timing:

-- EXPLAIN ANALYZE SELECT * FROM movie WHERE MATCH(title) AGAINST('Godfather');
