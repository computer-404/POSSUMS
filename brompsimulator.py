import tkinter as tk
from tkinter import messagebox, filedialog
import random
import math

# Event Class
class Event:
    def __init__(self, name, duration, proportion):
        self.name = name
        self.duration = duration
        self.proportion = proportion

    def get_name(self):
        return self.name

    def get_duration(self):
        return self.duration

    def get_proportion(self):
        return self.proportion

    def __str__(self):
        return f"{self.name} - {self.duration} - {self.proportion}"

# Class Run Event Data
class ClassRunEventData:
    def __init__(self, total_tally, percentage):
        self.total_tally = total_tally
        self.percentage = percentage

    def get_total_tally(self):
        return self.total_tally

    def get_percentage(self):
        return self.percentage

class BROMPSimulator:
    def __init__(self, events, timesPerObservation, numberOfStudents, totalObservationTime):
        self.events = events
        self.timesPerObservation = timesPerObservation
        self.numberOfStudents = numberOfStudents
        self.totalObservationTime = totalObservationTime
        self.randomGenerator = random.Random()

    def run(self, output_file):
        if app.repeated_simulation_check.get():
            self.run_repeated_simulation(output_file)
        else:
            self.run_single_simulation(output_file)
    
    def run_repeated_simulation(self, output_file):
        number_of_simulations = int(app.repeated_simulation_entry.get())
        cumulative_run_data = []
        for i in range(number_of_simulations):
            student_states = self.generate_students_states()
            all_observation_time_data = {}
            for time_per_observation in self.timesPerObservation:
                student_observations = self.compute_observation_results(student_states, time_per_observation)
                all_observation_time_data[time_per_observation] = self.compute_class_level_results(student_observations)
            cumulative_run_data.append(all_observation_time_data)
        self.output_cummulative_results(cumulative_run_data, output_file)
        
    def output_cummulative_results(self, cumulative_run_data, output_file):
        with open(output_file, 'w') as file:
            for time_per_observation in self.timesPerObservation:
                file.write("Time per observation = " + str(time_per_observation))
                file.write("\r\n\r\n")
                file.write(",average tally,std tally,average percentage,std percentage,,target percentage\r\n")
                for event in self.events:
                    average_tallies = 0
                    std_tallies = 0
                    average_percentage = 0
                    std_percentage = 0
                    tallies = []
                    percentages = []
                    for run_level_data in cumulative_run_data:
                        data = run_level_data[time_per_observation][event]
                        average_tallies += data.get_total_tally()
                        if data.get_percentage() == None:
                            average_percentage += 0
                        else:
                            average_percentage += data.get_percentage()
                        tallies.append(float(data.get_total_tally()))
                        percentages.append(data.get_percentage())
                    average_tallies = average_tallies / (float(len(cumulative_run_data)))
                    average_percentage = average_percentage / (float(len(cumulative_run_data)))
                    for i in range(len(tallies)):
                        std_tallies += (tallies[i] - average_tallies) * (tallies[i] - average_tallies)
                        std_percentage += (percentages[i] - average_percentage) * (percentages[i] - average_percentage)
                    
                    std_tallies = math.sqrt(std_tallies / (float(len(cumulative_run_data)-1)))
                    std_percentage = math.sqrt(std_percentage / (float(len(cumulative_run_data)-1)))

                    file.write(event.get_name() + "," + str(average_tallies) + "," + str(std_tallies) + "," + str(average_percentage) + "," + str(std_percentage) + ',,' + str((float(event.get_proportion()) / float(100))) + "\r\n")
                file.write("\r\n\r\n")

                file.write("Simulation#")
                for event in self.events:
                    file.write("," + event.get_name() + " tally," + event.get_name() + " percentage")
                file.write("\r\n")
                simulationIndex = 1
                for run_level_data in cumulative_run_data:
                    file.write(str(simulationIndex))
                    for event in self.events:
                        data = run_level_data[time_per_observation][event]
                        file.write("," + str(data.get_total_tally()) + "," + str(data.get_percentage()))
                    file.write("\r\n")
                    simulationIndex += 1
                file.write("\r\n")
    
    def compute_class_level_results(self, student_observations):
        number_of_students = len(student_observations)
        total_class_tallies = {}
        for event in self.events:
            total_class_tallies[event] = 0
        total_tally_per_student = []
        percentages_per_students = []
        for student in student_observations:
            total_student_tally = 0

            for event in self.events:
                current_tally = student[event]
                #print(current_tally, total_class_tallies[event])
                total_class_tallies[event] = total_class_tallies[event] + current_tally
                total_student_tally += current_tally

            percentages_for_current_student = {}
            print(total_student_tally)
            for event in self.events:
                if total_student_tally == 0:
                    percentages_for_current_student[event] = 0
                    continue
                percentages_for_current_student[event] = float(student[event]) / float(total_student_tally)
            
            total_tally_per_student.append(total_student_tally)
            percentages_per_students.append(percentages_for_current_student)
        average_class_percentages = {}
        for event in self.events:
            percentage_sum = 0
            for i in range(number_of_students):
                percentage_sum += percentages_per_students[i][event]
            average_class_percentages[event] = percentage_sum / float(number_of_students)
        
        class_level_data = {}
        for event in self.events:
            class_level_data[event] = ClassRunEventData(total_class_tallies[event], average_class_percentages[event])
        
        return class_level_data
    def run_single_simulation(self, output_file):
        with open(output_file, 'w') as file:
            student_states = self.generate_student_states()
            for time_per_observation in self.timesPerObservation:
                self.compute_and_output_observation_results(student_states, time_per_observation, file)
            file.write("Randomized events:\r\n\r\n")
            self.write_student_states(student_states, file)

    def compute_and_output_observation_results(self, student_states, time_per_observation, file):
        student_observations = self.compute_observation_results(student_states, time_per_observation)
        real_event_counts = self.compute_real_event_counts(student_states)
        self.write_observation_results(real_event_counts, student_observations, time_per_observation, file)

    def compute_observation_results(self, student_states, time_per_observation):
        assert len(student_states) == self.numberOfStudents
        current_time_index = 0
        current_student_index = 0

        student_observations = []
        for i in range(self.numberOfStudents):
            observation_map = {}
            for event in self.events:
                observation_map[event] = 0
            student_observations.append(observation_map)
        while current_time_index < len(student_states[0]):
            observed_event = student_states[current_student_index][current_time_index]
            observation_map = student_observations[current_student_index]
            observation_map[observed_event] = observation_map[observed_event] + 1
            current_time_index += time_per_observation
            current_student_index = (current_student_index + 1) % self.numberOfStudents
        return student_observations
    def compute_real_event_counts(self, student_states):
        real_event_counts = {}
        for event in self.events:
            real_event_counts[event] = 0
        for event in student_states[0]:
            real_event_counts[event] = real_event_counts[event] + 1
        return real_event_counts
    def write_observation_result(self, real_event_counts, student_observations, time_per_observation, file):
        file.write("Time per observation = " + str(time_per_observation))
        file.write("\r\n\r\n")

        for i in range(self.numberOfStudents):
            file.write(",tally student" + str(i+1) + ",percentage student" + str(i+1))
        
        file.write(",,total tally, average tally, std tally, average percentage, std percentage")
        file.write(",,target percentage")
        file.write("\r\n")
        number_of_target_observations = 0
        for num in real_event_counts.values():
            number_of_target_observations += num
        
        for event in self.events:
            file.write(event.get_name())
            tallies = []
            percentages = []
            for student_index in range(self.numberOfStudents):
                observations = student_observations[student_index]
                tally = observations[event]
                file.write("," + str(tally))
                number_of_observations = 0
                for num in observations.values():
                    number_of_observations += num

                percentage = float(tally) / float(number_of_observations)
                file.write("," + str(percentage))
                tallies.append(tally)
                percentages.append(percentage)
            total_tally = 0
            for tally in tallies:
                total_tally += tally
            average_taly = float(((float(total_tally)) / (float(self.numberOfStudents))))
            std_tally = 0
            for tally in tallies:
                std_tally += (tally - average_taly) * (tally - average_taly)
            std_tally = float(math.sqrt(std_tally / (float(self.numberOfStudents-1))))
            average_percentage = 0
            for percentage in percentages:
                average_percentage += percentage
            average_percentage = average_percentage / float(self.numberOfStudents)
            std_percentage = 0
            for percentage in percentages:
                std_percentage += (percentage - average_percentage) * (percentage - average_percentage)
            std_percentage = math.sqrt(std_percentage / float(self.numberOfStudents))
            file.write(",,," + str(total_tally) + "," + str(average_taly) + "," + str(std_tally) + "," + str(average_percentage) + "," + str(std_percentage) + ",," + float(event.get_proportion()) / float(100))
            file.write(",," + str(float(real_event_counts[event]) / float(number_of_target_observations)))
            file.write("\r\n")
        file.write("\r\n\r\n")
    def generate_students_states(self):
        student_states = []
        for i in range(self.numberOfStudents):
            student_states.append(self.generate_states_for_one_student())
        return student_states
    def generate_states_for_one_student(self):
        states = []
        nonRandomizedEvents = []
        for event in self.events:
            count_of_event = (float(self.totalObservationTime) * float(event.get_proportion())) / (100 * float(event.get_duration()))
            #print(math.floor(count_of_event))
            for i in range(int(count_of_event)):
                nonRandomizedEvents.append(event)
        randomizedEvents = []
        while(len(nonRandomizedEvents) > 0):
            randomIndex = self.randomGenerator.randrange(len(nonRandomizedEvents))
            randomizedEvents.append(nonRandomizedEvents.pop(randomIndex))
                    
        for event in randomizedEvents:
            for i in range(int(event.get_duration())):
                states.append(event)

        return states
    
    def write_student_states(self, student_states, file):
        file.write("time")
        for i in range(len(student_states)):
            file.write(",student" + str(i+1))
        
        file.write("\r\n")

        for timeIndex in range(len(student_states[0])):
            file.write(str(timeIndex+1))
            for studentIndex in range(len(student_states)):
                file.write("," + student_states[studentIndex][timeIndex].get_name())
            file.write("\r\n")
                                  

            

class EventManager:
    def __init__(self, root):
        self.root = root
        self.root.title("POSSUMS 1.0")
        self.root.geometry('550x840')

        self.events = []
        self.times_per_observation = []

        self.init_event_input_fields()
        self.init_simulation_parameters()
        self.init_run_interface()

    def init_event_input_fields(self):
        event_label = tk.Label(self.root, text="Event:", anchor='e')
        event_label.place(x=20, y=60, width=80, height=30)

        self.event_entry = tk.Entry(self.root)
        self.event_entry.place(x=110, y=60, width=150, height=30)

        duration_label = tk.Label(self.root, text="Duration:", anchor='e')
        duration_label.place(x=20, y=120, width=80, height=30)

        self.duration_entry = tk.Entry(self.root)
        self.duration_entry.place(x=110, y=120, width=150, height=30)

        proportion_label = tk.Label(self.root, text="Proportion:", anchor='e')
        proportion_label.place(x=20, y=180, width=80, height=30)

        self.proportion_entry = tk.Entry(self.root)
        self.proportion_entry.place(x=110, y=180, width=150, height=30)

        self.add_button = tk.Button(self.root, text="Add", command=self.add_event, state='disabled')
        self.add_button.place(x=140, y=240, width=90, height=30)

        event_list_label = tk.Label(self.root, text="Events", anchor='center')
        event_list_label.place(x=300, y=30, width=180, height=30)

        self.event_listbox = tk.Listbox(self.root)
        self.event_listbox.place(x=300, y=60, width=180, height=150)

        self.remove_button = tk.Button(self.root, text="Remove", command=self.remove_event, state='disabled')
        self.remove_button.place(x=345, y=240, width=90, height=30)

        self.event_entry.bind("<KeyRelease>", self.validate_entries)
        self.duration_entry.bind("<KeyRelease>", self.validate_entries)
        self.proportion_entry.bind("<KeyRelease>", self.validate_entries)
        self.event_listbox.bind("<<ListboxSelect>>", self.validate_listbox_selection)

    def init_simulation_parameters(self):
        students_label = tk.Label(self.root, text="Number of students:", anchor='e')
        students_label.place(x=20, y=350, width=130, height=30)

        self.students_entry = tk.Entry(self.root)
        self.students_entry.place(x=160, y=350, width=100, height=30)

        total_observation_time_label = tk.Label(self.root, text="Total observation time:", anchor='e')
        total_observation_time_label.place(x=20, y=410, width=130, height=30)

        self.total_observation_time_entry = tk.Entry(self.root)
        self.total_observation_time_entry.place(x=160, y=410, width=100, height=30)

        time_per_observation_label = tk.Label(self.root, text="Time per observation:", anchor='e')
        time_per_observation_label.place(x=20, y=470, width=130, height=30)

        self.time_per_observation_entry = tk.Entry(self.root)
        self.time_per_observation_entry.place(x=160, y=470, width=100, height=30)

        self.time_per_observation_add_button = tk.Button(self.root, text="Add", command=self.add_time_per_observation, state='disabled')
        self.time_per_observation_add_button.place(x=165, y=510, width=90, height=30)

        self.time_per_observation_listbox = tk.Listbox(self.root)
        self.time_per_observation_listbox.place(x=300, y=470, width=90, height=70)

        self.time_per_observation_remove_button = tk.Button(self.root, text="Remove", command=self.remove_time_per_observation, state='disabled')
        self.time_per_observation_remove_button.place(x=400, y=490, width=90, height=30)

        self.event_entry.bind("<FocusOut>", self.validate_entries)
        self.duration_entry.bind("<FocusOut>", self.validate_entries)
        self.proportion_entry.bind("<FocusOut>", self.validate_entries)
        self.students_entry.bind("<FocusOut>", self.validate_entries)
        self.total_observation_time_entry.bind("<FocusOut>", self.validate_entries)
        self.time_per_observation_entry.bind("<FocusOut>", self.validate_entries)


    def init_run_interface(self):
        self.repeated_simulation_check = tk.IntVar()
        self.repeated_simulation_checkbox = tk.Checkbutton(self.root, text="Repeated Simulation", variable=self.repeated_simulation_check, command=self.toggle_repeated_simulation)
        self.repeated_simulation_checkbox.place(x=100, y=600, width=150, height=30)

        self.repeated_simulation_entry = tk.Entry(self.root, state='disabled')
        self.repeated_simulation_entry.place(x=270, y=600, width=160, height=30)

        self.choose_output_button = tk.Button(self.root, text="Output", command=self.choose_output_file)
        self.choose_output_button.place(x=100, y=660, width=90, height=30)

        self.output_field = tk.Entry(self.root, state='readonly')
        self.output_field.place(x=210, y=660, width=220, height=30)

        self.run_button = tk.Button(self.root, text="Run", state='disabled', command=self.run_simulation)
        self.run_button.place(x=450, y=660, width=100, height=30)

        self.repeated_simulation_entry.bind("<KeyRelease>", self.validate_entries)

    def validate_entries(self, event=None):
        print("Validating entries...")
        event_valid = self.is_event_valid()
        print(f"Event valid: {event_valid}")

        run_valid = self.is_run_valid()
        print(f"Run valid: {run_valid}")

        time_per_observation_valid = self.is_time_per_observation_valid()
        print(f"Time per observation valid: {time_per_observation_valid}")
        
        self.add_button.config(state='normal' if event_valid else 'disabled')
        self.run_button.config(state='normal' if run_valid else 'disabled')
        self.time_per_observation_add_button.config(state='normal' if time_per_observation_valid else 'disabled')


    def validate_listbox_selection(self, event):
        self.remove_button.config(state='normal' if self.event_listbox.curselection() else 'disabled')

    def validate_time_per_observation_selection(self, event):
        self.time_per_observation_remove_button.config(state='normal' if self.time_per_observation_listbox.curselection() else 'disabled')

    def validate_time_per_observation_entry(self, event):
        self.time_per_observation_add_button.config(state='normal' if self.is_time_per_observation_valid() else 'disabled')

    def is_event_valid(self):
        event = self.event_entry.get()
        duration = self.duration_entry.get()
        proportion = self.proportion_entry.get()
        try:
            proportion_value = float(proportion)
            if not (0 < proportion_value <= 100):
                return False
        except ValueError:
            return False
            
        print(f"Event: {event}, Duration: {duration}, Proportion: {proportion}")
        return event and duration.isdigit() and int(duration) > 0


    def is_time_per_observation_valid(self):
        time_per_observation = self.time_per_observation_entry.get()
        valid = time_per_observation.isdigit() and int(time_per_observation) > 0
        print(f"Time per observation: {time_per_observation}")
        print(f"Time per observation valid: {valid}")
        return valid

    def is_run_valid(self):
        students = self.students_entry.get()
        total_observation_time = self.total_observation_time_entry.get()
        repeated_simulation = self.repeated_simulation_entry.get()
        output = self.output_field.get()
        valid = (self.events and self.times_per_observation
            and students.isdigit() and int(students) > 0
            and total_observation_time.isdigit() and int(total_observation_time) > 0
            and (not self.repeated_simulation_check.get() or (repeated_simulation.isdigit() and int(repeated_simulation) > 0))
            and output)
        print(f"Run valid: {valid}")
        return valid

    def toggle_repeated_simulation(self):
        self.repeated_simulation_entry.config(state='normal' if self.repeated_simulation_check.get() else 'disabled')
        self.validate_entries()

    def choose_output_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file:
            self.output_field.config(state='normal')
            self.output_field.delete(0, tk.END)
            self.output_field.insert(0, file)
            self.output_field.config(state='readonly')
        self.validate_entries()

    def add_event(self):
        print("Adding event...")
        event = self.event_entry.get()
        duration = self.duration_entry.get()
        proportion = self.proportion_entry.get()
        
        if self.is_event_valid():
            self.events.append(Event(event, duration, proportion))
            self.event_entry.delete(0, tk.END)
            self.duration_entry.delete(0, tk.END)
            self.proportion_entry.delete(0, tk.END)
            self.event_listbox.insert(tk.END, f"Event: {event}, Duration: {duration}, Proportion: {proportion}")
        self.validate_entries()

    def remove_event(self):
        selected_index = self.event_listbox.curselection()
        if selected_index:
            self.event_listbox.delete(selected_index)
            self.events.pop(selected_index[0])
        self.validate_entries()

    def add_time_per_observation(self):
        time_per_observation = self.time_per_observation_entry.get()
        if self.is_time_per_observation_valid():
            self.times_per_observation.append(int(time_per_observation))
            self.time_per_observation_listbox.insert(tk.END, time_per_observation)
            self.time_per_observation_entry.delete(0, tk.END)
        self.validate_entries()

    def remove_time_per_observation(self):
        selected_index = self.time_per_observation_listbox.curselection()
        if selected_index:
            self.time_per_observation_listbox.delete(selected_index)
            self.times_per_observation.pop(selected_index[0])
        self.validate_entries()

    def run_simulation(self):
        number_of_students = int(self.students_entry.get())
        total_observation_time = int(self.total_observation_time_entry.get())
        output_file = self.output_field.get()
        repeated_simulation = self.repeated_simulation_check.get()
        number_of_simulations = int(self.repeated_simulation_entry.get()) if repeated_simulation else 1
        # Convert self.events into a list of type Event
        events = []
        for event in self.events:
            events.append(Event(event.name, event.duration, event.proportion))
        #print(events, self.times_per_observation, number_of_students, total_observation_time, output_file, repeated_simulation, number_of_simulations)
        #for event in events:
        #    print(event.name, event.duration, event.proportion)
        simulator = BROMPSimulator(self.events, self.times_per_observation, number_of_students, total_observation_time)
        simulator.run(output_file)
        messagebox.showinfo("Run", "Simulation has been run.")

if __name__ == "__main__":
    root = tk.Tk()
    app = EventManager(root)
    root.mainloop()
