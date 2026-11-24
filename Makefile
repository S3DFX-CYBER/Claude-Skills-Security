SKILL     := skills/security-triage/SKILL.md
MIRROR    := .claude/skills/security-triage/SKILL.md

.PHONY: sync check cases

## Regenerate the Claude Code mirror from the canonical skill.
sync:
	@mkdir -p $(dir $(MIRROR))
	@cp $(SKILL) $(MIRROR)
	@echo "synced: $(MIRROR)"

## Fail if the mirror has drifted from the canonical skill.
check:
	@diff -q $(SKILL) $(MIRROR) && echo "skill copies in sync"
	@test -f evals/expected.yaml && echo "eval corpus present"

## List the eval cases and what each one tests.
cases:
	@grep -H "^# " evals/cases/*/README.md | sed 's|evals/cases/||;s|/README.md:# |  ->  |'
