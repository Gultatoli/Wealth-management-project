# Vendored Skills — Attribution

This directory contains skills used by Claude Code sessions on this repository.

## superpowers (14 skills)

The following skills come from the **Superpowers** skills library:

- Source: https://github.com/obra/superpowers
- Version: 6.1.1
- Author: Jesse Vincent
- License: MIT

Skills: `brainstorming`, `dispatching-parallel-agents`, `executing-plans`,
`finishing-a-development-branch`, `receiving-code-review`, `requesting-code-review`,
`subagent-driven-development`, `systematic-debugging`, `test-driven-development`,
`using-git-worktrees`, `using-superpowers`, `verification-before-completion`,
`writing-plans`, `writing-skills`.

These are **not vendored into this repo**. They are fetched fresh from GitHub at
the start of each Claude Code on the web session by `.claude/hooks/session-start.sh`,
and are git-ignored (see `.gitignore`). This keeps the repository clean. Only the
skills are installed — the upstream plugin's own session-start hook (which
auto-injects the `using-superpowers` dispatcher) is not used; the skills remain
individually available and can be invoked directly.

### MIT License (Superpowers)

```
MIT License

Copyright (c) 2025 Jesse Vincent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## the-humanizer

Personal skill supplied by the repository owner. Reviews written content for
AI-generated patterns and rewrites in an authentic human voice.
