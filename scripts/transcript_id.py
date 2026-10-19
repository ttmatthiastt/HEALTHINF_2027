import glob
import json

def promptstyle(name):
    names=name.split("_")
    transcriptid = names[1]
    promptype = names[-1].replace(".json","") 
    if promptype == "zero-thought chain of thought":
        promptype = "zero-shot chain of thought"
    return transcriptid, promptype

names_list = glob.glob("*.json")
for name in names_list:
    transcriptid, promptype = promptstyle(name)
    with open(name, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["transcriptid"] = "T"+str(transcriptid)
    data["promptype"] = promptype

    with open(name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("updated:", name, "UPDATESS TO!!", transcriptid, promptype)
