import os
import signal
from bson import ObjectId
from InquirerPy import prompt
import json
from pathlib import Path
import subprocess

abs_path = Path(__file__).parent.parent

def list_templates(directory: Path):
    templates_list = {}
    for dir in directory.glob("*"):
        if dir.is_dir():
            try:
                dir_id = ObjectId(dir.name)
                json_path = dir / "config.json"

                if json_path.exists():
                    with open(json_path, 'r', encoding='utf-8') as file:
                        json_data = json.load(file)
                    
                    template_name = json_data.get("name")
                    template_niche = json_data.get("niche")
                    template_category = json_data.get("category")

                    templates_list[template_niche, template_name] = dir.name

            except Exception as e:
                continue
    
    sorted_templates = sorted(templates_list.items(), key=lambda x:(x[0][0], x[0][1]))

    return {template_name: {"id": dir_name, "niche": niche} for (niche, template_name), dir_name in sorted_templates}

def main():
    templates_path = abs_path / "templates"
    templates_dict = list_templates(templates_path)

    if len(templates_dict) == 0:
        print("Nenhum template encontrado")
        return
    
    templates = list(f"{value.get('niche')} - {name}" for name, value in templates_dict.items())
    
    questions = [
        {
            "type": "fuzzy",
            "name": "template",
            "message": "Selecione o template:",
            "multiselect": True,
            "choices": templates
        }
    ]

    answers = prompt(questions)
    selected_templates = answers["template"]

    template_dirs = []
    for selected_template in selected_templates:
        selected_template = selected_template.split(" - ")[1]
        template_dir = templates_path / templates_dict[selected_template]["id"]
        template_dirs.append(str(template_dir))
    
    command = ["code"] + template_dirs
    process = subprocess.Popen(command, shell=True)
    parent_pid = os.getppid()
    process.wait()

    os.kill(parent_pid, signal.SIGTERM)
        


if __name__ == "__main__":
    main()