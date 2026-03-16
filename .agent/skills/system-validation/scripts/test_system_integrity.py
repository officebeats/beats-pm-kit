import os
import sys

def test_system_integrity():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    agents_dir = os.path.join(base, 'agents')
    workflows_dir = os.path.join(base, 'workflows')
    skills_dir = os.path.join(base, 'skills')
    rules_file = os.path.join(base, 'rules', 'GEMINI.md')
    project_root = os.path.abspath(os.path.join(base, '..'))
    
    errors = []
    
    # 1. Test Agents
    print('Testing Agents...')
    agents = [f for f in os.listdir(agents_dir) if f.endswith('.md')]
    if len(agents) == 0:
        errors.append('No agents found!')
    
    for agent in agents:
        with open(os.path.join(agents_dir, agent), 'r', encoding='utf-8') as f:
            content = f.read()
            if 'skills:' not in content:
                errors.append(f'Agent {agent} is missing skills array')
            
    # 2. Test Workflows
    print('Testing Workflows...')
    workflows = [f for f in os.listdir(workflows_dir) if f.endswith('.md')]
    core_wfs = {
        'boss.md', 'day.md', 'track.md', 'create.md',
        'plan.md', 'retro.md', 'fan-out.md', 'sprint.md',
        'discover.md', 'prioritize.md', 'paste.md', 'help.md', 'review.md',
        'data.md', 'launch.md', 'bug.md', 'feature-kickoff.md', 'regression.md',
        'reflect.md', 'kingmode.md'
    }
    
    missing_wfs = core_wfs - set(workflows)
    if missing_wfs:
        for wf in missing_wfs:
            errors.append(f'Core workflow {wf} is missing!')
    
    for wf in workflows:
        wf_path = os.path.join(workflows_dir, wf)
        if os.path.isfile(wf_path):
            with open(wf_path, 'r', encoding='utf-8') as f:
                if '```markdown\n#' in f.read():
                    errors.append(f'Workflow {wf} still contains embedded markdown templates.')
                
    # 3. Test Skills
    print('Testing Skills...')
    skills = [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
    for skill in skills:
        skill_path = os.path.join(skills_dir, skill)
        if not os.path.exists(os.path.join(skill_path, 'SKILL.md')):
             errors.append(f'Skill {skill} missing SKILL.md')
             
    # 4. Rules Integrity
    print('Testing Rules Anchor...')
    with open(rules_file, 'r', encoding='utf-8') as f:
        rules_text = f.read()
        if '## 🚀 TIER 0.5: THREE-TIER ARCHITECTURE' not in rules_text:
            errors.append('GEMINI.md missing the Three-Tier Architecture anchor.')

    # 5. Cross-CLI Adapter Validation
    print('Testing Cross-CLI Adapters...')
    
    # 5a. Folder aliases
    for alias in ['.agents', '_agent', '_agents']:
        alias_path = os.path.join(project_root, alias)
        if os.path.islink(alias_path) and os.path.exists(alias_path):
            pass  # Valid symlink
        elif os.path.isdir(alias_path):
            pass  # Real directory (also acceptable)
        else:
            errors.append(f'Folder alias {alias} is missing or broken. Run: python system/scripts/sync_cli_adapters.py')

    # 5b. CLI directory symlinks
    for cli_dir, subdirs in {'.kilocode': ['skills'], '.gemini': ['skills'], '.claude': ['commands']}.items():
        for subdir in subdirs:
            link_path = os.path.join(project_root, cli_dir, subdir)
            if os.path.exists(link_path):
                pass  # Exists (symlink or real)
            else:
                errors.append(f'{cli_dir}/{subdir} missing. Run: python system/scripts/sync_cli_adapters.py')

    # 5c. Config files
    claude_md = os.path.join(project_root, '.claude', 'CLAUDE.md')
    if os.path.exists(claude_md) and os.path.getsize(claude_md) > 100:
        pass  # Valid
    else:
        errors.append('CLAUDE.md missing or empty. Run: python system/scripts/sync_cli_adapters.py')

    agents_md = os.path.join(project_root, 'AGENTS.md')
    if os.path.exists(agents_md) and os.path.getsize(agents_md) > 100:
        pass  # Valid
    else:
        errors.append('AGENTS.md missing or empty. Run: python system/scripts/sync_cli_adapters.py')

    # ─── Results ─────────────────────────────────────────────────────────────
    print('\n--- TEST RESULTS ---')
    if errors:
        for err in errors:
            print(f'❌ ERROR: {err}')
        sys.exit(1)
    else:
        print('✅ ALL TESTS PASSED. System Integrity is at 100%.')
        print(f'Detected: {len(agents)} Agents, {len(workflows)} Workflows, {len(skills)} Skills.')

if __name__ == "__main__":
    test_system_integrity()

