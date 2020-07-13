from __future__ import annotations
from typing import List, Tuple, Callable
import src.api.retrieve_paper as rp
import src.utility.cmd_enum as ce
import src.utility.search_result as sr
import src.utility.save_query as sq
import src.util as u

"""Mode for searching for and saving papers from arXiv."""


def more_cmd_func(args: List[str], save_query: sq.SaveQuery) -> None:
    selected_id = u.is_list_of_n_ints(args, 1)[0]
    if not save_query.is_valid_id(selected_id):
        raise ValueError(f'selected id {selected_id} is not a valid id')
    print(save_query.get_result(selected_id))


def add_cmd_func(args: List[str], save_query: sq.SaveQuery) -> None:
    for param in args:
        save_query.select_id(int(param))
    u.is_list_of_n_ints(args)


def empty_cmd_func(params: List[str], save_query: sq.SaveQuery) -> None:
    u.is_list_of_n_ints(params, 0)


def quit_cmd_func(args: List[str], save_query: sq.SaveQuery) -> None:
    save_query.submit()
    u.is_list_of_n_ints(args, 0)


def view_cmd_func(args: List[str], save_query: sq.SaveQuery) -> None:
    u.is_list_of_n_ints(args, 0)
    print(save_query)


def help_cmd_func(args: List[str], save_query: sq.SaveQuery) -> None:
    u.is_list_of_n_ints(args, 0)
    UserSearchResponses.display_help_options()


def remove_cmd_func(args: List[str], save_query: sq.SaveQuery) -> None:
    to_remove = u.is_list_of_n_ints(args, 1)[0]
    save_query.remove_selected_id(to_remove)


def key_cmd_func(args: List[str], save_query: sq.SaveQuery) -> None:
    if len(args) < 2:
        raise ValueError('need at least a paper id and one keyword')
    paper_id = int(args[0])
    keywords = args[1:]
    save_query.add_keywords(paper_id, keywords)


class UserSearchResponses(ce.CmdEnum):
    MORE = ce.Command('more', more_cmd_func, 'view summary info selected paper')
    CONT = ce.Command('cont', empty_cmd_func, 'continue seeing new search results')
    VIEW = ce.Command('view', view_cmd_func, 'what files have been added to the query of files to saved')
    ADD = ce.Command('add', add_cmd_func, 'add paper to query to be saved')
    RMV = ce.Command('remove', remove_cmd_func, 'remove paper added to the save query')
    QUIT = ce.Command('quit', quit_cmd_func, 'quit this mode')
    DISP = ce.Command('disp', empty_cmd_func, 'display latest search results again')
    HELP = ce.Command('help', help_cmd_func, 'view what each option does')
    KEY = ce.Command('key', key_cmd_func, 'adding keywords to results added to the save queue')

    @classmethod
    def execute_params(cls, args: List[str], save_query: sq.SaveQuery = None) -> UserSearchResponses:
        return UserSearchResponses(super().execute_params_with_checks(args, save_query))


def create_result_display_func(responses: List[Tuple[int, sr.SearchResult]]) -> Callable:
    def print_results():
        for result_id, response in responses:
            print(result_id, response.title)

    return print_results


def search_mode():
    print('search mode entered')
    params = u.get_formatted_user_input('enter search params')

    print('fetching results...')
    search_query = rp.SearchQuery.from_args(params)
    print('results fetched')

    save_query = sq.SaveQuery()
    for responses in search_query.retrieve_search_results():
        time_to_quit = False
        responses_print_func = create_result_display_func(responses)
        for result_id, response in responses:
            save_query.add_valid_id(result_id, response)

        responses_print_func()

        while True:
            UserSearchResponses.display_available_options()
            results_response = u.get_formatted_user_input()
            cmd = UserSearchResponses.execute_params(results_response, save_query)

            if cmd == UserSearchResponses.CONT:
                break
            elif cmd == UserSearchResponses.QUIT:
                time_to_quit = True
                break
            elif cmd == UserSearchResponses.DISP:
                responses_print_func()

        if time_to_quit:
            break
