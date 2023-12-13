"""Created by agarc at 01/10/2023
Features:
"""


class ListHandler:
    @staticmethod
    def flatten_list(the_list: list) -> list:
        """Make a list from a list[list].
        Rather usefull considering all of our cells contain list
        """
        if not the_list:
            return the_list

        rt = []
        for i in the_list:
            if isinstance(i, list):
                rt.extend(ListHandler.flatten_list(i))
            else:
                rt.append(i)
        return rt

    @staticmethod
    def capitalize_list(the_list: list[str]) -> list[str]:
        if not the_list:
            return the_list

        if not isinstance(the_list, list):
            return the_list

        if isinstance(the_list, str):
            return the_list.capitalize()

        if len(the_list) == 1:
            return [the_list[0].capitalize()]

        capitalized_list = [string.capitalize() for string in the_list]
        return capitalized_list

    @staticmethod
    def remove_strings_in_list(
        the_list: list[str],
        strings_to_remove: list[str] = None,
    ) -> list[str]:
        if strings_to_remove is None:
            strings_to_remove = ["_"]
        cleaned_list = [
            string for string in the_list if string not in strings_to_remove
        ]
        if cleaned_list:
            return cleaned_list
        else:
            return []
