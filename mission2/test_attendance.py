import pytest
from attendance import (
    AttendanceManager, GradeFactory, Player, PresentRemovePolicy
)

INVALID_FILE_PATH = "invalid_file.txt"
TMP_ATTENDANCE_FILE = "attendance.txt"
SOMEONE = "Someone"
SOMEDAY = "Someday"


@pytest.fixture
def attendance_path(tmp_path):
    return tmp_path / TMP_ATTENDANCE_FILE


def get_attendance_manager(attendance_path):
    attendance_manager = AttendanceManager(
        attendance_path, Player, GradeFactory, PresentRemovePolicy
    )
    attendance_manager.read_attendance_file()
    attendance_manager.get_player_dict_from_attendance()
    return attendance_manager


def test_invalid_attendance_file():
    attendance_manager = AttendanceManager(
        INVALID_FILE_PATH, Player, GradeFactory, PresentRemovePolicy
    )
    with pytest.raises(FileNotFoundError):
        attendance_manager.read_attendance_file()


def test_invalid_day(attendance_path):
    attendance_path.write_text(f"{SOMEONE} {SOMEDAY}")
    attendance_manager = AttendanceManager(
        attendance_path, Player, GradeFactory, PresentRemovePolicy
    )

    with pytest.raises(ValueError):
        attendance_manager.read_attendance_file()


@pytest.mark.parametrize(
    "day,basic_point",
    [("wednesday", 3), ("saturday", 2), ("sunday", 2), ("monday", 1)]
)
def test_player_basic_point(attendance_path, day, basic_point):
    attendance_path.write_text(f"{SOMEONE} {day}")

    attendance_manager = get_attendance_manager(attendance_path)
    assert attendance_manager.player_dict[SOMEONE].point == basic_point


@pytest.mark.parametrize(
    "day,basic_point",
    [("wednesday", 3), ("saturday", 2), ("sunday", 2), ("tuesday", 1)],
)
def test_player_bonus_point(attendance_path, day, basic_point):
    attendance_file_content = ""
    for i in range(10):
        attendance_file_content += f"{SOMEONE} {day}\n"
    attendance_path.write_text(attendance_file_content)

    attendance_manager = get_attendance_manager(attendance_path)

    point = basic_point * 10
    if day == "wednesday" or day == "saturday" or day == "sunday":
        point += 10
    assert attendance_manager.player_dict[SOMEONE].point == point


@pytest.mark.parametrize(
    "day,basic_point,grade",
    [
        ("wednesday", 3, "GOLD"),
        ("saturday", 2, "SILVER"),
        ("sunday", 2, "SILVER"),
        ("thursday", 1, "NORMAL"),
    ],
)
def test_player_grade(attendance_path, day, basic_point, grade):
    attendance_file_content = ""
    for i in range(15):
        attendance_file_content += f"{SOMEONE} {day}\n"
    attendance_path.write_text(attendance_file_content)

    attendance_manager = get_attendance_manager(attendance_path)
    assert attendance_manager.player_dict[SOMEONE].grade.name == grade


@pytest.mark.parametrize(
    "day,basic_point,grade",
    [
        ("wednesday", 3, "GOLD"),
        ("saturday", 2, "SILVER"),
        ("friday", 1, "NORMAL")
     ],
)
def test_player_status(capsys, attendance_path, day, basic_point, grade):
    attendance_file_content = ""
    for i in range(15):
        attendance_file_content += f"{SOMEONE} {day}\n"
    attendance_path.write_text(attendance_file_content)

    attendance_manager = get_attendance_manager(attendance_path)
    attendance_manager.print_player_status()

    captured = capsys.readouterr()
    point = basic_point * 15
    if day == "wednesday" or day == "saturday" or day == "sunday":
        point += 10
    status = f"NAME : {SOMEONE}, POINT : {point}, GRADE : {grade}\n"
    assert captured.out == status


@pytest.mark.parametrize("day", ["wednesday", "sunday"])
def test_empty_removed_player(capsys, attendance_path, day):
    attendance_path.write_text(f"{SOMEONE} {day}")

    attendance_manager = get_attendance_manager(attendance_path)
    attendance_manager.print_removed_player()

    captured = capsys.readouterr()
    empty_removed_player = "\nRemoved player\n"
    empty_removed_player += "==============\n"
    assert captured.out == empty_removed_player


@pytest.mark.parametrize("lines", [30, 50])
def test_empty_removed_player_not_normal(capsys, attendance_path, lines):
    attendance_file_content = ""
    for i in range(lines):
        attendance_file_content += f"{SOMEONE} monday\n"
    attendance_path.write_text(attendance_file_content)

    attendance_manager = get_attendance_manager(attendance_path)
    attendance_manager.print_removed_player()

    captured = capsys.readouterr()
    empty_removed_player = "\nRemoved player\n"
    empty_removed_player += "==============\n"
    assert captured.out == empty_removed_player


def test_removed_player(capsys, attendance_path):
    attendance_file_content = ""
    for i in range(29):
        attendance_file_content += f"{SOMEONE} monday\n"
    attendance_path.write_text(attendance_file_content)

    attendance_manager = get_attendance_manager(attendance_path)
    attendance_manager.print_removed_player()

    captured = capsys.readouterr()
    removed_player = "\nRemoved player\n"
    removed_player += "==============\n"
    removed_player += f"{SOMEONE}\n"
    assert captured.out == removed_player


def test_print_player_status_and_removed_player(capsys, attendance_path):
    attendance_file_content = ""
    for i in range(29):
        attendance_file_content += f"{SOMEONE} monday\n"
    attendance_path.write_text(attendance_file_content)

    attendance_manager = AttendanceManager(
        attendance_path, Player, GradeFactory, PresentRemovePolicy
    )
    attendance_manager.print_status_and_removed_player()

    captured = capsys.readouterr()
    status = f"NAME : {SOMEONE}, POINT : 29, GRADE : NORMAL\n"
    removed_player = "\nRemoved player\n"
    removed_player += "==============\n"
    removed_player += f"{SOMEONE}\n"
    assert captured.out == status + removed_player
