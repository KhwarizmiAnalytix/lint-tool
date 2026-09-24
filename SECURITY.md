# Security Policy

## Reporting Security Vulnerabilities

**Do not open public issues for security vulnerabilities.**

If you discover a security vulnerability in lint-tool, please email us directly at:

📧 **security@khwarizmianalytix.dev**

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt of your report within 48 hours and provide updates on our progress.

## Security Considerations

### 1. Linter Binary Execution

lint-tool executes external binaries (clang-format, clang-tidy, etc.) based on configuration.

**Security Practices:**
- Verify linter binaries come from trusted sources
- Use pinned versions in init_commands
- Consider running linters in isolated environments
- Audit `.lintrunner.toml` before execution

### 2. File System Access

Adapters read and potentially modify files based on include/exclude patterns.

**Security Practices:**
- Review pattern configurations carefully
- Avoid overly broad patterns (e.g., `**`)
- Use exclude patterns for sensitive directories
- Run with minimal necessary permissions

### 3. Configuration Files

`.lintrunner.toml` is read as untrusted input.

**Security Practices:**
- Keep configuration files in version control
- Review configuration changes in PRs
- Avoid embedding secrets in configuration
- Use environment variables for sensitive values

### 4. Third-Party Dependencies

lint-tool depends on several libraries.

**Security Practices:**
- Keep dependencies updated: `pip install --upgrade lint-tool`
- Review security advisories: `pip-audit`
- Report vulnerabilities in dependencies to maintainers

### 5. Environment Variables

Some adapters use environment variables (e.g., `DRYRUN`, tool-specific options).

**Security Practices:**
- Don't pass sensitive data via environment variables
- Sanitize user-provided environment values
- Document expected environment variables

## Supported Versions

Security updates are provided for:
- Latest minor version (e.g., 2026.9.x)
- One previous minor version (e.g., 2026.8.x)

## Dependency Management

### Automated Security Updates

We use:
- Dependabot for dependency monitoring
- GitHub Security Advisories
- OSINT feeds for emerging threats

### Regular Audits

- Monthly security audits
- Quarterly penetration testing considerations
- Continuous monitoring of CVE databases

## Best Practices for Users

### 1. Run lintrunner in CI/CD

```bash
# In GitHub Actions
lintrunner lint --all-files
```

### 2. Review lint configuration

```bash
# Audit your .lintrunner.toml
cat .lintrunner.toml

# Verify no overly broad patterns
grep include_patterns .lintrunner.toml
```

### 3. Keep tools updated

```bash
# Update lint-tool
pip install --upgrade lint-tool

# Update linter binaries
python3 -m lint_tool.adapters.pip_init --update
```

### 4. Minimal permissions

```bash
# Run lintrunner with minimal file access
# Avoid running as root/administrator
lintrunner lint
```

### 5. Monitor supply chain

```bash
# Check for vulnerable dependencies
pip install pip-audit
pip-audit
```

## Known Limitations

### Security Boundary

lint-tool is a **development tool**, not a security tool:
- Not suitable for cryptographic operations
- Not designed for privileged execution
- Assumes cooperative environment (trusted developers)
- Does not provide sandboxing

### Linter Limitations

Each external linter has its own security considerations:
- clang-tidy: May parse malformed C++ code
- ruff: May execute user code via plugins
- mypy: Imports modules for type analysis

Refer to each tool's security documentation.

## Responsible Disclosure

We appreciate security researchers who responsibly disclose vulnerabilities.

**Responsible Disclosure Process:**
1. Report to security@khwarizmianalytix.dev
2. Allow 90 days for patch development and testing
3. Coordinate disclosure timing with maintainers
4. Receive public credit in security advisory

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Supply Chain Security](https://slsa.dev/)

## Compliance

lint-tool aims to comply with:
- GPL-3.0-or-later licensing requirements
- OWASP secure coding practices
- CWE/SANS Top 25 vulnerability mitigation

## Questions?

- 🔒 Security concern: security@khwarizmianalytix.dev
- 📝 General questions: contact@khwarizmianalytix.dev
- 💬 Public discussions: [GitHub Discussions](https://github.com/KhwarizmiAnalytix/lint-tool/discussions)

---

**Last Updated:** 2026-09-24  
**Version:** lint-tool 2026.9.14+
