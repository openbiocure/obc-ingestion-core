# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Test database directory fixture (`test_db_dir`) to create temporary directory for test database files
- Support for direct database connection string configuration
- Proper cleanup in `initialized_engine` fixture
- Comprehensive test cases for error handling and edge cases in Repository

### Changed
- Updated test configuration to use temporary database path
- Improved database context startup task to handle both connection string and individual parameters
- Modified `Engine.current()` test to properly await engine start
- Updated `Repository.update` method to handle both string IDs and entity objects
- Enhanced validation in TestEntity to properly raise SQLAlchemyError for null name

### Fixed
- Database path issues in CI environment
- SQLite database file access in tests
- Immutable fields handling in Repository updates
- Test startup tasks to utilize async execute methods
- RuntimeError: 'Engine not started' by ensuring proper engine initialization

### Improved
- Test coverage for repository operations
- Error handling in CRUD operations
- Edge case handling in find operations
- Documentation about the async startup process
