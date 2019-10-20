class ModelBase:
    @staticmethod
    def _stringToBool(str) -> bool:
        if str == "0":
            return False
        elif str == "1":
            return True
        else:
            raise Exception(f"Unexpected boolean value {str}")
