import os
import json
from pathlib import Path
from openai import OpenAI

client = OpenAI(
    api_key = os.getenv("OPENROUTER_API_KEY"),
    base_url = "https://openrouter.ai/api/v1"
)

project_dir = Path(__file__).parent

company_files = [
    project_dir / "test_company.txt",
    project_dir / "test_company_2.txt"
]

claim_ledger = []

for company_file in company_files:
    document_id = company_file.stem
    company_text = company_file.read_text(encoding="utf-8")

    for line_number, line in enumerate(company_text.splitlines(), start=1):
        statement = line.strip()

        if not statement:
            continue

        item = {
            "claim": statement,
            "source_text": statement,
            "source_line": line_number,
            "evidence_status": "TEST",
            "document_id": document_id
    }

        claim_ledger.append(item)

for i, item in enumerate(claim_ledger, start=1):
    item["claim_id"] = f"claim_{i}"

for item in claim_ledger:
    claim_number = item["claim_id"].replace("claim_", "")

    print(f'【主张 {claim_number}】{item["claim"]}')
    print(f'来源：{item["document_id"]}.txt｜第{item["source_line"]}行')
    print()

total_claims = len(claim_ledger)
total_documents = len(set(item["document_id"] for item in claim_ledger))

html = f"""
<html>
<head>
<meta charset="utf-8">
<title>Claim Ledger</title>

<style>
body {{
    font-family: Arial, "Microsoft YaHei", sans-serif;
    background: #f5f6f8;
    margin: 0;
    padding: 28px;
    color: #222;
}}

.container {{
    max-width: 960px;
    margin: auto;
}}

h1 {{
    margin-bottom: 4px;
}}

.subtitle {{
    color: #777;
    margin-top: 0;
    margin-bottom: 24px;
}}

.claim-card {{
    background: white;
    border: 1px solid #e8e8e8;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}}

.claim-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}}

.claim-id {{
    font-size: 12px;
    color: #999;
}}

.status {{
    font-size: 12px;
    background: #f2f2f2;
    padding: 3px 8px;
    border-radius: 12px;
    color: #666;
}}

.claim-text {{
    font-size: 17px;
    line-height: 1.5;
    font-weight: 500;
    margin-bottom: 8px;
}}

.source {{
    font-size: 12px;
    color: #999;
}}

.summary {{
    font-size: 14px;
    color: #555;
    margin-bottom: 20px;
}}
</style>

</head>

<body>

<div class="container">

<h1>Claim Ledger</h1>
<p class="subtitle">跨文档主张追踪与证据核对</p>
<p class="summary">共 {total_claims} 条记录 · {total_documents} 个来源文件</p>
"""

for item in claim_ledger:
    claim_number = item["claim_id"].replace("claim_", "")

    html += f"""
    <div class="claim-card">

        <div class="claim-top">
            <span class="claim-id">主张 {claim_number}</span>
            <span class="status">{item["evidence_status"]}</span>
        </div>

        <div class="claim-text">
            {item["claim"]}
        </div>

        <div class="source">
            {item["document_id"]}.txt · 第 {item["source_line"]} 行
        </div>

    </div>
    """

html += """
</div>

</body>
</html>
"""

output_file = Path(__file__).parent / "claim_ledger.html"
output_file.write_text(html, encoding="utf-8")

print("HTML 已生成：", output_file.resolve())

ledger_file = Path(__file__).parent / "claim_ledger.json"

ledger_file.write_text(
    json.dumps(claim_ledger, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

loaded_ledger = json.loads(
    ledger_file.read_text(encoding="utf-8")
)

print(type(loaded_ledger))
print(len(loaded_ledger))
print("Claim Ledger 已保存：", ledger_file.resolve())