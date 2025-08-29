from pathlib import Path

ATTENDANCE_PATH = "attendance_weekday_500.txt"

NORMAL = "NORMAL"
SILVER = "SILVER"
GOLD = "GOLD"

MONDAY = "monday"
TUESDAY = "tuesday"
WEDNESDAY = "wednesday"
THURSDAY = "thursday"
FRIDAY = "friday"
SATURDAY = "saturday"
SUNDAY = "sunday"

DAYS = [MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY]
WEEKEND = [SATURDAY, SUNDAY]

DAY_INDEX = {
    MONDAY: 0,
    TUESDAY: 1,
    WEDNESDAY: 2,
    THURSDAY: 3,
    FRIDAY: 4,
    SATURDAY: 5,
    SUNDAY: 6,
}

BASIC_POINT = {
    MONDAY: 1,
    TUESDAY: 1,
    WEDNESDAY: 3,
    THURSDAY: 1,
    FRIDAY: 1,
    SATURDAY: 2,
    SUNDAY: 2,
}


class Attendance:
    def __init__(self, name: str, day: str):
        self.name = name
        self.day = day


def read_attendance_file(attendance_path: str) -> list[Attendance]:
    if not Path(attendance_path).exists():
        raise FileNotFoundError(f"{attendance_path} 파일을 찾을 수 없습니다.")

    attendance_list = []
    with open(attendance_path, encoding="utf-8") as f:
        for line in f.readlines():
            name, day = line.strip().split()
            if day not in DAYS:
                raise ValueError("Invalid day")

            attendance_list.append(Attendance(name, day))
    return attendance_list


def set_name_to_id(attendance_list: list[Attendance]) -> dict[str, int]:
    name_to_id = {}
    for attendance in attendance_list:
        if attendance.name not in name_to_id:
            name_to_id[attendance.name] = len(name_to_id) + 1
    return name_to_id


def set_id_to_name(name_to_id: dict[str, int]) -> dict[int, str]:
    id_to_name = {}
    for player_name in name_to_id:
        id_to_name[name_to_id[player_name]] = player_name
    return id_to_name


def get_wednesday_attendance(
    attendance_list: list[Attendance], name_to_id: dict[str, int]
) -> list[int]:
    wednesday_attendance = [0] * (len(name_to_id) + 1)
    for attendance in attendance_list:
        player_id = name_to_id[attendance.name]
        if attendance.day == WEDNESDAY:
            wednesday_attendance[player_id] += 1
    return wednesday_attendance


def get_weekend_attendance(
    attendance_list: list[Attendance], name_to_id: dict[str, int]
) -> list[int]:
    weekend_attendance = [0] * (len(name_to_id) + 1)
    for attendance in attendance_list:
        player_id = name_to_id[attendance.name]
        if attendance.day in WEEKEND:
            weekend_attendance[player_id] += 1
    return weekend_attendance


def get_basic_point(
    attendance_list: list[Attendance], name_to_id: dict[str, int]
) -> list[int]:
    player_point = [0] * (len(name_to_id) + 1)
    for attendance in attendance_list:
        player_id = name_to_id[attendance.name]
        player_point[player_id] += BASIC_POINT[attendance.day]
    return player_point


def plus_bonus_point(
    id_to_name: dict[int, str],
    player_point: list[int],
    wednesday_attendance: list[int],
    weekend_attendance: list[int],
) -> list[int]:
    for player_id in id_to_name:
        if wednesday_attendance[player_id] > 9:
            player_point[player_id] += 10
        if weekend_attendance[player_id] > 9:
            player_point[player_id] += 10
    return player_point


def get_player_grade(id_to_name: dict[int, str], player_point: list[int]) -> list[str]:
    player_grade = [NORMAL] * len(player_point)
    for player_id in id_to_name:
        if player_point[player_id] >= 50:
            player_grade[player_id] = GOLD
        elif player_point[player_id] >= 30:
            player_grade[player_id] = SILVER
    return player_grade


def print_player_status(
    id_to_name: dict[int, str], player_point: list[int], player_grade: list[str]
):
    for player_id in id_to_name:
        print(
            f"NAME : {id_to_name[player_id]}, "
            f"POINT : {player_point[player_id]}, "
            f"GRADE : {player_grade[player_id]}"
        )


def print_removed_player(
    id_to_name: dict[int, str],
    player_grade: list[str],
    wednesday_attendance: list[int],
    weekend_attendance: list[int],
):
    print("\nRemoved player")
    print("==============")
    for player_id, player_name in id_to_name.items():
        if (
            player_grade[player_id] == NORMAL
            and wednesday_attendance[player_id] == 0
            and weekend_attendance[player_id] == 0
        ):
            print(player_name)


def print_player_status_and_removed_player():
    attendance_list = read_attendance_file(ATTENDANCE_PATH)
    name_to_id = set_name_to_id(attendance_list)
    id_to_name = set_id_to_name(name_to_id)

    wednesday_attendance = get_wednesday_attendance(attendance_list, name_to_id)
    weekend_attendance = get_weekend_attendance(attendance_list, name_to_id)

    player_basic_point = get_basic_point(attendance_list, name_to_id)
    player_total_point = plus_bonus_point(
        id_to_name, player_basic_point, wednesday_attendance, weekend_attendance
    )
    player_grade = get_player_grade(id_to_name, player_total_point)

    print_player_status(id_to_name, player_total_point, player_grade)
    print_removed_player(
        id_to_name, player_grade, wednesday_attendance, weekend_attendance
    )


if __name__ == "__main__":
    print_player_status_and_removed_player()
