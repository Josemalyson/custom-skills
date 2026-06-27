# Contributing to Custom Skills

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Adding a New Skill](#adding-a-new-skill)
- [Improving Existing Skills](#improving-existing-skills)
- [Style Guidelines](#style-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

1. Check existing [issues](https://github.com/josemalyson/custom-skills/issues) first
2. Use the "Bug Report" issue template
3. Include reproduction steps, expected vs actual behavior

### Suggesting Features

1. Use the "Feature Request" issue template
2. Describe the problem and proposed solution
3. Include use cases

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test with your AI agent
5. Submit a pull request

## Adding a New Skill

### 1. Create the Skill Directory

```bash
mkdir my-skill-name
```

### 2. Create SKILL.md

The main skill definition file must include YAML frontmatter:

```markdown
---
name: my-skill-name
description: >
  Trigger phrases that activate this skill.
  Be specific about when it should activate.
  Use multiple phrases separated by commas.
---

# My Skill Name

## Overview

What this skill does and why it exists.

## When to Use

- Use case 1
- Use case 2

## Workflow

### Phase 1: Name
Description of the first phase.

### Phase 2: Name
Description of the second phase.

## Output

What the skill produces.

## References

- `references/file.md` — Description
```

### 3. Add Reference Documents

Create a `references/` directory with supporting materials:

```bash
mkdir my-skill-name/references
```

Each reference should be a Markdown file with:
- Clear title and purpose
- Structured content (tables, lists, code blocks)
- Examples where applicable

### 4. Test Your Skill

Before submitting:
- Test with Claude Code or your target AI agent
- Verify trigger phrases activate the skill
- Ensure all references load correctly
- Check output quality

### 5. Update Documentation

Add your skill to the README.md:
- Add to the Skills Overview table
- Include in the Project Structure tree
- Add a deep dive section if complex

## Improving Existing Skills

1. Open an issue first to discuss the change
2. Reference the skill name in the issue title
3. Explain what you want to improve and why
4. Submit a PR with the changes

## Style Guidelines

### Markdown

- Use clear headings (H1 for title, H2 for sections, H3 for subsections)
- Include code blocks with language tags
- Use tables for structured data
- Keep lines under 100 characters where possible

### Code

- Follow existing code style in the repository
- Add comments for complex logic
- Use meaningful variable/function names

### References

- Structure with clear sections
- Include examples and anti-patterns
- Cross-reference other documents where relevant

## Pull Request Process

1. **Title**: Use conventional commits format
   - `feat: add new skill for X`
   - `fix: correct trigger phrase in Y`
   - `docs: update installation guide`

2. **Description**: Explain what and why
   - What changes were made
   - Why the changes are needed
   - How to test them

3. **Checklist**:
   - [ ] SKILL.md follows the template
   - [ ] At least one reference document included
   - [ ] Tested with target AI agent
   - [ ] README.md updated
   - [ ] No breaking changes (or documented)

4. **Review**: Wait for maintainer review before merging

## Questions?

Open a [Discussion](https://github.com/josemalyson/custom-skills/discussions) if you have questions about contributing.

---

Thank you for helping make Custom Skills better!
