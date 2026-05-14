# Security Model — Supply Chain Security Scanner

## Defensive scope

This tool is a **defensive analysis tool**. It reads local project files and produces risk reports. It does not perform any offensive action.

## What the tool does

- Reads dependency manifest files from a user-supplied local path
- Compares declared package versions against a static vulnerability database
- Generates risk scores and reports

## What the tool does NOT do

- Does not execute dependencies or any code from the scanned project
- Does not download or install packages
- Does not scan remote systems
- Does not exfiltrate secrets or credentials
- Does not exploit any vulnerability it detects
- Does not modify any files in the scanned project
- Does not access the network by default (offline mode is the default)

## Threat model assumptions

- The user runs the scanner on a project they own or are authorized to assess
- The vulnerability database is a demonstration dataset; it does not represent live CVE data
- Reports may contain sensitive information about the project's dependency inventory — treat them accordingly

## Attack surface of the scanner itself

- **File parsing**: parsers handle potentially malformed manifest files. XML parsing (pom.xml) uses Python's standard library `xml.etree.ElementTree`, which is not vulnerable to XXE by default in modern Python. JSON and TOML parsing use standard library functions.
- **Network**: in offline mode (default), no network requests are made. In online mode, only the OSV API is contacted over HTTPS.
- **SQL**: all database operations use SQLAlchemy with parameterized queries. No raw SQL string interpolation.
- **HTML reports**: Jinja2 templates auto-escape user data. Package names and versions from dependency files are treated as untrusted data.

## Why the tool does not execute dependencies

Executing packages to analyze them would introduce a remote code execution risk — a malicious dependency could exploit the analysis environment. Static analysis of manifest files avoids this entirely.

## Responsible use

This tool must only be used on projects you own or are authorized to assess. Using it to enumerate vulnerabilities in a project without authorization may violate applicable laws.
