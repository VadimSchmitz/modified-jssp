from itertools import product
from logging import log
from mip import Model, BINARY
from datetime import datetime
from datetime import timedelta 
import xlsxwriter

workbook = xlsxwriter.Workbook('output.xlsx')
worksheet = workbook.add_worksheet("output")
row = 2
col = 2

n = m = 3

times = [[2, 1, 2],
         [1, 2, 2],
         [1, 2, 1]]

M = sum(times[i][j] for i in range(n) for j in range(m))

machines = [[2, 0, 1],
            [1, 2, 0],
            [2, 1, 0]]

model = Model('JSSP')

c = model.add_var(name="C")
x = [[model.add_var(name='x({},{})'.format(j+1, i+1))
      for i in range(m)] for j in range(n)]
y = [[[model.add_var(var_type=BINARY, name='y({},{},{})'.format(j+1, k+1, i+1))
       for i in range(m)] for k in range(n)] for j in range(n)]

model.objective = c

for (j, i) in product(range(n), range(1, m)):
    model += x[j][machines[j][i]] - x[j][machines[j][i-1]] >= \
        times[j][machines[j][i-1]]

for (j, k) in product(range(n), range(n)):
    if k != j:
        for i in range(m):
            model += x[j][i] - x[k][i] + M*y[j][k][i] >= times[k][i]
            model += -x[j][i] + x[k][i] - M*y[j][k][i] >= times[j][i] - M

for j in range(n):
    model += c - x[j][machines[j][m - 1]] >= times[j][machines[j][m - 1]]

model.optimize()
#outputting data
machine_count = 0
for i in machines:
    machine_count = machine_count + 1

task_count = 0
for i in times:
    task_count = task_count + 1


holder = []

for i in range(machine_count):
  holder.append([])


machine_one = [] 
machine_two = []
machine_three = []


print(holder)
# print("Completion time: ", c.x)


count = 0
for (j, i) in product(range(n), range(m)):
    #j+1 = task 
    #i+1 = machine
    converted_time = x[j][i].x
    task_number = j+1

    # if i  == count:
    # print(task_number, converted_time)
    holder[i].append([task_number,converted_time])


    count = count + 1
    print("task %d starts on machine %d at time %g  " % (j+1, i+1, x[j][i].x))
    i = i + 1
    row += 1

print(holder)


#sort

machine_one_sorted_by_second = sorted(machine_one, key=lambda tup: tup[1])
machine_two_sorted_by_second = sorted(machine_two, key=lambda tup: tup[1])
machine_three_sorted_by_second = sorted(machine_three, key=lambda tup: tup[1])

sorted_holder = []
for i in range(machine_count):
    sorted_holder.append(sorted(holder[i], key=lambda tup: tup[1]))

print(sorted_holder)


col = 1
row = 1

#TODO dynamically change to correct date
worksheet.write(row,col-1,"monday")

count = 1
for _ in range(machine_count):
    worksheet.write(row,col,"location "+str(count))
    col = col+1
    count = count+1

start_time = datetime(2020,12,7,0,0,0,0)
#needs to be placed where you can easily change it

#keep this for later? 
#'%d %b, %Y %H:%M:%S'

timespan = int(c.x)
for _ in range(timespan * 2 + 1):
    worksheet.write(row+1,col-machine_count-1,start_time.strftime('%H:%M'))
    row = row + 1
    start_time = start_time + timedelta(minutes=30)

#populating table
#to go down add 1
#initial start
print(sorted_holder[0])
col = 2 + int(sorted_holder[0][0][1]*2)
#to go to right add
row = 1
x = 1    
worksheet.write(col,row,"1")

for machine in sorted_holder:

    for i in range(len(machine)): 
        try:
            if i < len(machine)-1:
                first = machine[i][x]
                second = machine[i+1][x]
                diff = int(first -second)
        except IndexError:
            print('end of list')

        #invert number
        if diff < 0:
            diff = diff * -1
        print(first, second , diff)
        worksheet.write(col,row, f'vessel: {machine[i][0]} \n stop: {i+1}')
        col = col+ (diff * 2)
    #re initialize col and row
    col = 2
    row = row + 1

workbook.close()

