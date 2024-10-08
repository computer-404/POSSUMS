import tkinter as tk
from tkinter import messagebox, filedialog
import random
import math
import numpy as np

class HiddenMarkovModel:
    def __init__(self, events):
        self.events = events
        self.num_events = len(events)
        self.transition_matrix = self.generate_transition_matrix()
    
    def generate_transition_matrix(self):
        # Assuming equal transition probabilities for simplicity
        transition_matrix = np.full((self.num_events, self.num_events), 1.0 / self.num_events)
        return transition_matrix
    
    def get_next_state(self, current_state_index):
        return np.random.choice(self.num_events, p=self.transition_matrix[current_state_index])
    
    def get_steady_state_distribution(self):
        # Calculate the steady state distribution using eigenvalues and eigenvectors
        eigvals, eigvecs = np.linalg.eig(self.transition_matrix.T)
        stationary = eigvecs[:, np.isclose(eigvals, 1)]
        stationary = stationary / stationary.sum()
        return stationary.real.flatten()

    def calculate_observation_likelihood(self, observed_states):
        # Calculate the likelihood of observing a given sequence of states
        likelihood = 1.0
        current_state = observed_states[0]
        for next_state in observed_states[1:]:
            likelihood *= self.transition_matrix[current_state][next_state]
            current_state = next_state
        return likelihood

# Event Class
class Event:
    '''
    Summary: Constructor to population an event object
    '''
    def __init__(self, name, duration, proportion):
        self.name = name
        self.duration = duration
        self.proportion = proportion

    '''
    Summary: Return the name of the event
    '''
    def get_name(self):
        return self.name

    '''
    Summary: Return the duration of the event
    '''
    def get_duration(self):
        return self.duration

    '''
    Summary: Return the proportion of the event
    '''
    def get_proportion(self):
        return self.proportion

    '''
    Summary: Return a formatted string representation of an event
    '''
    def __str__(self):
        return f"{self.name} - {self.duration} - {self.proportion}"

# Run Event Data Class
class ClassRunEventData:
    '''
    Summary: Constructor to populate a run event data class object
    '''
    def __init__(self, total_tally, percentage):
        self.total_tally = total_tally
        self.percentage = percentage

    '''
    Summary: Return the total tally of the event's data
    '''
    def get_total_tally(self):
        return self.total_tally

    '''
    Summary: Return the percentage
    '''
    def get_percentage(self):
        return self.percentage

# Simulator Class
class BROMPSimulator:
    '''
    Summary: Constructor to populate a simulator object
    '''
    def __init__(self, events, timesPerObservation, numberOfStudents, totalObservationTime):
        self.events = events
        self.timesPerObservation = timesPerObservation
        self.numberOfStudents = numberOfStudents
        self.totalObservationTime = totalObservationTime
        self.randomGenerator = random.Random()
        self.hmm = HiddenMarkovModel(events)  # Initialize the HMM with the events
    
    '''
    Summary: Run the simulation
    Parameter: output_file - the file to output the results to
    '''
    def run(self, output_file):
        if app.repeated_simulation_check.get():
            self.run_repeated_simulation(output_file)
        else:
            self.run_single_simulation(output_file)
    
    '''
    Summary: Run the simulation multiple times as specified by user
    Parameter: output_file - the file to output the results
    '''
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
        self.output_cumulative_results(cumulative_run_data, output_file)
        
    '''
    Summary: Output the cumulative results to a file, using specific formatting and calculations
    Parameter: cumulative_run_data - the cumulative data collected throughout the simulation
    Parameter: output_file - the file to output the results
    '''
    def output_cumulative_results(self, cumulative_run_data, output_file):
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
    
    '''
    Summary: Compute the results at the level of the class
    Parameter: student_observations - the observations made by the students
    '''
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
    
    '''
    Summary: Run a single simulation
    Parameter: output_file - the file to output the results
    '''
    def run_single_simulation(self, output_file):
        with open(output_file, 'w') as file:
            student_states = self.generate_students_states()
            # Example of using extended HMM functionality
            steady_state_distribution = self.hmm.get_steady_state_distribution()
            print("Steady State Distribution:", steady_state_distribution, file=file)

            for time_per_observation in self.timesPerObservation:
                self.compute_and_output_observation_results(student_states, time_per_observation, file)
            file.write("Randomized events:\r\n\r\n")
            self.write_student_states(student_states, file)

    '''
    Summary: Calls functions to compute and output the observation results obtained from the simulation
    Parameter: student_states - the states of each student, based on the simulation
    Parameter: time_per_observation - the time per observation
    Parameter: file - the file to output the results
    '''
    def compute_and_output_observation_results(self, student_states, time_per_observation, file):
        student_observations = self.compute_observation_results(student_states, time_per_observation)
        real_event_counts = self.compute_real_event_counts(student_states)
        self.write_observation_results(real_event_counts, student_observations, time_per_observation, file)

    '''
    Summary: Computes the observation results obtained from the simulation
    Parameter: student_states - the states of each student, based on the simulation
    Parameter: time_per_observation - the time per observation
    '''
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
    
    '''
    Summary: Compute the real event counts
    Parameter: student_states - the states of each student, based on the simulation
    '''
    def compute_real_event_counts(self, student_states):
        real_event_counts = {}
        for event in self.events:
            real_event_counts[event] = 0
        for event in student_states[0]:
            real_event_counts[event] = real_event_counts[event] + 1
        return real_event_counts
    
    '''
    Summary: Write the observation results to a file
    Parameter: real_event_counts - the real event counts
    Parameter: student_observations - the observations for each student
    Parameter: time_per_observation - the time per observation
    Parameter: file - the file to output the results
    '''
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
    
    '''
    Summary: Function to generate the states for each student
    '''
    def generate_students_states(self):
        student_states = []
        for i in range(self.numberOfStudents):
            student_states.append(self.generate_states_for_one_student())
        return student_states
    
    '''
    Summary: Function to generate the state for a single student, executing the Monte Carlo Simulation
    '''
    def generate_states_for_one_student(self):
        states = []
        current_event_index = np.random.choice(len(self.events))  # Start with a random event
        total_time_units = self.totalObservationTime

        while total_time_units > 0:
            event = self.events[current_event_index]
            duration = int(event.get_duration())
            for _ in range(duration):
                if total_time_units > 0:
                    states.append(event)
                    total_time_units -= 1
            # Transition to the next event using the HMM
            current_event_index = self.hmm.get_next_state(current_event_index)

        return states
    
    '''
    Summary: Function to write the student states to a file
    Parameter: student_states - the states of each student
    Parameter: file - the file to output the student states
    '''
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

# Event Manager Class to handle the GUI
class EventManager:
    '''
    Summary: Constructor to populate an event manager object
    '''
    def __init__(self, root):
        self.root = root
        self.root.title("POSSUMS 1.0")
        self.root.geometry('550x840')

        self.events = []
        self.times_per_observation = []

        self.init_event_input_fields()
        self.init_simulation_parameters()
        self.init_run_interface()

    '''
    Summary: Initialize the event input fields into the GUI
    '''
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

    '''
    Summary: Initialize the simulation parameters input fields into the GUI
    '''
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

    '''
    Summary: Initialize the run interface into the GUI, allowing you to select a file to save the output to
    '''
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

    '''
    Summary: Validate the user entires to ensure they are valid
    '''
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

    '''
    Summary: Validate the selection in the listbox
    '''
    def validate_listbox_selection(self, event):
        self.remove_button.config(state='normal' if self.event_listbox.curselection() else 'disabled')

    '''
    Summary: Validate the time per observation entry
    '''
    def validate_time_per_observation_selection(self, event):
        self.time_per_observation_remove_button.config(state='normal' if self.time_per_observation_listbox.curselection() else 'disabled')

    '''
    Summary: Validate the time per observation entry
    '''
    def validate_time_per_observation_entry(self, event):
        self.time_per_observation_add_button.config(state='normal' if self.is_time_per_observation_valid() else 'disabled')

    '''
    Summary: Validate the event data
    '''
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

    '''
    Summary: Validate the time per observation entry
    '''
    def is_time_per_observation_valid(self):
        time_per_observation = self.time_per_observation_entry.get()
        valid = time_per_observation.isdigit() and int(time_per_observation) > 0
        print(f"Time per observation: {time_per_observation}")
        print(f"Time per observation valid: {valid}")
        return valid

    '''
    Summary: Check if the run is valid and all the entries are valid
    '''
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

    '''
    Summary: Allow the user to toggle if they would like to have repeated simulations
    '''
    def toggle_repeated_simulation(self):
        self.repeated_simulation_entry.config(state='normal' if self.repeated_simulation_check.get() else 'disabled')
        self.validate_entries()

    '''
    Summary: Allow the user to choose the output file from their file directory system
    '''
    def choose_output_file(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file:
            self.output_field.config(state='normal')
            self.output_field.delete(0, tk.END)
            self.output_field.insert(0, file)
            self.output_field.config(state='readonly')
        self.validate_entries()

    '''
    Summary: Add an event to the list of events
    '''
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

    '''
    Summary: Remove an event from the list of events
    '''
    def remove_event(self):
        selected_index = self.event_listbox.curselection()
        if selected_index:
            self.event_listbox.delete(selected_index)
            self.events.pop(selected_index[0])
        self.validate_entries()

    '''
    Summary: Add the time per observation to the list of times per observation
    '''
    def add_time_per_observation(self):
        time_per_observation = self.time_per_observation_entry.get()
        if self.is_time_per_observation_valid():
            self.times_per_observation.append(int(time_per_observation))
            self.time_per_observation_listbox.insert(tk.END, time_per_observation)
            self.time_per_observation_entry.delete(0, tk.END)
        self.validate_entries()

    '''
    Summary: Remove the time per observation from the list of times per observation
    '''
    def remove_time_per_observation(self):
        selected_index = self.time_per_observation_listbox.curselection()
        if selected_index:
            self.time_per_observation_listbox.delete(selected_index)
            self.times_per_observation.pop(selected_index[0])
        self.validate_entries()

    '''
    Summary: Run the simulation
    '''
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

# Main function to run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = EventManager(root)
    root.mainloop()