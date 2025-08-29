from abc import ABC, abstractmethod
from pathlib import Path
from typing import Type

ATTENDANCE_PATH = "attendance_weekday_500.txt"

NORMAL = "NORMAL"
SILVER = "SILVER"
GOLD = "GOLD"

WEDNESDAY = "wednesday"
SATURDAY = "saturday"
SUNDAY = "sunday"
OTHERS = ["monday", "tuesday", "thursday", "friday"]

WEEKEND = [SATURDAY, SUNDAY]
DAYS = WEEKEND + [WEDNESDAY] + OTHERS


class Grade(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def is_match(self) -> bool:
        pass


class Gold(Grade):
    @property
    def name(self) -> str:
        return GOLD

    def is_match(self, point) -> bool:
        if point >= 50:
            return True
        return False


class Silver(Grade):
    @property
    def name(self) -> str:
        return SILVER

    def is_match(self, point) -> bool:
        if 30 <= point < 50:
            return True
        return False


class Normal(Grade):
    @property
    def name(self) -> str:
        return NORMAL

    def is_match(self, point) -> bool:
        if point < 30:
            return True
        return False


class GradeFactory:
    _registry = [Gold, Silver, Normal]

    @classmethod
    def create_grade(cls, point: int) -> Grade:
        for grade_class in cls._registry:
            grade = grade_class()
            if grade.is_match(point):
                return grade
        raise ValueError(f"Matching grade is not found for point {point}")


class RemovePolicy(ABC):
    @classmethod
    def is_removed(
        cls,
        grade: Grade,
        attendance_wednesday: int,
        attendance_weekend: int,
        attendance_others,
    ) -> bool:
        pass


class PresentRemovePolicy(RemovePolicy):
    @classmethod
    def is_removed(
        cls,
        grade: Grade,
        attendance_wednesday: int,
        attendance_weekend: int,
        attendance_others,
    ) -> bool:
        if (
            grade.name == NORMAL
            and attendance_wednesday == 0
            and attendance_weekend == 0
        ):
            return True
        return False


class Player:
    _id = 0
    WEDNESDAY_POINT = 3
    WEEKEND_POINT = 2

    def __init__(
        self,
            name: str,
            grade_factory: Type[GradeFactory],
            remove_policy: Type[RemovePolicy]
    ):
        Player._id += 1
        self._id = Player._id
        self._name = name
        self._grade_factory = grade_factory
        self._remove_policy = remove_policy

        self._attendance_wednesday = 0
        self._attendance_weekend = 0
        self._attendance_others = 0

    def attend(self, day):
        if day == WEDNESDAY:
            self._attendance_wednesday += 1
        elif day in WEEKEND:
            self._attendance_weekend += 1
        else:
            self._attendance_others += 1

    @property
    def basic_point(self) -> int:
        point = self._attendance_others
        point += self._attendance_wednesday * Player.WEDNESDAY_POINT
        point += self._attendance_weekend * Player.WEEKEND_POINT
        return point

    @property
    def bonus_point(self) -> int:
        point = 0
        if self._attendance_wednesday > 9:
            point += 10
        if self._attendance_weekend > 9:
            point += 10
        return point

    @property
    def point(self) -> int:
        return self.basic_point + self.bonus_point

    @property
    def grade(self) -> Grade:
        grade = self._grade_factory.create_grade(self.point)
        return grade

    def print_status(self):
        print(
            f"NAME : {self._name}, "
            f"POINT : {self.point}, "
            f"GRADE : {self.grade.name}"
        )

    def is_removed(self) -> bool:
        if self._remove_policy.is_removed(
            self.grade,
            self._attendance_wednesday,
            self._attendance_weekend,
            self._attendance_others,
        ):
            return True
        return False


class Attendance:
    def __init__(self, name: str, day: str):
        self.name = name
        self.day = day


class AttendanceManager:
    def __init__(
        self,
        attendance_path: str,
        player: Type[Player],
        grade_factory: Type[GradeFactory],
        remove_policy: Type[RemovePolicy],
    ):
        self._attendance_path = attendance_path
        self._player = player
        self._grade_factory = grade_factory
        self._remove_policy = remove_policy

    def read_attendance_file(self):
        if not Path(self._attendance_path).exists():
            raise FileNotFoundError(f"{self._attendance_path} 파일을 찾을 수 없습니다.")

        self.attendance_list = []
        with open(self._attendance_path, encoding="utf-8") as f:
            for line in f.readlines():
                name, day = line.strip().split()
                if day not in DAYS:
                    raise ValueError("Invalid day")

                self.attendance_list.append(Attendance(name, day))

    def get_player_dict_from_attendance(self):
        self.player_dict = {}
        for attendance in self.attendance_list:
            if attendance.name not in self.player_dict:
                self.player_dict[attendance.name] = self._player(
                    attendance.name, self._grade_factory, self._remove_policy
                )

            self.player_dict[attendance.name].attend(attendance.day)

    def print_player_status(self):
        for player in self.player_dict.values():
            player.print_status()

    def print_removed_player(self):
        print("\nRemoved player")
        print("==============")
        for name, player in self.player_dict.items():
            if player.is_removed():
                print(name)

    def print_status_and_removed_player(self):
        self.read_attendance_file()
        self.get_player_dict_from_attendance()
        self.print_player_status()
        self.print_removed_player()


if __name__ == "__main__":
    attendance_manager = AttendanceManager(
        ATTENDANCE_PATH, Player, GradeFactory, PresentRemovePolicy
    )
    attendance_manager.print_status_and_removed_player()
