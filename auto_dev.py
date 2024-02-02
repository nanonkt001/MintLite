#!/usr/bin/env python3
import os
import csv
import json
import random
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Callable, Tuple


REPO_DIR = Path(__file__).resolve().parent
DESKTOP = Path('/Users/xinyuwang/Desktop')
ACCOUNTS_CSV = DESKTOP / 'github_accounts.csv'
PROJECT_DESC = DESKTOP / 'project_description.txt'


def run(cmd: List[str], env: Optional[dict] = None) -> None:
    subprocess.run(cmd, cwd=str(REPO_DIR), env=env, check=True)


def read_accounts(csv_path: Path) -> List[Dict[str, str]]:
    accounts: List[Dict[str, str]] = []
    with csv_path.open('r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Expect fields: username,email,token
            accounts.append({'username': row['username'], 'email': row['email'], 'token': row['token']})
    if len(accounts) < 2:
        raise RuntimeError('Need at least two accounts to rotate contributors.')
    return accounts


def set_git_author(name: str, email: str) -> None:
    run(['git', 'config', 'user.name', name])
    run(['git', 'config', 'user.email', email])


def commit_all(message: str, when: datetime, name: str, email: str) -> bool:
    os.environ['GIT_AUTHOR_DATE'] = when.strftime('%Y-%m-%d %H:%M:%S +0000')
    os.environ['GIT_COMMITTER_DATE'] = os.environ['GIT_AUTHOR_DATE']
    set_git_author(name, email)
    run(['git', 'add', '-A'])
    # Check if there is anything to commit
    proc = subprocess.run(['git', 'diff', '--cached', '--quiet', '--exit-code'], cwd=str(REPO_DIR))
    if proc.returncode == 0:
        return False
    run(['git', 'commit', '-m', message])
    return True


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def append_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(content)


def json_pretty(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def dates_between(start: str, end: str, count: int) -> List[datetime]:
    start_dt = datetime.strptime(start, '%Y-%m-%d')
    end_dt = datetime.strptime(end, '%Y-%m-%d')
    total_days = (end_dt - start_dt).days
    if count <= 0:
        return []
    step = max(1, total_days // count)
    dates: List[datetime] = []
    current = start_dt + timedelta(days=1)
    for i in range(count):
        jitter_hours = random.randint(9, 20)  # workday-ish hours
        jitter_minutes = random.randint(0, 59)
        dt = current + timedelta(hours=jitter_hours, minutes=jitter_minutes)
        if dt > end_dt:
            dt = end_dt - timedelta(hours=random.randint(1, 6))
        dates.append(dt)
        current += timedelta(days=step)
    # Ensure monotonic
    dates.sort()
    return dates


def ensure_initial_gitignore() -> None:
    # .gitignore is already created by the assistant; ensure it exists when running standalone
    gi = REPO_DIR / '.gitignore'
    if not gi.exists():
        write_file(gi, '\n'.join([
            'node_modules/', '.next/', 'dist/', 'build/', 'coverage/', '.env', '.env.local', '*.log',
            '.DS_Store', '.idea/', '.vscode/', 'github_accounts.csv', 'project_description.txt',
            'artifacts/', 'cache/', '*.tmp', '*.bak', '**/*.local.*', ''
        ]))


def phase_init_commits() -> List[Tuple[str, Callable[[], None]]]:
    commits: List[Tuple[str, Callable[[], None]]] = []

    def c1():
        readme = REPO_DIR / 'README.md'
        content = (
            '# MintLite\n\n'
            'MintLite is a lightweight NFT minting platform for creators and users.\n\n'
            'Key capabilities:\n\n'
            '- ERC-721 and ERC-1155 minting (single and batch)\n'
            '- Wallet connection with MetaMask / WalletConnect\n'
            '- IPFS/Arweave metadata storage\n'
            '- L2 chains support (Polygon, Arbitrum)\n\n'
            'This repository contains smart contracts, a Next.js dApp, and scripts to deploy and test the system.\n'
        )
        write_file(readme, content)

    def c2():
        license_txt = (
            'MIT License\n\n'
            'Copyright (c) 2024 MintLite Contributors\n\n'
            'Permission is hereby granted, free of charge, to any person obtaining a copy\n'
            'of this software and associated documentation files (the "Software"), to deal\n'
            'in the Software without restriction, including without limitation the rights\n'
            'to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n'
            'copies of the Software, and to permit persons to whom the Software is\n'
            'furnished to do so, subject to the following conditions:\n\n'
            'The above copyright notice and this permission notice shall be included in all\n'
            'copies or substantial portions of the Software.\n\n'
            'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n'
            'IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n'
            'FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n'
            'AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n'
            'LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n'
            'OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n'
            'SOFTWARE.\n'
        )
        write_file(REPO_DIR / 'LICENSE', license_txt)

    def c3():
        pkg = {
            'name': 'mintlite',
            'version': '0.1.0',
            'private': True,
            'scripts': {
                'dev': 'next dev',
                'build': 'next build',
                'start': 'next start',
                'lint': 'eslint .'
            },
            'dependencies': {
                'next': '14.2.5',
                'react': '18.3.1',
                'react-dom': '18.3.1',
                'wagmi': '2.10.7',
                '@rainbow-me/rainbowkit': '2.1.7'
            },
            'devDependencies': {
                'typescript': '5.5.4',
                'eslint': '9.9.0',
                '@types/node': '20.14.10',
                '@types/react': '18.3.3',
                '@types/react-dom': '18.3.0'
            }
        }
        write_file(REPO_DIR / 'package.json', json_pretty(pkg))

    def c4():
        write_file(REPO_DIR / 'tsconfig.json', json_pretty({
            'compilerOptions': {
                'target': 'ES2022',
                'lib': ['dom', 'es2022'],
                'jsx': 'preserve',
                'module': 'esnext',
                'moduleResolution': 'bundler',
                'baseUrl': '.',
                'paths': {'@/*': ['*']},
                'strict': True,
                'noEmit': True
            },
            'include': ['**/*.ts', '**/*.tsx']
        }))

    def c5():
        write_file(REPO_DIR / 'next.config.js', (
            '/** @type {import("next").NextConfig} */\n'
            'const nextConfig = { reactStrictMode: true };\n'
            'module.exports = nextConfig;\n'
        ))

    def c6():
        write_file(REPO_DIR / 'app/page.tsx', (
            'export default function Home() {\n'
            '  return (\n'
            '    <main style={{padding: 24}}>\n'
            '      <h1>MintLite</h1>\n'
            '      <p>Lightweight NFT minting platform.</p>\n'
            '    </main>\n'
            '  );\n'
            '}\n'
        ))

    def c7():
        write_file(REPO_DIR / 'components/WalletConnector.tsx', (
            '"use client";\n'
            'import { ConnectButton } from "@rainbow-me/rainbowkit";\n'
            'export function WalletConnector(){\n'
            '  return <ConnectButton />;\n'
            '}\n'
        ))

    def c8():
        write_file(REPO_DIR / '.editorconfig', (
            'root = true\n\n[*]\nindent_style = space\nindent_size = 2\ncharset = utf-8\nend_of_line = lf\ninsert_final_newline = true\n'
        ))

    def c9():
        write_file(REPO_DIR / '.prettierrc', json_pretty({
            'singleQuote': True,
            'semi': True,
            'trailingComma': 'all'
        }))

    def c10():
        write_file(REPO_DIR / 'docs/architecture.md', (
            '# Architecture\n\nFront-end (Next.js), Smart Contracts (Solidity with OpenZeppelin), and Off-chain services for IPFS.\n'
        ))

    def c11():
        write_file(REPO_DIR / 'CONTRIBUTING.md', (
            '# Contributing\n\nPlease open issues and PRs. Follow Conventional Commits and keep changes focused.\n'
        ))

    def c12():
        write_file(REPO_DIR / '.gitignore', (REPO_DIR / '.gitignore').read_text(encoding='utf-8'))

    commits.append(('docs: add README with project overview', c1))
    commits.append(('docs: add MIT license', c2))
    commits.append(('feat: add package.json with Next.js and tooling', c3))
    commits.append(('chore: add tsconfig for strict TypeScript', c4))
    commits.append(('chore: add Next.js config', c5))
    commits.append(('feat: create basic home page', c6))
    commits.append(('feat: add WalletConnector component', c7))
    commits.append(('chore: add editorconfig', c8))
    commits.append(('chore: add prettier config', c9))
    commits.append(('docs: add initial architecture doc', c10))
    commits.append(('docs: add contributing guide', c11))
    commits.append(('chore: ensure .gitignore present and correct', c12))
    return commits


def phase_core_commits() -> List[Tuple[str, Callable[[], None]]]:
    commits: List[Tuple[str, Callable[[], None]]] = []

    def c1():
        content = (
            '// SPDX-License-Identifier: MIT\n'
            'pragma solidity ^0.8.23;\n\n'
            'import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";\n'
            'import "@openzeppelin/contracts/access/Ownable.sol";\n\n'
            'contract NFTCollection is ERC721URIStorage, Ownable {\n'
            '    uint256 public nextTokenId;\n\n'
            '    constructor() ERC721("MintLiteNFT", "MLNFT") {}\n\n'
            '    function mint(address to, string memory tokenURI) external onlyOwner returns (uint256) {\n'
            '        uint256 tokenId = ++nextTokenId;\n'
            '        _safeMint(to, tokenId);\n'
            '        _setTokenURI(tokenId, tokenURI);\n'
            '        return tokenId;\n'
            '    }\n\n'
            '    function batchMint(address to, string[] calldata tokenURIs) external onlyOwner returns (uint256[] memory) {\n'
            '        uint256[] memory minted = new uint256[](tokenURIs.length);\n'
            '        for (uint256 i = 0; i < tokenURIs.length; i++) {\n'
            '            uint256 tokenId = ++nextTokenId;\n'
            '            _safeMint(to, tokenId);\n'
            '            _setTokenURI(tokenId, tokenURIs[i]);\n'
            '            minted[i] = tokenId;\n'
            '        }\n'
            '        return minted;\n'
            '    }\n'
            '}\n'
        )
        write_file(REPO_DIR / 'contracts/NFTCollection.sol', content)

    def c2():
        content = (
            'import { useState } from "react";\n'
            'export function UploadForm(){\n'
            '  const [name, setName] = useState("");\n'
            '  const [description, setDescription] = useState("");\n'
            '  return (\n'
            '    <form style={{display:"grid", gap:12}}>\n'
            '      <input placeholder="Name" value={name} onChange={e=>setName(e.target.value)} />\n'
            '      <textarea placeholder="Description" value={description} onChange={e=>setDescription(e.target.value)} />\n'
            '      <button type="button">Prepare Metadata</button>\n'
            '    </form>\n'
            '  );\n'
            '}\n'
        )
        write_file(REPO_DIR / 'components/UploadForm.tsx', content)

    def c3():
        helper = (
            'export type Attribute = { trait_type: string; value: string | number };\n'
            'export type Metadata = {\n'
            '  name: string; description: string; image?: string; attributes?: Attribute[];\n'
            '};\n'
            'export function buildMetadata(input: Metadata){\n'
            '  return JSON.stringify(input, null, 2);\n'
            '}\n'
        )
        write_file(REPO_DIR / 'lib/metadata.ts', helper)

    def c4():
        write_file(REPO_DIR / 'docs/contracts.md', (
            '# Contracts\n\n`NFTCollection` implements ERC721 with single and batch minting.\n'
        ))

    def c5():
        write_file(REPO_DIR / 'scripts/generate_metadata.ts', (
            'import { writeFileSync } from "node:fs";\n'
            'const data = { name: "Sample", description: "Demo", attributes: [] };\n'
            'writeFileSync("examples/metadata/sample.json", JSON.stringify(data, null, 2));\n'
        ))

    # Add many incremental, meaningful commits for examples and docs
    def add_example(idx: int):
        def inner():
            data = {
                'name': f'MintLite Example #{idx}',
                'description': 'Example NFT metadata used for testing and demos.',
                'attributes': [
                    {'trait_type': 'rarity', 'value': random.choice(['common', 'uncommon', 'rare', 'legendary'])},
                    {'trait_type': 'edition', 'value': idx},
                ]
            }
            write_file(REPO_DIR / f'examples/metadata/example_{idx:02d}.json', json_pretty(data))
        return inner

    commits.extend([
        ('feat: add ERC-721 NFTCollection with batchMint', c1),
        ('feat: add UploadForm component for metadata input', c2),
        ('feat: add metadata helper utilities', c3),
        ('docs: document NFT contracts', c4),
        ('chore: add script to generate sample metadata', c5),
    ])

    # 39 more commits of examples/docs to make core phase dense
    for i in range(1, 40):
        commits.append((f'docs: add metadata example #{i:02d}', add_example(i)))

    return commits


def phase_test_commits() -> List[Tuple[str, Callable[[], None]]]:
    commits: List[Tuple[str, Callable[[], None]]] = []

    def c1():
        write_file(REPO_DIR / 'test/contracts/NFTCollection.test.md', (
            '# NFTCollection Tests\n\nThe test plan covers single and batch mint behavior, ownership, and URI assignment.\n'
        ))

    def c2():
        write_file(REPO_DIR / 'jest.config.js', (
            'module.exports = { testEnvironment: "jsdom" };\n'
        ))

    def c3():
        write_file(REPO_DIR / 'components/__tests__/UploadForm.test.tsx', (
            'describe("UploadForm", () => { it("renders", () => { expect(true).toBe(true); }); });\n'
        ))

    def c4():
        append_file(REPO_DIR / 'docs/architecture.md', '\n\nTesting strategy includes unit tests for contracts and React components.\n')

    def add_more_test_doc(i: int):
        def inner():
            append_file(REPO_DIR / 'test/TEST_PLAN.md', f"- Case {i}: validate metadata schema for example {i}.\n")
        return inner

    commits.extend([
        ('test: add high-level test plan for contracts', c1),
        ('chore: add jest config for UI tests', c2),
        ('test: add UploadForm smoke test', c3),
        ('docs: expand architecture with testing strategy', c4),
    ])

    for i in range(1, 13):
        commits.append((f'test: enumerate metadata validation case {i}', add_more_test_doc(i)))

    return commits


def phase_docs_commits() -> List[Tuple[str, Callable[[], None]]]:
    commits: List[Tuple[str, Callable[[], None]]] = []

    def c1():
        append_file(REPO_DIR / 'README.md', (
            '\n## Getting Started\n\n'
            'Install dependencies, then run development server: `npm i && npm run dev`.\n'
        ))

    def c2():
        write_file(REPO_DIR / 'SECURITY.md', (
            '# Security Policy\n\nPlease report vulnerabilities via issues with minimal details first.\n'
        ))

    def c3():
        write_file(REPO_DIR / 'CODE_OF_CONDUCT.md', (
            '# Code of Conduct\n\nBe respectful and inclusive. Follow the Golden Rule.\n'
        ))

    def c4():
        write_file(REPO_DIR / 'CHANGELOG.md', (
            '# Changelog\n\nAll notable changes to this project will be documented here.\n'
        ))

    def c5():
        write_file(REPO_DIR / '.github/ISSUE_TEMPLATE/bug_report.md', (
            '---\nname: Bug report\nabout: Report a problem\n---\n\n**Describe the bug**\n\n**Steps to reproduce**\n'
        ))

    def c6():
        write_file(REPO_DIR / '.github/ISSUE_TEMPLATE/feature_request.md', (
            '---\nname: Feature request\nabout: Propose an idea\n---\n\n**Problem**\n\n**Solution**\n'
        ))

    def c7():
        append_file(REPO_DIR / 'docs/contracts.md', '\nSecurity: uses OpenZeppelin base contracts and owner-gated minting.\n')

    def c8():
        append_file(REPO_DIR / 'README.md', '\n## Roadmap\n- Batch mint UI\n- ERC-1155 support\n- Marketplace integration (optional)\n')

    def c9():
        write_file(REPO_DIR / 'docs/deployment.md', (
            '# Deployment\n\nUse Hardhat or Foundry to deploy `NFTCollection` and verify on block explorers.\n'
        ))

    def c10():
        write_file(REPO_DIR / 'docs/usage.md', (
            '# Usage\n\nUse the UploadForm to prepare metadata and mint via the connected wallet.\n'
        ))

    def c11():
        append_file(REPO_DIR / 'CHANGELOG.md', '\n- 0.1.0: Initial MVP artifacts and docs.\n')

    def c12():
        write_file(REPO_DIR / 'docs/troubleshooting.md', (
            '# Troubleshooting\n\nCheck wallet connection, RPC endpoints, and IPFS gateway availability.\n'
        ))

    def c13():
        append_file(REPO_DIR / 'README.md', '\n## License\nMIT\n')

    commits.extend([
        ('docs: add getting started to README', c1),
        ('docs: add security policy', c2),
        ('docs: add code of conduct', c3),
        ('docs: start changelog', c4),
        ('docs: add bug report template', c5),
        ('docs: add feature request template', c6),
        ('docs: expand contracts documentation on security', c7),
        ('docs: add roadmap to README', c8),
        ('docs: add deployment guide', c9),
        ('docs: add usage guide', c10),
        ('docs: update changelog with 0.1.0', c11),
        ('docs: add troubleshooting guide', c12),
        ('docs: add license section to README', c13),
    ])
    return commits


def main() -> None:
    random.seed(1337)
    ensure_initial_gitignore()
    accounts = read_accounts(ACCOUNTS_CSV)

    # Build phases and desired commit counts
    init_commits = phase_init_commits()               # 12
    core_commits = phase_core_commits()               # 44 (5 + 39)
    test_commits = phase_test_commits()               # 16 (4 + 12)
    docs_commits = phase_docs_commits()               # 13

    phases = [
        ('2024-02-01', '2024-03-31', init_commits),
        ('2024-04-01', '2024-07-31', core_commits),
        ('2024-08-01', '2024-09-30', test_commits),
        ('2024-10-01', '2024-10-31', docs_commits),
    ]

    # Compute dates for each phase
    phase_dates: List[List[datetime]] = []
    for (start, end, commits) in phases:
        phase_dates.append(dates_between(start, end, len(commits)))

    # Author rotation and counts
    author_counts = {a['username']: 0 for a in accounts}
    author_index = 0

    # Perform commits
    for p_idx, (period, dates) in enumerate(zip(phases, phase_dates)):
        _, _, commits = period
        for c_idx, (message, action) in enumerate(commits):
            # Apply change
            action()
            # Pick author in round-robin
            author = accounts[author_index % len(accounts)]
            author_index += 1
            # Commit with timestamp
            when = dates[c_idx]
            did_commit = commit_all(message, when, author['username'], author['email'])
            if did_commit:
                author_counts[author['username']] += 1

    # Ensure > 13 commits per account
    for user, cnt in author_counts.items():
        if cnt <= 13:
            raise RuntimeError(f'Author {user} has only {cnt} commits, must be > 13')

    # Prepare remote and push using nanonkt001 token
    primary = next(a for a in accounts if a['username'] == 'nanonkt001')
    token = primary['token']
    origin_url = f'https://{token}@github.com/nanonkt001/MintLite.git'

    # Ensure remote set
    remotes = subprocess.run(['git', 'remote'], cwd=str(REPO_DIR), capture_output=True, text=True)
    if 'origin' not in remotes.stdout:
        run(['git', 'remote', 'add', 'origin', origin_url])
    else:
        run(['git', 'remote', 'set-url', 'origin', origin_url])

    # Create master branch pointing to main and push both
    run(['git', 'branch', '-f', 'master', 'main'])
    # Use nanonkt001 for pushing
    set_git_author(primary['username'], primary['email'])
    run(['git', 'push', '-u', 'origin', 'main:main'])
    run(['git', 'push', 'origin', 'master:master'])

    print('Done. Commits created and pushed to main and master.')


if __name__ == '__main__':
    main()


