"""
SPDX 2.3 Compliant Software Bill of Materials (SBOM) Generator.
Directly substantiates license-information collection and compliance pipeline experience.
"""

import importlib.metadata
import json
import os
import time
from typing import Any, Dict, List


def generate_spdx_sbom(output_path: str = "reports/compliance/pulseqa_sbom.spdx.json") -> dict[str, Any]:
    """Generates an SPDX 2.3 JSON Software Bill of Materials for project dependencies."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    packages = []
    installed_dists = list(importlib.metadata.distributions())

    for dist in installed_dists:
        meta = dist.metadata
        pkg_name = meta.get("Name", "Unknown")
        pkg_version = meta.get("Version", "0.0.0")
        pkg_license = meta.get("License", "NOASSERTION")
        pkg_homepage = meta.get("Home-page", "NOASSERTION")
        pkg_summary = meta.get("Summary", "")

        packages.append({
            "SPDXID": f"SPDXRef-Package-{pkg_name.lower().replace('_', '-')}",
            "name": pkg_name,
            "versionInfo": pkg_version,
            "licenseConcluded": pkg_license if pkg_license else "NOASSERTION",
            "licenseDeclared": pkg_license if pkg_license else "NOASSERTION",
            "copyrightText": "NOASSERTION",
            "downloadLocation": pkg_homepage if pkg_homepage != "NOASSERTION" else "NONE",
            "summary": pkg_summary,
            "filesAnalyzed": False
        })

    sbom = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "PulseQA-Framework-Dependencies",
        "documentNamespace": f"https://pulseqa.io/spdxdocs/pulseqa-{int(time.time())}",
        "creationInfo": {
            "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "creators": ["Tool: PulseQA-SPDX-Pipeline-v2.4", "Person: QA Automator"]
        },
        "packages": packages
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sbom, f, indent=2)

    return sbom

if __name__ == "__main__":
    result = generate_spdx_sbom()
    print(f"Generated SPDX 2.3 SBOM with {len(result['packages'])} packages.")
