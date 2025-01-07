# This module will contain functions for scheduling sequential and simultaneous periodic chart posting.
from datetime import timezone, datetime, timedelta

import constants


class SimultaneousScheduler:
    def __init__(self, posting_interval: int, custom_current_time=None):
        self.posting_interval = posting_interval

        self.starting_time = None

        self.__get_starting_time()

    def __get_ms_until_next_interval(self):
        """
        Calculate the number of seconds until the next interval.

        Args:
            interval (int): The interval in seconds.

        Returns:
            float: The number of seconds until the next interval.
        """

        now = datetime.now(timezone.utc)

        ms_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() * 1000
        ms_until_next_interval = self.posting_interval * 1000 - (ms_since_midnight % (self.posting_interval * 1000))

        # +delay to make sure the candles are formed
        return ms_until_next_interval + constants.CHART_DELAY_SECONDS * 1000

    def __get_starting_time(self):
        time_until_start = self.__get_ms_until_next_interval()
        starting_time = datetime.now() + timedelta(milliseconds=time_until_start)

        self.starting_time = starting_time


class SequentialScheduler:
    # This class will handle all the scheduling needed for sequential chart sending.
    def __init__(self, posting_interval: int, pair_interval: int, pair_list: list[str]):
        self.posting_interval = posting_interval
        self.pair_interval = pair_interval
        self.pair_list = pair_list
        self.n_pairs = len(pair_list)

        self.starting_schedule = dict()

        self.__get_starting_schedule()

    def __get_ms_since_last_posting(self):
        # Get number of milliseconds since last posting time

        now = datetime.now(timezone.utc)

        ms_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() * 1000

        ms_since_last_posting_time = ms_since_midnight % (self.posting_interval * 1000)

        return ms_since_last_posting_time

    def __get_last_posting_time(self):
        # Get the last posting time as a datetime object

        ms_since_last_posting_time = timedelta(milliseconds=self.__get_ms_since_last_posting())
        now = datetime.now(timezone.utc)

        return now - ms_since_last_posting_time

    def __get_next_scheduled_pair_index(self):
        # Returns the index of the next pair that should be scheduled to post after the launch of the bot.

        ms_since_last_posting_time = self.__get_ms_since_last_posting()
        n_pairs = int(ms_since_last_posting_time / (self.pair_interval * 1000))
        next_scheduled_pair_idx = n_pairs + 1

        if next_scheduled_pair_idx >= self.n_pairs:
            return 0
        else:
            return next_scheduled_pair_idx

    def __get_starting_schedule(self):
        def calculate_left_rolled_posting_times(lst, shift):
            """
                This function rolls the list, and adds posting_interval to whichever pairs have been shifted to the end of the list. The pairs at the
                start are not affected. For example, a minus-1-rolled [0 3600 7200] (With pair interval 3600) would become [3600 7200 46800] if the
                posting interval is 43200.
                Rolls the list to the left by the specified number of positions.

                Args:
                    lst (list): The list to shift, which should contain tuples of pairs and their posting times in seconds, counted from 00:00:00 UTC.
                    shift (int): The shifting delta
            """

            shift = shift % len(lst)  # Ensure the shift is within the bounds of the list length

            # The initial rolled list without the timedelta added
            initial_rolled_list = lst[shift:] + lst[:shift]

            # Add posting_interval to the indices at the end that have been moved there.
            final_rolled_list = []
            for i, posting_seconds_info in enumerate(initial_rolled_list):
                # If the shift value isn't zero, that means we are currently in an incomplete cycle, so the first pair for which charts should be sent
                # is returned as an index.
                if shift != 0:
                    if i > len(initial_rolled_list) - abs(shift) - 1:
                        final_rolled_list.append((posting_seconds_info[0], posting_seconds_info[1] + self.posting_interval))
                    else:
                        final_rolled_list.append((posting_seconds_info[0], posting_seconds_info[1]))

                # If the shift value is zero, that means we have finished a full cycle, and we are about to start a new one. In this case, since
                # the timedeltas are added to the last posting time, all the timedeltas should be increased by the posting interval to update it to
                # the new cycle.
                else:
                    final_rolled_list.append((posting_seconds_info[0], posting_seconds_info[1] + self.posting_interval))

            # Final rolled list is the rolled posting seconds, with the posting interval added to the next posting_interval's times.
            return final_rolled_list

        first_pair_to_post_idx = self.__get_next_scheduled_pair_index()

        # The posting times of the pairs to be posted, without rolling. Basically the posting times if the bot starts before the first pair's posting
        # time.
        pair_times = [pair_order_idx * self.pair_interval for pair_order_idx in range(self.n_pairs)]
        pair_posting_times_zipped = list(zip(self.pair_list, pair_times))

        # The posting time for each pair, once rolled and the next posting_interval's delta taken into account.
        rolled_posting_times = calculate_left_rolled_posting_times(pair_posting_times_zipped, first_pair_to_post_idx)

        # The final schedule of the pair posting data.
        starting_schedule = []

        for pair_order_tuple in rolled_posting_times:
            starting_time = self.__get_last_posting_time() + timedelta(seconds=pair_order_tuple[1] + constants.CHART_DELAY_SECONDS)

            starting_schedule.append(
                {"pair": pair_order_tuple[0],
                 "starting_time": starting_time
                 }
            )

        self.starting_schedule = starting_schedule

    def compose_starting_schedule(self):
        schedule_string = "Sequential mode starting schedule: \n"
        for pair_schedule_item in self.starting_schedule:
            schedule_string += f"{pair_schedule_item['pair']}: {pair_schedule_item['starting_time']}\n"

        return schedule_string
