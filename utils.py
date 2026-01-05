import json

def json_to_markdown(json_str):
    data = json.loads(json_str)
    
    # 1. Header and Score
    md = f"# OKR Evaluation Report\n\n"
    md += f"**Quality Label:** `{data['quality_label']}`  \n"
    md += f"**Total Score:** `{data['total_score']}/10` \n\n"
    
    # 2. Critique Table
    md += "## Detailed Critique\n\n"
    md += "| Dimension | Feedback |\n"
    md += "| :--- | :--- |\n"
    for dimension, feedback in data['critique'].items():
        md += f"| **{dimension.capitalize()}** | {feedback} |\n"
    md += "\n"
    
    # 3. Improvement Suggestions (Bulleted List)
    md += "## Improvement Suggestions\n\n"
    for suggestion in data['improvement_suggestions']:
        md += f"- {suggestion}\n"
    md += "\n"
    
    # 4. Action Plan Table
    # md += "## Action Plan\n\n"

    # for i, item in enumerate(data['action_plan'], 1):
    #     # Headline task
    #     md += f"{i}. TASK: {item['task']}\n"
        
    #     # Detail lines
    #     md += f"   - Owner:   {item['owner']}\n"
    #     md += f"   - Cadence: {item['cadence']}\n"
    #     md += f"   - Blockers: {item['blockers']}\n"
        
        
    return md
