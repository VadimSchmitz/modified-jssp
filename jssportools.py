"""Minimal jobshop example."""
import collections
from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import numpy as np

def main():
    """Minimal jobshop problem."""
    # Data.
    jobs_data = [  # task = (machine_id, processing_time).
        [(0, 3), (2, 4), (3, 6)],  # Job1
        [(0, 2), (1, 1), (2, 2), (3,4)],  # Job2
        [(0, 4), (1, 6)],  # Job3
        [(0, 3), (1,3), (3,8)], #job4
        [(0,4), (1,4) , (2,4), (3,4)], #job 5
        [(0,2), (1,2) , (2,8), (3,2)], #job 6
        [(0,4), (1,2) , (2,8)], #job 7
        [(0,4), (1,2)], #job 8
        [(0,5), (3,2)], #job 9
    ]

    arrival_time = [0, 3, 5 ,10, 15, 20, 18, 30, 22]

    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
    all_machines = range(machines_count)
    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Create the model.
    model = cp_model.CpModel()

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('task_type', 'start end interval')
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple('assigned_task_type',
                                                'start job index duration')

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)

    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine = task[0]
            duration = task[1]
            suffix = '_%i_%i' % (job_id, task_id)
            start_var = model.NewIntVar(0, horizon, 'start' + suffix)
            end_var = model.NewIntVar(0, horizon, 'end' + suffix)
            interval_var = model.NewIntervalVar(start_var, duration, end_var,
                                                'interval' + suffix)
            all_tasks[job_id, task_id] = task_type(start=start_var,
                                                   end=end_var,
                                                   interval=interval_var)
            machine_to_intervals[machine].append(interval_var)

    # Create and add disjunctive constraints.
    for machine in all_machines:
        model.AddNoOverlap(machine_to_intervals[machine])

    # create arrival time constraint
    x = 0
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            model.Add(all_tasks[job_id, task_id].start >= arrival_time[x])
        x = x + 1

    # Precedences inside a job.
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            model.Add(all_tasks[job_id, task_id +
                                1].start >= all_tasks[job_id, task_id].end)

    # Makespan objective.
    obj_var = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(obj_var, [
        all_tasks[job_id, len(job) - 1].end
        for job_id, job in enumerate(jobs_data)
    ])
    model.Minimize(obj_var)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Solution:')
        # Create one list of assigned tasks per machine.
        assigned_jobs = collections.defaultdict(list)
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine = task[0]
                assigned_jobs[machine].append(
                    assigned_task_type(start=solver.Value(
                        all_tasks[job_id, task_id].start),
                                       job=job_id,
                                       index=task_id,
                                       duration=task[1]))

        # Create per machine output lines.
        holder = []
        for i in range(len(assigned_jobs)):
            holder.append([])
            for j in range(len(assigned_jobs[i])):
                holder[i].append((assigned_jobs[i][j].start, assigned_jobs[i][j].start + assigned_jobs[i][j].duration, assigned_jobs[i][j].job, assigned_jobs[i][j].index))

        print(holder)
        output = ''
        for machine in all_machines:
            # Sort by starting time.
            assigned_jobs[machine].sort()
            sol_line_tasks = 'Machine ' + str(machine) + ': '
            sol_line = '           '

            for assigned_task in assigned_jobs[machine]:
                name = 'job_%i_task_%i' % (assigned_task.job,
                                           assigned_task.index)
                # Add spaces to output to align columns.
                sol_line_tasks += '%-15s' % name

                start = assigned_task.start
                duration = assigned_task.duration
                sol_tmp = '[%i,%i]' % (start, start + duration)
                # Add spaces to output to align columns.
                sol_line += '%-15s' % sol_tmp

            sol_line += '\n'
            sol_line_tasks += '\n'
            output += sol_line_tasks
            output += sol_line

        # Finally print the solution found.
        print(f'Optimal Schedule Length: {solver.ObjectiveValue()}')
        #plotting
        last = 0
        x = holder
        fig, ax = plt.subplots()
        for i,evt in enumerate(holder): 
            for p,task in enumerate(evt):   
                
                ax.barh(i,width=evt[p][1]-evt[p][0] ,left=evt[p][0], color="lightgray", edgecolor="black", label="test")
                ax.text(evt[p][0] + 0.1 , i, str("Job %s\nTask %s\n Time %s" % (evt[p][2] + 1, evt[p][3] + 1, str(evt[p][1]-evt[p][0]))), color='black', fontweight='bold')

                #time spent doing operations
                print("time spent doing stuff", evt[p][1]-evt[p][0])
                print("arrival time", arrival_time[i])


                #logic for lenght of x axis
                if (evt[p][1]> last):
                    last = evt[p][1] + 5

        #y axis amount of quays
        ax.set_yticks(range(len(x)))
        plt.xticks(np.arange(0,last,1))
        ax.set_yticklabels([f'Quay {i+1}' for i in range(len(holder))])
        ax.invert_yaxis()
        plt.show()


        #benchmarks
    else:
        print('No solution found.')

    # Statistics.
    print('\nStatistics')
    print('  - conflicts: %i' % solver.NumConflicts())
    print('  - branches : %i' % solver.NumBranches())
    print('  - wall time: %f s' % solver.WallTime())


if __name__ == '__main__':
    main()