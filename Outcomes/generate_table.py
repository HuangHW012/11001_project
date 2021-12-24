import datetime


class generate_table():
    def __init__(self, patient_id, diagnosis_outcomes, which_diagnosis):
        self.diagnosis_outcomes = diagnosis_outcomes
        self.patient_id = patient_id
        self.which_diagnosis = which_diagnosis

    def print_table(self):
        path = f'./{self.patient_id}_Diagnosis_Outcomes.txt'
        with open(path, 'w') as file:
            file.write(f"Patient ID: {self.patient_id}\n")
            file.write("=" * 50 + "\n")
            index = 0
            for i, diagnosis_type in enumerate(['   Brain', '   Chest', '    Skin', 'Diabetes', '  Stroke']):
                if  self.which_diagnosis[i] == True:
                    file.write(f"[{diagnosis_type}]: ")
                    file.write(f"{self.diagnosis_outcomes[index]}\n")
                    index += 1

            file.write("=" * 50 + "\n")
            now_time = datetime.datetime.today() 
            now_time_format = now_time.strftime("%Y/%m/%d %H:%M:%S")
            file.write(f"Time: {now_time_format}\n")
                



if __name__ == '__main__':
    text = generate_table('001', ['Yes', 'No', 'Yes', 'No', 'No'], [True, True, True, True, True])
    text.print_table()

