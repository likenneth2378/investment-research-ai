import argparse
import json
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
EXAMPLES_DIR = PROJECT_DIR / "examples"
DEMO_FILE = PROJECT_DIR / "demo" / "sample_claims.json"
OUTPUT_DIR = PROJECT_DIR / "output"

EVIDENCE_STATUSES = {
    "Unverified",
    "Supported",
    "Projection",
    "Subjective / Marketing",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build an evidence-first Claim Ledger from investment research materials."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run without an API key using saved sample claims.",
    )
    return parser.parse_args()


def load_company_files():
    company_files = sorted(EXAMPLES_DIR.glob("*.txt"))
    if not company_files:
        raise FileNotFoundError(
            f"No .txt files found in {EXAMPLES_DIR}. Add example materials first."
        )
    return company_files


def clean_document(company_file):
    company_text = company_file.read_text(encoding="utf-8")
    lines = company_text.splitlines()
    clean_lines = []

    for line_number, line in enumerate(lines, start=1):
        statement = line.strip()
        if not statement:
            continue

        clean_lines.append({
            "line_number": line_number,
            "text": statement,
        })

    return clean_lines


def build_chunks(clean_lines, chunk_size=3):
    chunks = []

    for i in range(0, len(clean_lines), chunk_size):
        chunk_lines = clean_lines[i:i + chunk_size]
        chunk_text = "\n".join(item["text"] for item in chunk_lines)

        chunks.append({
            "chunk_index": i // chunk_size,
            "chunk_text": chunk_text,
            "source_line_start": chunk_lines[0]["line_number"],
            "source_line_end": chunk_lines[-1]["line_number"],
        })

    return chunks


def build_prompt(chunk_text):
    return f"""
你是一名投资研究信息抽取助手。

请从下面的材料片段中提取真正具有研究价值的事实性或可验证主张。

一个片段中可能有：
- 0 条主张
- 1 条主张
- 多条主张

不要把标题、公司名称、\"公司称：\"这类单独的上下文标签当成主张。

请严格返回 JSON 数组，不要输出 Markdown，不要解释。

每条主张必须包含：

claim:
用简洁中文表达主张，但不要增强原文含义。

source_text:
复制支持该主张的原始文本。尽量保持原文，不要改写。

attribution:
这是谁提出或提供的说法，例如：
\"公司\"
\"管理层\"
\"CEO 陈浩\"
\"公司融资材料\"
如果无法判断，填写 \"Unknown\"。

evidence_status:
只能使用下面四种值：
\"Unverified\"
\"Supported\"
\"Projection\"
\"Subjective / Marketing\"

规则：
- 已发生但尚未独立验证的事实 → Unverified
- 明确有当前材料中的证据直接支持 → Supported
- 预计、计划、预测、目标 → Projection
- 主观定位、领先、优秀等不可直接验证表述 → Subjective / Marketing

特别注意：
不要删除“公司称”“管理层表示”等 attribution 信息。
不要把历史事实误判为 Projection。
不要因为一个数字听起来像宣传就自动判断为 Subjective / Marketing。

材料片段：

{chunk_text}
"""


def create_client():
    from openai import OpenAI

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Run `python main.py --demo` "
            "or set your own OpenRouter API key for live mode."
        )

    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )


def extract_live(client, chunk_text):
    response = client.responses.create(
        model="cohere/north-mini-code:free",
        input=build_prompt(chunk_text),
    )

    result = response.output_text

    try:
        extracted_claims = json.loads(result)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid JSON:\n{result}") from exc

    return extracted_claims


def load_demo_claims():
    if not DEMO_FILE.exists():
        raise FileNotFoundError(f"Demo fixture not found: {DEMO_FILE}")

    return json.loads(DEMO_FILE.read_text(encoding="utf-8"))


def validate_claim(extracted):
    required_fields = {"claim", "source_text", "attribution", "evidence_status"}
    missing_fields = required_fields - extracted.keys()

    if missing_fields:
        raise ValueError(f"Missing fields: {sorted(missing_fields)}")

    if extracted["evidence_status"] not in EVIDENCE_STATUSES:
        raise ValueError(
            f"Invalid evidence_status: {extracted['evidence_status']}"
        )


def build_claim_ledger(demo=False):
    company_files = load_company_files()
    claim_ledger = []
    demo_claims = load_demo_claims() if demo else None
    client = None if demo else create_client()

    for company_file in company_files:
        document_id = company_file.stem
        clean_lines = clean_document(company_file)
        chunks = build_chunks(clean_lines)

        for chunk in chunks:
            if demo:
                key = f"{document_id}:{chunk['chunk_index']}"
                extracted_claims = demo_claims.get(key, [])
            else:
                extracted_claims = extract_live(client, chunk["chunk_text"])

            for extracted in extracted_claims:
                validate_claim(extracted)

                claim_ledger.append({
                    "claim": extracted["claim"],
                    "source_text": extracted["source_text"],
                    "attribution": extracted["attribution"],
                    "source_line_start": chunk["source_line_start"],
                    "source_line_end": chunk["source_line_end"],
                    "evidence_status": extracted["evidence_status"],
                    "document_id": document_id,
                })

    for i, item in enumerate(claim_ledger, start=1):
        item["claim_id"] = f"claim_{i}"

    return claim_ledger


def render_html(claim_ledger):
    total_claims = len(claim_ledger)
    total_documents = len(set(item["document_id"] for item in claim_ledger))
    status_labels = {
        "Unverified": "未验证",
        "Supported": "当前材料支持",
        "Projection": "预测 / 目标",
        "Subjective / Marketing": "主观 / 营销表述",
    }

    html = f"""
<html>
<head>
<meta charset="utf-8">
<title>投资研究 Claim Ledger</title>
<style>
body {{
    font-family: Arial, "Microsoft YaHei", sans-serif;
    background: #f5f6f8;
    margin: 0;
    padding: 28px;
    color: #222;
}}
.container {{ max-width: 980px; margin: auto; }}
h1 {{ margin-bottom: 6px; }}
.subtitle {{ color: #666; margin-top: 0; margin-bottom: 10px; }}
.summary {{ font-size: 14px; color: #666; margin-bottom: 24px; }}
.notice {{
    background: #fff8e6;
    border: 1px solid #f0d58a;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 22px;
    font-size: 14px;
    line-height: 1.6;
}}
.claim-card {{
    background: white;
    border: 1px solid #e8e8e8;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
}}
.claim-top {{ display: flex; justify-content: space-between; gap: 12px; margin-bottom: 8px; }}
.claim-id {{ font-size: 12px; color: #999; }}
.status {{ font-size: 12px; background: #f2f2f2; padding: 3px 8px; border-radius: 12px; color: #555; white-space: nowrap; }}
.claim-text {{ font-size: 17px; line-height: 1.55; font-weight: 600; margin-bottom: 12px; }}
.meta {{ font-size: 13px; line-height: 1.7; color: #555; }}
.label {{ color: #888; }}
.source-text {{ margin-top: 9px; padding: 10px 12px; background: #f8f8f8; border-radius: 6px; font-size: 13px; line-height: 1.6; }}
.footer {{ color: #888; font-size: 12px; margin-top: 22px; }}
</style>
</head>
<body>
<div class="container">
<h1>投资研究 Claim Ledger</h1>
<p class="subtitle">保留原文、信息归属与证据状态的结构化主张账本</p>
<p class="summary">共 {total_claims} 条主张 · {total_documents} 份来源材料</p>
<div class="notice">
    <strong>Demo 观察重点：</strong>
    27 个项目与 30 个项目来自不同时间点；3 亿元与 3.2 亿元属于预测版本变化；“11 项核心专利”包含合作开发和未授权项目。
    当前版本负责保留这些差异及来源，不自动判断谁真谁假。
</div>
"""

    for item in claim_ledger:
        claim_number = item["claim_id"].replace("claim_", "")
        status_label = status_labels.get(item["evidence_status"], item["evidence_status"])
        html += f"""
<div class="claim-card">
    <div class="claim-top">
        <span class="claim-id">主张 {claim_number}</span>
        <span class="status">{status_label}</span>
    </div>
    <div class="claim-text">{item['claim']}</div>
    <div class="meta">
        <div><span class="label">信息归属：</span>{item['attribution']}</div>
        <div><span class="label">来源：</span>{item['document_id']}.txt · 第 {item['source_line_start']}-{item['source_line_end']} 行</div>
    </div>
    <div class="source-text"><span class="label">原文：</span>{item['source_text']}</div>
</div>
"""

    html += """
<p class="footer">注：Demo 使用虚构公司与合成尽调材料，用于展示工作流，不代表真实公司的事实判断。</p>
</div>
</body>
</html>
"""

    return html

def save_outputs(claim_ledger):
    OUTPUT_DIR.mkdir(exist_ok=True)

    ledger_file = OUTPUT_DIR / "claim_ledger.json"
    ledger_file.write_text(
        json.dumps(claim_ledger, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    html_file = OUTPUT_DIR / "claim_ledger.html"
    html_file.write_text(render_html(claim_ledger), encoding="utf-8")

    return ledger_file, html_file


def main():
    args = parse_args()
    mode_name = "DEMO" if args.demo else "LIVE"
    print(f"Running in {mode_name} mode...")

    claim_ledger = build_claim_ledger(demo=args.demo)
    ledger_file, html_file = save_outputs(claim_ledger)

    print(f"Generated {len(claim_ledger)} claims.")
    print("JSON:", ledger_file.resolve())
    print("HTML:", html_file.resolve())


if __name__ == "__main__":
    main()
