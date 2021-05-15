import json

with open(r"rawData/course_data3.json", encoding="utf-8") as f:
    raw_data = json.load(f)

processed_data = {}

for item in raw_data["data"]["courses"].keys():
    newKey = raw_data["data"]["courses"][item]["courseCode"]
    processed_data[newKey] = raw_data["data"]["courses"][item]

with open(r"rawData/processed_data.json", "w") as f:
    json.dump(processed_data, f, indent=4)
