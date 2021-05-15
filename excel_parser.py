import pandas as pd

curr_dat_filename = "data"  # do not end with .dat
excel_file_name = 'new excel template - alex.xlsx'  # ends with .xlsx
excel_sheet_name = 'Inputs'
default_df = pd.read_excel(excel_file_name, sheet_name=excel_sheet_name)


def parse_csv(df=default_df):
    df.columns = ["Course Preferences",
                  "Course Rankings",
                  "Blank",
                  "Alternatives",
                  "Total Number of Courses",
                  'Set 1', 'Set 2', 'Set 3', 'Set 4', 'Set 5', 'Set 6', 'Set 7', 'Set 8', 'Set 9', 'Set 10', 'Set 11', 'Set 12', 'Set 13', 'Set 14', 'Set 15', 'Set 16', 'Set 17', 'Set 18', 'Set 19', 'Set 20', 'Set 21', 'Set 22', 'Set 23', 'Set 24', 'Set 25', 'Set 26', 'Set 27', 'Set 28', 'Set 29', 'Set 30', 'Set 31', 'Set 32', 'Set 33', 'Set 34', 'Set 35'
                  ]  # FIXME: Remove hardcoding upper limit of alternates

    # Removes nan values from lists
    def clean_list(l):
        return [x for x in l if str(x) != 'nan']

    # Course Preferences:
    courses = df["Course Preferences"].tolist()
    course_rankings = df["Course Rankings"].tolist()
    cleaned_courses = clean_list(courses)
    set_courses = set(cleaned_courses)
    # print(set_courses)
    cleaned_course_rankings = [int(x)
                               for x in course_rankings if str(x) != 'nan']
    # Creates dictionary in {course: ranking} format
    courses_cost = {}
    for i in range(len(cleaned_courses)):
        courses_cost[cleaned_courses[i]] = cleaned_course_rankings[i]

    # Alternates:
    x = df.iloc[:, 4:]
    num_alts = x.shape[1]
    lower_bounds = {}
    upper_bounds = {}
    alternates_dict = {}
    set_alternates = set()
    for i in range(num_alts):
        curr_alt_id = "alternates" + str(i)
        curr_alt = df.iloc[:, i+4]
        curr_alt = [x for x in curr_alt if str(x) != 'nan']
        if curr_alt == []:
            break
        set_alternates.add(curr_alt_id)
        lower_bounds[curr_alt_id] = int(curr_alt[0])
        upper_bounds[curr_alt_id] = int(curr_alt[1])
        alternates_dict[curr_alt_id] = curr_alt[2:]

    return (set_courses, courses_cost,  set_alternates, alternates_dict, lower_bounds, upper_bounds)
