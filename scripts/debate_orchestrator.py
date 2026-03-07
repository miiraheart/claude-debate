#!/usr/bin/env python3
"""
Debate session orchestrator — manages state, file I/O, and phase transitions.

This is the backbone script that the SKILL.md orchestrator calls between phases.
Each session gets a timestamped directory under /tmp/debate-sessions/ (e.g.
/tmp/debate-sessions/debate-20260304-143022/). A symlink at /tmp/debate-session
always points to the latest session. Previous sessions are preserved.

Provides utilities for the prompt-relay architecture (from Mysti: no direct
agent-to-agent communication).

Usage:
    python3 debate_orchestrator.py init <query>
    python3 debate_orchestrator.py detect-domain <query>
    python3 debate_orchestrator.py select-personas <domain>
    python3 debate_orchestrator.py set-personas '[{"name": "...", "description": "..."}]'
    python3 debate_orchestrator.py summarize-research
    python3 debate_orchestrator.py check-duplicates
    python3 debate_orchestrator.py compile-synthesis
    python3 debate_orchestrator.py update-state '{"key": "value"}'
    python3 debate_orchestrator.py issue-tracker init "Topic text"
    python3 debate_orchestrator.py issue-tracker update '{"resolved": [...], "open": [...], "stalled": [...]}'
    python3 debate_orchestrator.py status
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

DEBATE_BASE = Path("/tmp/debate-sessions")
SYMLINK_PATH = Path("/tmp/debate-session")  # always points to latest session


def _resolve_session_dir() -> Path:
    """Resolve current session directory from symlink or create base."""
    if SYMLINK_PATH.is_symlink():
        return SYMLINK_PATH.resolve()
    if SYMLINK_PATH.is_dir():
        return SYMLINK_PATH
    print("WARNING: No active debate session found at /tmp/debate-session. "
          "Run 'init' first or ensure debate-output/ exists.", file=sys.stderr)
    return DEBATE_BASE / "no-session"


SESSION_DIR = _resolve_session_dir()
STATE_FILE = SESSION_DIR / "state.json"

DEFAULT_AGREEMENT_INTENSITY = 9


# Domain detection keywords
DOMAIN_KEYWORDS = {
    "health": ["pain", "ergonomic", "posture", "health", "medical", "therapy",
               "back", "joint", "sleep", "lumbar", "support", "orthopedic",
               "spine", "comfort", "relief", "wellness", "muscle"],
    "technology": ["computer", "phone", "keyboard", "monitor", "laptop", "gaming",
                   "processor", "wireless", "bluetooth", "usb", "mechanical",
                   "programming", "coding", "developer", "screen", "display",
                   "headphone", "speaker", "audio", "microphone", "camera"],
    "home": ["sofa", "chair", "desk", "mattress", "furniture", "room", "home",
             "kitchen", "bed", "couch", "table", "shelf", "storage", "office",
             "standing desk", "recliner", "sectional", "loveseat"],
    "consumer": ["buy", "best", "review", "product", "brand", "quality",
                 "price", "compare", "recommendation", "top", "rated",
                 "worth", "value", "alternative", "vs"],
}

# Persona sets per domain (from personas.md)
PERSONA_SETS = {
    "health": [
        ("Medical Professional", "You are a medical professional with clinical experience. You evaluate health products and claims based on peer-reviewed research, clinical trials, and evidence-based medicine. You cite PubMed studies and medical guidelines."),
        ("Ergonomics Specialist", "You are an ergonomics specialist who evaluates products for their impact on physical health, posture, and long-term musculoskeletal wellbeing. You reference biomechanical studies and occupational health standards."),
        ("Patient Advocate", "You are a patient advocate who has reviewed thousands of patient experiences with health-related products. You understand real-world usage patterns, compliance challenges, and accessibility needs."),
        ("Budget Strategist", "You are a financial analyst specializing in consumer purchases. You evaluate total cost of ownership, price-to-value ratios, warranty terms, resale value, and hidden costs. You reference price history data and market trends."),
        ("Contrarian Reviewer", "You are a critical reviewer who stress-tests popular recommendations. You actively look for overlooked flaws, astroturfed reviews, survivorship bias in testimonials, and marketing claims that don't hold up to scrutiny."),
    ],
    "technology": [
        ("Hardware Engineer", "You are a hardware engineer who evaluates electronic products based on component quality, thermal design, power efficiency, and manufacturing standards. You reference spec sheets, benchmark data, and teardown analyses."),
        ("Software/UX Analyst", "You are a software and user experience analyst. You evaluate technology products based on software quality, ecosystem integration, update history, and day-to-day usability. You reference long-term reviews and software changelogs."),
        ("Power User", "You are a power user and enthusiast who has extensively tested products in the category. You know the edge cases, the hidden settings, the community mods, and the real-world performance that differs from marketing claims."),
        ("Budget Strategist", "You are a financial analyst specializing in consumer purchases. You evaluate total cost of ownership, price-to-value ratios, warranty terms, resale value, and hidden costs. You reference price history data and market trends."),
        ("Contrarian Reviewer", "You are a critical reviewer who stress-tests popular recommendations. You actively look for overlooked flaws, astroturfed reviews, survivorship bias in testimonials, and marketing claims that don't hold up to scrutiny."),
    ],
    "home": [
        ("Materials Scientist", "You are a materials scientist who evaluates products based on material composition, durability testing, chemical safety, and manufacturing quality. You reference ASTM standards, BIFMA certifications, and material data sheets."),
        ("Interior Design Professional", "You are an interior designer with experience selecting furniture and home products for diverse clients. You evaluate aesthetics, space efficiency, style versatility, and how products integrate into real living spaces."),
        ("Comfort Specialist", "You are a comfort and ergonomics specialist for home furnishings. You evaluate support, firmness, material breathability, and long-term comfort based on body mechanics and material science."),
        ("Budget Strategist", "You are a financial analyst specializing in consumer purchases. You evaluate total cost of ownership, price-to-value ratios, warranty terms, resale value, and hidden costs. You reference price history data and market trends."),
        ("Contrarian Reviewer", "You are a critical reviewer who stress-tests popular recommendations. You actively look for overlooked flaws, astroturfed reviews, survivorship bias in testimonials, and marketing claims that don't hold up to scrutiny."),
    ],
    "consumer": [
        ("Product Analyst", "You are a product analyst specializing in consumer goods. You evaluate products based on build quality, materials, durability, and value for money. You reference teardown analyses, lab testing data, and manufacturer specs."),
        ("Domain Expert", "You are a domain expert for the product category in question. You have deep knowledge of the technical specifications, industry standards, and performance benchmarks that matter most. You cite specific measurements and test results."),
        ("User Experience Researcher", "You are a UX researcher who synthesizes real user feedback at scale. You analyze review patterns across platforms (Amazon, Reddit, specialized forums), identify common complaints and praise points, and weight feedback by reviewer credibility."),
        ("Budget Strategist", "You are a financial analyst specializing in consumer purchases. You evaluate total cost of ownership, price-to-value ratios, warranty terms, resale value, and hidden costs. You reference price history data and market trends."),
        ("Contrarian Reviewer", "You are a critical reviewer who stress-tests popular recommendations. You actively look for overlooked flaws, astroturfed reviews, survivorship bias in testimonials, and marketing claims that don't hold up to scrutiny."),
    ],
    "general": [
        ("Generalist Researcher", "You are a thorough generalist researcher. You approach topics with intellectual curiosity and methodical rigor, cross-referencing multiple authoritative sources."),
        ("Domain Expert", "You are a domain expert for the product category in question. Adapt your expertise to the specific domain of the query."),
        ("User Experience Researcher", "You are a UX researcher who synthesizes real user feedback at scale. You analyze review patterns across platforms (Amazon, Reddit, specialized forums), identify common complaints and praise points, and weight feedback by reviewer credibility."),
        ("Budget Strategist", "You are a financial analyst specializing in consumer purchases. You evaluate total cost of ownership, price-to-value ratios, warranty terms, resale value, and hidden costs. You reference price history data and market trends."),
        ("Contrarian Reviewer", "You are a critical reviewer who stress-tests popular recommendations. You actively look for overlooked flaws, astroturfed reviews, survivorship bias in testimonials, and marketing claims that don't hold up to scrutiny."),
    ],
}


def init_session(query: str, mode: str = "product") -> dict:
    """Initialize a new debate session with timestamped directory."""
    global SESSION_DIR, STATE_FILE

    # Create timestamped session directory (preserves previous sessions)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    SESSION_DIR = DEBATE_BASE / f"debate-{timestamp}"
    STATE_FILE = SESSION_DIR / "state.json"

    DEBATE_BASE.mkdir(parents=True, exist_ok=True)

    # Create directory structure
    for subdir in ["phase1", "phase2", "phase3", "phase4", "phase5", "phase6"]:
        (SESSION_DIR / subdir).mkdir(parents=True, exist_ok=True)

    # Update symlink to point to latest session
    if SYMLINK_PATH.is_symlink():
        SYMLINK_PATH.unlink()
    elif SYMLINK_PATH.exists():
        import shutil
        shutil.rmtree(SYMLINK_PATH)
    SYMLINK_PATH.symlink_to(SESSION_DIR)

    domain = detect_domain(query)
    persona_set = PERSONA_SETS.get(domain, PERSONA_SETS["general"])

    state = {
        "query": query,
        "mode": mode,
        "domain": domain,
        "session_dir": str(SESSION_DIR),
        "created_at": datetime.now().isoformat(),
        "phase": "initialized",
        "agents": [],
        "agent_count": len(persona_set),
        "products": {},
        "eliminated": [],
        "finalists": [],
        "winner": None,
        "runner_up": None,
        "cumulative_votes": {},
        "convergence_history": [],
        "agreement_intensity": DEFAULT_AGREEMENT_INTENSITY,
    }

    STATE_FILE.write_text(json.dumps(state, indent=2))
    return state


def detect_domain(query: str) -> str:
    """Detect query domain from keywords."""
    query_lower = query.lower()
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        scores[domain] = sum(1 for kw in keywords if kw in query_lower)

    if not any(scores.values()):
        return "general"

    return max(scores, key=lambda k: scores[k])


def select_personas(domain: str) -> list[dict]:
    """Select personas for the detected domain from predefined sets."""
    persona_set = PERSONA_SETS.get(domain, PERSONA_SETS["general"])
    personas = [{"name": name, "description": desc, "agent_id": i + 1}
                for i, (name, desc) in enumerate(persona_set)]

    update_state({"agents": personas, "agent_count": len(personas)})
    return personas


def set_personas(personas_json: str) -> list[dict]:
    """
    Save arbitrary personas to state.

    Accepts a JSON array of persona objects with at minimum a 'name' and
    'description' field. Agent IDs are assigned by position if not provided.

    Example input:
        '[{"name": "Scientist", "description": "You are a scientist..."}]'
    """
    raw = json.loads(personas_json)
    personas = []
    for i, p in enumerate(raw):
        persona = {
            "name": p["name"],
            "description": p.get("description", ""),
            "stance": p.get("stance", ""),
            "role": p.get("role", "balanced"),
            "agent_id": p.get("agent_id", i + 1),
        }
        personas.append(persona)

    update_state({"agents": personas, "agent_count": len(personas)})
    return personas


def get_state() -> dict:
    """Load current session state."""
    if not STATE_FILE.exists():
        return {"error": "No active session. Run 'init' first."}
    return json.loads(STATE_FILE.read_text())


def update_state(updates: dict) -> dict:
    """Update session state."""
    state = get_state()
    state.update(updates)
    STATE_FILE.write_text(json.dumps(state, indent=2))
    return state


def summarize_research() -> dict:
    """Summarize Phase 1 research results — extract all product picks."""
    phase1_dir = SESSION_DIR / "phase1"
    agent_files = sorted(phase1_dir.glob("agent-*.md"))

    all_products = {}
    per_agent = {}

    for f in agent_files:
        text = f.read_text()
        agent_id = f.stem

        # Extract product names from headers like "### 1. Product Name" or "**Name**: Product"
        picks = []
        name_patterns = [
            re.compile(r'###\s*\d+\.\s*(.+)', re.MULTILINE),
            re.compile(r'\*?\*?Name\*?\*?[:\s]+(.+)', re.MULTILINE),
            re.compile(r'##\s*(?:Top Pick|Pick)\s*\d*[:\s]*(.+)', re.MULTILINE),
        ]
        for pattern in name_patterns:
            matches = pattern.findall(text)
            picks.extend([m.strip().strip('*') for m in matches])

        per_agent[agent_id] = picks
        for p in picks:
            normalized = p.lower().strip()
            if normalized not in all_products:
                all_products[normalized] = {"name": p, "mentioned_by": []}
            all_products[normalized]["mentioned_by"].append(agent_id)

    return {
        "total_unique_products": len(all_products),
        "products": all_products,
        "per_agent": per_agent,
    }


def _normalize_product(name: str) -> str:
    """Normalize a product name for comparison.
    Strips markdown, extra whitespace, and common suffixes."""
    name = re.sub(r'\*+', '', name)
    name = re.sub(r'\s+', ' ', name).strip().lower()
    for suffix in [' mattress', ' sofa', ' chair', ' bed', ' headphones']:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()
    return name


def _is_fuzzy_match(a: str, b: str) -> bool:
    """Check if two product names are likely the same product.
    Uses containment check and word overlap threshold."""
    na, nb = _normalize_product(a), _normalize_product(b)
    if na == nb:
        return True
    if na in nb or nb in na:
        return True
    words_a = set(na.split())
    words_b = set(nb.split())
    if not words_a or not words_b:
        return False
    overlap = len(words_a & words_b) / min(len(words_a), len(words_b))
    return overlap >= 0.7


def extract_position(text: str) -> str:
    """Extract the product pick from an agent's response.
    Looks for 'My Pick:', 'PICK:', 'recommend', 'champion' patterns."""
    pick_patterns = [
        re.compile(r'\*{0,2}(?:My Pick|PICK|Winner)\*{0,2}\s*:\s*\*{0,2}(.+?)\*{0,2}\s*$', re.IGNORECASE | re.MULTILINE),
        re.compile(r'\b(?:recommend|champion)\s*:\s*\*{0,2}(.+?)\*{0,2}\s*$', re.IGNORECASE | re.MULTILINE),
        re.compile(r'I (?:still )?(?:support|recommend|pick|choose|advocate)\s+\*{0,2}(.+?)\*{0,2}\s*$', re.IGNORECASE | re.MULTILINE),
    ]
    for pattern in pick_patterns:
        match = pattern.search(text)
        if match:
            return match.group(1).strip().strip('*').strip()
    return ""


def check_duplicates(output_dir: str = "debate-output") -> dict:
    """Check Phase 2 opening statements for duplicate product picks.
    Uses fuzzy matching to catch near-duplicates like
    'Sony WH-1000XM5' vs 'Sony WH-1000XM5 Headphones'."""
    phase2_dir = Path(output_dir) / "phase2"
    if not phase2_dir.exists():
        phase2_dir = SESSION_DIR / "phase2"
    files = sorted(phase2_dir.glob("agent-*.md"))

    picks = {}
    for f in files:
        text = f.read_text()
        agent_id = f.stem
        position = extract_position(text)
        picks[agent_id] = position

    seen = {}
    duplicates = []
    for agent_id, pick in picks.items():
        matched = False
        for seen_pick, seen_agent in seen.items():
            if _is_fuzzy_match(pick, seen_pick):
                duplicates.append({
                    "agent": agent_id,
                    "pick": pick,
                    "conflicts_with": seen_agent,
                    "matched_pick": seen_pick,
                })
                matched = True
                break
        if not matched:
            seen[pick] = agent_id

    return {
        "picks": picks,
        "duplicates": duplicates,
        "has_duplicates": len(duplicates) > 0,
    }


def compile_synthesis(output_dir: str = "debate-output") -> dict:
    """Gather all evidence needed for Phase 6 synthesis."""
    state = get_state()
    out_path = Path(output_dir)

    evidence = {
        "query": state["query"],
        "winner": state.get("winner"),
        "runner_up": state.get("runner_up"),
        "eliminated": state.get("eliminated", []),
        "convergence_history": state.get("convergence_history", []),
    }

    phase1_dir = SESSION_DIR / "phase1"
    evidence["research"] = {}
    if phase1_dir.exists():
        for f in sorted(phase1_dir.glob("agent-*.md")):
            evidence["research"][f.stem] = f.read_text()[:3000]

    phase4_dir = SESSION_DIR / "phase4"
    evidence["elimination_details"] = []
    if phase4_dir.exists():
        for elim_file in sorted(phase4_dir.rglob("elimination-results.json")):
            evidence["elimination_details"].append(json.loads(elim_file.read_text()))

    phase5_dir = out_path / "phase5"
    if not phase5_dir.exists():
        phase5_dir = SESSION_DIR / "phase5"
    for name in ["final-judgment.md", "final-verdict.md"]:
        verdict_file = phase5_dir / name
        if verdict_file.exists():
            evidence["judge_verdict"] = verdict_file.read_text()
            break

    jury_files = sorted(phase5_dir.glob("jury-*.md")) if phase5_dir.exists() else []
    evidence["jury_validations"] = [f.read_text() for f in jury_files]

    return evidence


def issue_tracker_init(topic: str, output_dir: str | None = None) -> str:
    """
    Initialize the issue tracker file.

    Creates issue-tracker.md in output_dir (defaults to debate-output/ in cwd,
    falling back to SESSION_DIR for backward compatibility).
    """
    target_dir = Path(output_dir) if output_dir else Path("debate-output")
    if not target_dir.exists():
        target_dir = SESSION_DIR

    content = f"""# Issue Tracker

**Topic**: {topic}
**Created**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## Resolved Issues

_None yet._

---

## Open Issues

_None yet._

---

## Stalled Issues

_None yet._
"""
    tracker_path = target_dir / "issue-tracker.md"
    tracker_path.write_text(content)
    return str(tracker_path)


def issue_tracker_update(updates_json: str, output_dir: str | None = None) -> str:
    """
    Update the issue tracker with new resolved/open/stalled lists.

    Accepts a JSON object:
        {
          "resolved": ["Issue A was settled", ...],
          "open": ["Still debating X", ...],
          "stalled": ["No progress on Y", ...]
        }

    Rewrites the relevant sections of issue-tracker.md.
    """
    updates = json.loads(updates_json)
    target_dir = Path(output_dir) if output_dir else Path("debate-output")
    tracker_path = target_dir / "issue-tracker.md"

    if not tracker_path.exists():
        tracker_path = SESSION_DIR / "issue-tracker.md"

    if not tracker_path.exists():
        return issue_tracker_init("(topic not set)", output_dir)

    existing = tracker_path.read_text()

    def _format_list(items: list[str]) -> str:
        if not items:
            return "_None._"
        return "\n".join(f"- {item}" for item in items)

    resolved = updates.get("resolved", [])
    open_issues = updates.get("open", [])
    stalled = updates.get("stalled", [])

    # Replace each section — keep header block intact
    def _replace_section(text: str, heading: str, new_body: str) -> str:
        pattern = re.compile(
            rf'(## {re.escape(heading)}\n)(.*?)(?=\n---|\Z)',
            re.DOTALL,
        )
        replacement = rf'\g<1>{new_body}\n'
        result, count = pattern.subn(replacement, text)
        if count == 0:
            result = text + f"\n## {heading}\n{new_body}\n"
        return result

    content = existing
    content = _replace_section(content, "Resolved Issues", _format_list(resolved))
    content = _replace_section(content, "Open Issues", _format_list(open_issues))
    content = _replace_section(content, "Stalled Issues", _format_list(stalled))

    tracker_path.write_text(content)
    return str(tracker_path)


def print_status():
    """Print current session status."""
    state = get_state()
    if "error" in state:
        print(state["error"])
        return

    print(f"Query: {state['query']}")
    print(f"Mode: {state.get('mode', 'product')}")
    print(f"Domain: {state['domain']}")
    print(f"Phase: {state['phase']}")
    print(f"Created: {state['created_at']}")
    if state.get('agents'):
        print(f"Agents: {len(state['agents'])} (count: {state.get('agent_count', '?')})")
    if state.get('products'):
        print(f"Products tracked: {len(state['products'])}")
    if state.get('eliminated'):
        print(f"Eliminated: {state['eliminated']}")
    if state.get('finalists'):
        print(f"Finalists: {state['finalists']}")
    if state.get('winner'):
        print(f"Winner: {state['winner']}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        query = " ".join(sys.argv[2:])
        mode = "product"
        # Support optional --mode flag: init --mode topic "query text"
        if len(sys.argv) > 3 and sys.argv[2] == "--mode":
            mode = sys.argv[3]
            query = " ".join(sys.argv[4:])
        result = init_session(query, mode=mode)
        print(json.dumps(result, indent=2))

    elif command == "detect-domain":
        query = " ".join(sys.argv[2:])
        domain = detect_domain(query)
        print(json.dumps({"query": query, "domain": domain}))

    elif command == "select-personas":
        domain = sys.argv[2] if len(sys.argv) > 2 else "general"
        personas = select_personas(domain)
        print(json.dumps(personas, indent=2))

    elif command == "set-personas":
        if len(sys.argv) < 3:
            print("Usage: set-personas '[{\"name\": \"...\", \"description\": \"...\"}]'")
            sys.exit(1)
        personas = set_personas(sys.argv[2])
        print(json.dumps(personas, indent=2))

    elif command == "summarize-research":
        result = summarize_research()
        print(json.dumps(result, indent=2))

    elif command == "check-duplicates":
        out_dir = "debate-output"
        for i, arg in enumerate(sys.argv):
            if arg == "--output-dir" and i + 1 < len(sys.argv):
                out_dir = sys.argv[i + 1]
        result = check_duplicates(output_dir=out_dir)
        print(json.dumps(result, indent=2))

    elif command == "compile-synthesis":
        out_dir = "debate-output"
        for i, arg in enumerate(sys.argv):
            if arg == "--output-dir" and i + 1 < len(sys.argv):
                out_dir = sys.argv[i + 1]
        result = compile_synthesis(output_dir=out_dir)
        evidence_dir = SESSION_DIR / "phase6"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "evidence.json").write_text(json.dumps(result, indent=2))
        print(json.dumps({"status": "compiled", "keys": list(result.keys())}))

    elif command == "update-state":
        if len(sys.argv) < 3:
            print("Usage: update-state '{\"key\": \"value\"}'")
            sys.exit(1)
        updates = json.loads(sys.argv[2])
        result = update_state(updates)
        print(json.dumps({"status": "updated", "phase": result.get("phase", "unknown")}))

    elif command == "issue-tracker":
        if len(sys.argv) < 3:
            print("Usage: issue-tracker init 'Topic' [--output-dir path] | issue-tracker update '{json}' [--output-dir path]")
            sys.exit(1)
        subcommand = sys.argv[2]
        out_dir = None
        for i, arg in enumerate(sys.argv):
            if arg == "--output-dir" and i + 1 < len(sys.argv):
                out_dir = sys.argv[i + 1]
        if subcommand == "init":
            remaining = [a for i, a in enumerate(sys.argv[3:], 3) if a != "--output-dir" and (i == 0 or sys.argv[i - 1] != "--output-dir")]
            topic = " ".join(remaining)
            path = issue_tracker_init(topic, out_dir)
            print(json.dumps({"status": "created", "path": path}))
        elif subcommand == "update":
            if len(sys.argv) < 4:
                print("Usage: issue-tracker update '{\"resolved\": [...], \"open\": [...], \"stalled\": [...]}'")
                sys.exit(1)
            path = issue_tracker_update(sys.argv[3], out_dir)
            print(json.dumps({"status": "updated", "path": path}))
        else:
            print(f"Unknown issue-tracker subcommand: {subcommand}")
            sys.exit(1)

    elif command == "status":
        print_status()

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)
