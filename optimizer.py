import json
from ortools.linear_solver import pywraplp
from collections import defaultdict
import excel_parser
solver = pywraplp.Solver.CreateSolver('SCIP')

############### DATA #############
processed_data = {}

with open(r"rawData/course_data3.json", encoding="utf-8") as f:
    raw_data = json.load(f)

for item in raw_data["data"]["courses"].keys():
    newKey = raw_data["data"]["courses"][item]["courseCode"]
    processed_data[newKey] = raw_data["data"]["courses"][item]

########## FUNCTIONS ##############


def optimizer(data, useCsv=False, currTerm=True):

    ########## Input Format ###############
    if useCsv:
        set_courses, courses_cost, set_alternates, alternates_dict, lower_bounds, upper_bounds = excel_parser.parse_csv(
            df)
    else:
        set_courses, courses_cost, set_alternates, alternates_dict, lower_bounds, upper_bounds = data

    ###############################
    """
    course_bool is a dictionary where the key is the 
    course name and the value is an integer variable that the
    solver sets in order to optimize the cost.
    0 stands for not taking the course and
    1 stands for taking it.
    """
    courses_bool = {}
    for course in set_courses:
        courses_bool[course] = solver.IntVar(0, 1, '')

    #######################
    # Time constraint:
    """ 
    To encode the constraint that the program should not select two
    courses that are taking place at the same time/overlap, we break time
    into discrete intervals of ten minutes, and then ensure that for each 
    discrete timestep, at most only one course is selected.

    time_course_bool[(course, time)] = 1 if course taking place at that time,
    otherwise 0
    """
    course_time_bool = {}
    set_current_time_ids = set()
    discrete_times = []
    for k in range(7, 24):
        for j in range(0, 6):
            curr_time = "0" + str(k) + str(j) + "0"
            curr_time = int(curr_time)
            discrete_times.append(curr_time)

    days = "MTWRF"
    for curr_time in discrete_times:
        for day in days:
            curr_time_id = day + str(curr_time)
            set_current_time_ids.add(curr_time_id)
            for course in set_courses:
                for item in processed_data[course]["courseSchedule"]:
                    if day in item["scheduleDays"]:
                        start_time = item["scheduleStartTime"]
                        end_time = item["scheduleEndTime"]
                        # Removing the colon from "hh:mm" and then converting it to an int
                        start_time = int(start_time[0:2] + start_time[3:])
                        end_time = int(end_time[0:2] + end_time[3:])
                        # Not strictly greater than or less than because
                        # courses can take place back to back.
                        after_start_time = curr_time > start_time
                        before_end_time = curr_time < end_time

                        if after_start_time and before_end_time:
                            course_time_bool[(course, curr_time_id)] = 1

    # (Because defaultdict isn't playing well with or-tools)
    for time_id in set_current_time_ids:
        for course in set_courses:
            if (course, time_id) not in course_time_bool:
                course_time_bool[(course, time_id)] = 0

    ################################
    # No Two Same Courses Constraint:
    """
    This constraint prevents the program from selecting
    two courses that are the same (but are different sections
    or on different campuses)
    """
    course_same_bool = {}
    underlying_courses = {}
    # Grouping courses that are the same together:
    for course in set_courses:
        course_components = course.split(" ")
        # Example: ENGR 190AV HM-01 -> ENGR 190AV
        main_components = course_components[0] + " " + course_components[1]
        if main_components in underlying_courses:
            underlying_courses[main_components].append(course)
        else:
            underlying_courses[main_components] = [course]

    """
    Creating a dictionary where the key is
    (course, underlying_course) and its value is
    1 if course is essentially the underlying course and
    0 otherwise.
    Example:
    course_same_bool[(ENGR 190AV HM-01, ENGR 190AV)] = 1
    but
    course_same_bool[(ENGR 190AV HM-01, CSCI 140)] = 0
    """
    for underlying_course in underlying_courses.keys():
        for course in set_courses:
            if underlying_course in course:
                course_same_bool[(course, underlying_course)] = 1
            else:
                course_same_bool[(course, underlying_course)] = 0

    ########################################
    ###### ALTERNATES ######################
    """
    For every course that falls under an alternate_id filter
    set by the user, the value of 
    course_alt_bool[(course, alternate_id)] will be 1. (Otherwise 0.)
    """
    course_alt_bool = defaultdict()
    for alternate_id in set_alternates:
        for course in set_courses:
            for alt in alternates_dict[alternate_id]:
                if alt in course:
                    course_alt_bool[(course, alternate_id)] = 1

    # (Because defaultdict isn't playing well with or-tools, this is
    # manually coding in the "otherwise 0" part.
    for alternate_id in set_alternates:
        for course in set_courses:
            if (course, alternate_id) not in course_alt_bool:
                course_alt_bool[(course, alternate_id)] = 0

    # CONSTRAINTS:

    # UNIQUENESS CONSTRAINT
    for underlying_course in underlying_courses.keys():
        solver.Add(solver.Sum([course_same_bool[(
            course, underlying_course)]*courses_bool[course] for course in set_courses]) <= 1)

    # TIME CONFLICT CONSTRAINT
    for time_id in set_current_time_ids:
        solver.Add(solver.Sum([course_time_bool[(course, time_id)]
                   * courses_bool[course] for course in set_courses]) <= 1)

    # ALTERNATES CONSTRAINT
    for alternate_id in set_alternates:
        solver.Add(solver.Sum([course_alt_bool[(course, alternate_id)]*courses_bool[course]
                   for course in set_courses]) <= upper_bounds[alternate_id])

        solver.Add(solver.Sum([course_alt_bool[(course, alternate_id)]*courses_bool[course]
                   for course in set_courses]) >= lower_bounds[alternate_id])

    # Objective
    objective_terms = []
    for course in set_courses:
        objective_terms.append(courses_bool[course] * courses_cost[course])

    solver.Maximize(solver.Sum(objective_terms))

    # Solve
    status = solver.Solve()

    res = []  # list of courses that the user should take
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        # print('Total cost = ', solver.Objective().Value(), '\n')
        for course in set_courses:
            if courses_bool[course].solution_value() > 0.5:
                courseName = processed_data[course]["courseName"]
                # print(course)
                res.append((course, courseName))
    else:
        return[("Status: ", status)]

    return (solver.Objective().Value(), res)


def courseToHyperScheduleFormat(listOfCourses):
    res = []
    for course, _ in listOfCourses:
        currCourseInfo = processed_data[course]
        currCourseInfo["selected"] = True
        res.append(currCourseInfo)

    # print(res)

    return res
