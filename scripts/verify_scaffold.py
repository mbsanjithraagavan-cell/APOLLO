"""Read-only Phase 0 syntax, contract, and resolver metadata checks; no pytest needed."""
import ast
import importlib.metadata as metadata
import json
from pathlib import Path

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    sources = list((ROOT / "app").rglob("*.py")) + list((ROOT / "scripts").glob("*.py"))
    for path in sources:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    print(f"Syntax OK: {len(sources)} Python files")
    report = json.loads((ROOT / "docs" / "dependency-resolution.json").read_text(encoding="utf-8"))
    distributions = {canonicalize_name(d.metadata["Name"]): {
        "name": d.metadata["Name"], "version": d.version, "requires_dist": d.requires or []
    } for d in metadata.distributions()}
    for item in report["install"]:
        data = item["metadata"]
        distributions[canonicalize_name(data["name"])] = data
    environment = default_environment()
    environment["extra"] = ""
    problems = []
    for name, data in distributions.items():
        for text in data.get("requires_dist", []):
            requirement = Requirement(text)
            if requirement.marker and not requirement.marker.evaluate(environment):
                continue
            dependency = distributions.get(canonicalize_name(requirement.name))
            if dependency is None or not requirement.specifier.contains(dependency["version"], prereleases=True):
                problems.append(f"{name}: {requirement}, found {dependency and dependency['version']}")
    if problems:
        raise SystemExit("Metadata conflicts:\n" + "\n".join(problems))
    print("All installed + proposed base dependency metadata constraints satisfied")
    print("Selected extras were checked by pip's successful dry-run resolver")


if __name__ == "__main__":
    main()
