# patch_slaapp_v2.py — One-shot patcher for Advania_V2_PoC_AI_Verification_NET10_Upgrade.docx
# Applies: remove Swedish comments, renumber sections, ZDR red/green markup, estimates TBD, parallelism caveat
# Input:  /tmp/slaapp_v2/ (extracted docx contents)
# Output: Downloads/Advania_V2_PoC_AI_Verification_NET10_Upgrade_REVISED.docx
# Status: Completed 2026-04-14. Single-use — do not rerun without re-extracting source.

import sys, os, shutil, zipfile
import xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')

with open('/tmp/slaapp_v2/word/document.xml', 'r', encoding='utf-8') as f:
    content = f.read()

def validate(c, label):
    try:
        ET.fromstring(c)
        print(f"  OK: {label}")
    except ET.ParseError as e:
        print(f"  BROKEN after {label}: {e}")
        # Show context around error
        line, col = e.position
        print(repr(c[col-100:col+100]))
        sys.exit(1)

# ── 1. Remove first Swedish comment — full <w:p>...</w:p> ────────────────────
old_sv1 = (
    '<w:p w14:paraId="7BE5D89E" w14:textId="43B0FAAD" w:rsidR="00BE7ED7" w:rsidRPr="000165B6" '
    'w:rsidRDefault="000165B6" w:rsidP="000165B6">'
    '<w:pPr><w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="4"/></w:numPr>'
    '<w:spacing w:before="80" w:after="80"/><w:rPr><w:highlight w:val="yellow"/></w:rPr></w:pPr>'
    '<w:r w:rsidRPr="000165B6"><w:rPr><w:highlight w:val="yellow"/></w:rPr>'
    '<w:t>Detta fungerar jag p\xe5 att ta bort \u2013 om\xf6jligt att g\xf6ra en uppskattning p\xe5 detta.</w:t>'
    '</w:r></w:p>'
)
assert old_sv1 in content, "sv1 not found"
content = content.replace(old_sv1, '', 1)
validate(content, "1. Remove Swedish comment 1")

# ── 2. Remove second Swedish comment — full <w:p>...</w:p> ───────────────────
old_sv2_start = '<w:p w14:paraId="192447E5"'
# Find the closing </w:p> — it ends with <w:t>.</w:t></w:r></w:p>
idx_start = content.find(old_sv2_start)
idx_end = content.find('</w:p>', idx_start) + len('</w:p>')
assert idx_start > 0, "sv2 not found"
content = content[:idx_start] + content[idx_end:]
validate(content, "2. Remove Swedish comment 2")

# ── 3. Fix section numbering ──────────────────────────────────────────────────
content = content.replace('<w:t>2.1 Overview of the AI Validation Model</w:t>', '<w:t>3.1 Overview of the AI Validation Model</w:t>', 1)
content = content.replace('<w:t>2.2 Functional Test Areas</w:t>', '<w:t>3.2 Functional Test Areas</w:t>', 1)
for i, sub in enumerate(['Report Engine', 'Report Templates', 'Excel Export', 'Email Subscription Service', 'Administrative Tools', 'User Permission Model', 'Customer Grouping'], 1):
    content = content.replace(f'<w:t>2.2.{i} {sub}</w:t>', f'<w:t>3.2.{i} {sub}</w:t>', 1)
for old, new in [
    ('3.1 Environment Strategy', '4.1 Environment Strategy'),
    ('3.2 TEST Environment Execution', '4.2 TEST Environment Execution'),
    ('3.3 PROD Environment Execution', '4.3 PROD Environment Execution'),
    ('3.4 Execution Phases', '4.4 Execution Phases'),
    ('4.1 Data Residency', '5.1 Data Residency'),
    ('4.2 Credential Management', '5.2 Credential Management'),
    ('4.3 Data Minimisation', '5.3 Data Minimisation'),
    ('4.4 Access Control', '5.4 Access Control'),
    ('4.5 Audit', '5.5 Audit'),
    ('4.6 Scope Limitations', '5.6 Scope Limitations'),
    ('5.1 Deliverables', '6.1 Deliverables'),
    ('5.2 Success Criteria', '6.2 Success Criteria'),
    ('5.3 Out-of-Scope', '6.3 Out-of-Scope'),
    ('6.1 Roles', '7.1 Roles'),
    ('6.2 Customer Responsibilities', '7.2 Customer Responsibilities'),
    ('6.3 Dependencies', '7.3 Dependencies'),
    ('7.1 Proposed Next Steps', '8.1 Proposed Next Steps'),
    ('7.2 Open Items', '8.2 Open Items'),
]:
    content = content.replace(f'<w:t>{old}', f'<w:t>{new}', 1)
validate(content, "3. Section numbering")

# ── 4. ZDR fix — table cell: add red highlight ────────────────────────────────
old_tc_full = (
    '<w:rPr><w:color w:val="1A1A1A"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>'
    "<w:t>All AI inference and test execution runs on the customer's own infrastructure. "
    "No application data, credentials, or session tokens leave the customer's environment.</w:t>"
)
new_tc_full = (
    '<w:rPr><w:color w:val="1A1A1A"/><w:sz w:val="21"/><w:szCs w:val="21"/><w:highlight w:val="red"/></w:rPr>'
    "<w:t>All AI inference and test execution runs on the customer's own infrastructure. "
    "No application data, credentials, or session tokens leave the customer's environment.</w:t>"
)
assert old_tc_full in content, "table cell not found"
content = content.replace(old_tc_full, new_tc_full, 1)
validate(content, "4. ZDR table cell red")

# ── 5. ZDR fix — body paragraph: red + green replacement ─────────────────────
old_para = (
    '<w:r w:rsidRPr="000165B6"><w:rPr><w:color w:val="1A1A1A"/></w:rPr>'
    '<w:t xml:space="preserve">This is a non-negotiable design constraint. The AI model used for test analysis is deployed locally or accessed via a customer-controlled API endpoint. </w:t></w:r>'
    '<w:proofErr w:type="spellStart"/>'
    '<w:r w:rsidRPr="000165B6"><w:rPr><w:color w:val="1A1A1A"/></w:rPr>'
    "<w:t>Anthropic's</w:t></w:r>"
    '<w:proofErr w:type="spellEnd"/>'
    '<w:r w:rsidRPr="000165B6"><w:rPr><w:color w:val="1A1A1A"/></w:rPr>'
    '<w:t xml:space="preserve"> Claude API (if used) communicates only with the Anthropic inference endpoint \u2014 no application payloads are retained by Anthropic.</w:t></w:r></w:p>'
)
new_para = (
    '<w:r w:rsidRPr="000165B6"><w:rPr><w:color w:val="1A1A1A"/><w:highlight w:val="red"/></w:rPr>'
    '<w:t xml:space="preserve">This is a non-negotiable design constraint. The AI model used for test analysis is deployed locally or accessed via a customer-controlled API endpoint. '
    "Anthropic's Claude API (if used) communicates only with the Anthropic inference endpoint \u2014 no application payloads are retained by Anthropic.</w:t></w:r></w:p>"
    '<w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr>'
    '<w:r><w:rPr><w:color w:val="1A1A1A"/><w:highlight w:val="green"/></w:rPr>'
    '<w:t xml:space="preserve">The Claude API is accessed via an Anthropic enterprise agreement with Zero Data Retention (ZDR) enabled. '
    'Under ZDR, Anthropic does not store prompt inputs or model outputs beyond the duration of the API response \u2014 '
    'this is contractually guaranteed. The AI agent interacts with the application as a browser-based user (Claude-in-Chrome); '
    'no database content or raw report data enters the API. '
    'For the TEST environment, standard API access with 30-day auto-deletion is sufficient. '
    'ZDR is a hard gate before any PROD execution involving live customer data.</w:t></w:r></w:p>'
)
assert old_para in content, "body para not found"
content = content.replace(old_para, new_para, 1)
validate(content, "5. ZDR body paragraph")

# ── 6. Parallelism caveat ─────────────────────────────────────────────────────
old_parallel = (
    '<w:t>Parallelisation: Multiple AI agent instances can test different user roles, report types, or browsers simultaneously. '
    'Manual testing is inherently sequential.</w:t>'
)
new_parallel = (
    '<w:t xml:space="preserve">Parallelisation: Multiple AI agent instances can theoretically test different user roles, '
    'report types, or browsers simultaneously by running separate Claude Code instances via terminal, each targeting a dedicated browser profile. '
    'However, concurrent control of Chrome via the MCP extension is untested and requires validation before it can be relied upon. '
    'For this PoC, execution is sequential. Parallelism is listed as a future consideration.</w:t>'
)
assert old_parallel in content, "parallel not found"
content = content.replace(old_parallel, new_parallel, 1)
validate(content, "6. Parallelism caveat")

# ── 7. Estimates table — red AI figures, green TBD replacements ──────────────
estimates = [
    ('3\u20135 days (after setup)', 'TBD \u2014 to be established during Phase 1 baseline capture'),
    ('4\u20138 hours (agent re-run)', 'TBD \u2014 to be established after first full regression run'),
    ('5\u201310 days (one-time)', 'TBD \u2014 dependent on application scope and complexity'),
    ('2\u20134 hours', 'TBD \u2014 to be established during Phase 1'),
    ('~2nd regression cycle', 'TBD \u2014 to be calculated after Phase 1 and first re-run'),
]
rpr_italic = '<w:rPr><w:i/><w:iCs/><w:color w:val="1A1A1A"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>'
for old_val, new_val in estimates:
    old_cell = f'{rpr_italic}<w:t>{old_val}</w:t>'
    new_cell = (
        f'<w:rPr><w:i/><w:iCs/><w:color w:val="1A1A1A"/><w:sz w:val="20"/><w:szCs w:val="20"/><w:highlight w:val="red"/></w:rPr>'
        f'<w:t>{old_val}</w:t>'
        f'</w:r></w:p>'
        f'<w:p><w:r>'
        f'<w:rPr><w:i/><w:iCs/><w:color w:val="1A1A1A"/><w:sz w:val="20"/><w:szCs w:val="20"/><w:highlight w:val="green"/></w:rPr>'
        f'<w:t>{new_val}</w:t>'
    )
    assert old_cell in content, f"estimate cell not found: {old_val}"
    content = content.replace(old_cell, new_cell, 1)
validate(content, "7. Estimates table red/green")

# ── 8. Finding line: red old, green new ─────────────────────────────────────
old_finding = (
    '<w:rPr><w:b/><w:bCs/><w:color w:val="FFFFFF"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>'
    '<w:t>Finding: Yes \u2014 provided the architecture is designed with data residency as a first-order constraint.</w:t>'
    '</w:r></w:p></w:tc></w:tr></w:tbl>'
)
new_finding = (
    '<w:rPr><w:b/><w:bCs/><w:color w:val="FFFFFF"/><w:sz w:val="24"/><w:szCs w:val="24"/><w:highlight w:val="red"/></w:rPr>'
    '<w:t>Finding: Yes \u2014 provided the architecture is designed with data residency as a first-order constraint.</w:t>'
    '</w:r></w:p></w:tc></w:tr></w:tbl>'
    '<w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr>'
    '<w:r><w:rPr><w:b/><w:bCs/><w:color w:val="1A1A1A"/><w:highlight w:val="green"/></w:rPr>'
    '<w:t xml:space="preserve">Finding: Yes \u2014 provided the Claude API is accessed under a Zero Data Retention (ZDR) enterprise agreement, '
    'and the AI agent operates exclusively as a browser-based user (Claude-in-Chrome). '
    'Data residency is not the primary control; contractual non-retention and browser-scoped access are.</w:t>'
    '</w:r></w:p>'
)
assert old_finding in content, "finding line not found"
content = content.replace(old_finding, new_finding, 1)
validate(content, "8. Finding line red/green")

# ── 9. Conclusion line in security section: red old, green new ────────────────
old_conclusion = (
    '<w:r w:rsidRPr="000165B6"><w:rPr><w:color w:val="1A1A1A"/><w:sz w:val="21"/><w:szCs w:val="21"/></w:rPr>'
    '<w:t xml:space="preserve"> or under a contractual no-retention API agreement, and the agent scope is limited to metadata and structural signals in PROD.</w:t>'
    '</w:r></w:p></w:tc></w:tr></w:tbl>'
)
new_conclusion = (
    '<w:r w:rsidRPr="000165B6"><w:rPr><w:color w:val="1A1A1A"/><w:sz w:val="21"/><w:szCs w:val="21"/><w:highlight w:val="red"/></w:rPr>'
    '<w:t xml:space="preserve"> or under a contractual no-retention API agreement, and the agent scope is limited to metadata and structural signals in PROD.</w:t>'
    '</w:r></w:p></w:tc></w:tr></w:tbl>'
    '<w:p><w:pPr><w:spacing w:before="60" w:after="60"/></w:pPr>'
    '<w:r><w:rPr><w:color w:val="1A1A1A"/><w:highlight w:val="green"/></w:rPr>'
    '<w:t xml:space="preserve">Conclusion: AI-assisted testing can be conducted without data leakage. '
    'The control is a ZDR enterprise agreement with Anthropic (contractual non-retention) combined with browser-only agent scope \u2014 '
    'the agent sees only what a human tester would see on screen. '
    'No raw report data, database content, or PII is transmitted to the API.</w:t>'
    '</w:r></w:p>'
)
assert old_conclusion in content, "conclusion not found"
content = content.replace(old_conclusion, new_conclusion, 1)
validate(content, "9. Conclusion red/green")

# ── Save + repack ─────────────────────────────────────────────────────────────
shutil.rmtree('/tmp/slaapp_v2_revised/', ignore_errors=True)
shutil.copytree('/tmp/slaapp_v2/', '/tmp/slaapp_v2_revised/')

with open('/tmp/slaapp_v2_revised/word/document.xml', 'w', encoding='utf-8') as f:
    f.write(content)

validate(content, "Final save")

original = 'C:/Users/JasonNicolini/Downloads/Advania_V2_PoC_AI_Verification_NET10_Upgrade.docx'
output_path = 'C:/Users/JasonNicolini/Downloads/Advania_V2_PoC_AI_Verification_NET10_Upgrade_REVISED.docx'

with zipfile.ZipFile(original, 'r') as zin:
    original_order = [item.filename for item in zin.infolist()]

with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name in original_order:
        filepath = os.path.join('/tmp/slaapp_v2_revised/', name.replace('/', os.sep))
        if os.path.exists(filepath):
            zout.write(filepath, name)
    for root, dirs, files in os.walk('/tmp/slaapp_v2_revised/'):
        for file in files:
            filepath = os.path.join(root, file)
            arcname = os.path.relpath(filepath, '/tmp/slaapp_v2_revised/').replace(os.sep, '/')
            if arcname not in original_order:
                zout.write(filepath, arcname)

print("Done:", output_path)
