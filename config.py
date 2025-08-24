import os
path_to_csv = os.path.join(os.path.dirname(__file__), "data", "seizure.csv")
path_to_medicine_csv = os.path.join(os.path.dirname(__file__), "data", "medicine.csv")
admin_list = [
    5460055491, 997175404, 6529721479, 351620312
]

admin_json = {
    5460055491: "Зилола",
    997175404: "Абдусалом",
    6529721479: "Акобир",
    351620312: "Абдумуталиб"
}