from typing import Optional


class ModelBase:
    @staticmethod
    def _stringToBool(str) -> bool:
        if str == "0":
            return False
        elif str == "1":
            return True
        else:
            raise Exception(f"Unexpected boolean value {str}")

    @staticmethod
    def _nonifyStr(x: str) -> Optional[str]:
        return None if x == "" else x

    @staticmethod
    def _nonifyInt(x: str) -> Optional[int]:
        return None if x == "" or x == "0" else int(x)
