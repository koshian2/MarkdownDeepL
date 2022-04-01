import eel
from sys import exit
import json
import deepl
import os
import re

master_data = {}

def main():
    eel.init("./", allowed_extensions=[".js", ".html", ".css"])
    eel.start("index.html", port=11384, 
        size=(1024, 768),
        close_callback=on_application_ended)

# 終了処理用（これがないとポートを専有し続ける）
def on_application_ended(route, websockets):
    if not websockets:
        save_settings()
        exit()

@eel.expose
def load_settings():
    global master_data, translator
    # デフォルト値
    master_data = {
        "auth_key": "",
        "source_lang": "JA",
        "target_lang": "EN-US"
    }
    try:
        with open("config.json") as fp:
            update_data = json.load(fp)
        for k, v in update_data.items():
            master_data[k] = v
    except Exception as e:
        pass
    # UI値に反映
    eel.updateMasterData(master_data)

def save_settings():
    if master_data != {} and type(master_data) == dict:
        with open("config.json", "w") as fp:
            json.dump(master_data, fp, ensure_ascii=False, indent=4, separators=(',', ': '))

@eel.expose
def translate(source_string):
    # Get Replacement rule
    rules_path = f"rules/{master_data['source_lang']}_{master_data['target_lang']}.txt"
    replacement_rule = []
    if os.path.exists(rules_path):
        with open(rules_path, "r") as fp:
            rules_raw = fp.readlines()
        for rule in rules_raw:
            tmp_split = rule.replace("\n", "").split("\t")
            if(len(tmp_split)) >= 2:
                replacement_rule.append([tmp_split[0], tmp_split[1]])

    # split contents
    sources, tmp = [], []
    cnt = 0
    for s in source_string.splitlines(keepends=True):
        cnt += len(s)
        if cnt > 4500:
            sources.append("".join(tmp))
            tmp = [s]
            cnt = len(s)
        else:
            tmp.append(s)
    else:
        sources.append("".join(tmp))

    # DeepL Translate
    try:
        translator = deepl.Translator(auth_key=master_data["auth_key"])
        result = translator.translate_text(
                    [sources], 
                    source_lang=master_data["source_lang"],
                    target_lang=master_data["target_lang"])
        usage = translator.get_usage()
        result_txt = "\n".join([r.text for r in result])
    except Exception as ex:
        return "", "DeepL translation error\n"+str(ex)

    # ルールベースで置き換え
    message = ""
    for rule in replacement_rule:
        try:
            #print(rule)
            result_txt = re.sub(rule[0], rule[1], result_txt)
        except Exception as ex:
            message = f"Replacement rule error at {rule[0]} -> {rule[1]}\n"+str(ex)
    
    if message == "":
        return result_txt, f"Translate success\nCharacter usage: {usage.character.count} of {usage.character.limit}"
    else:
        return result_txt, message

if __name__ == "__main__":
    main()