import logging
import inspect
import multiprocessing
import time
import random

# Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
logger = logging.getLogger(__name__)


class PipelineV2:
    def __init__(self, stages, items_to_process, error_func=None):
        self.stages = stages
        self.items_to_process = items_to_process
        self.error_queue = multiprocessing.Queue()

        self.stage_funcs = []
        for stage in self.stages:
            if stage['func'] is None:
                self.stage_funcs.append(self.default_stage_func)
            else:
                # Make sure the user-defined function accepts the error queue as an argument
                assert callable(stage['func']), "stage['func'] must be a callable function"
                assert len(inspect.signature(stage[
                                                 'func']).parameters) >= 4, "user-defined stage function must accept at least 4 arguments: input_queue, output_queue, stage_index, and error_queue"
                self.stage_funcs.append(stage['func'])

        if error_func is None:
            self.error_func = self.default_error_func
        else:
            self.error_func = error_func

    @staticmethod
    def default_stage_func(input_queue, output_queue, stage_index, error_queue):
        while True:
            item = input_queue.get()
            if item is None:
                break
            print(f'Stage {stage_index + 1} Worker {multiprocessing.current_process().name} received: {item}')
            time.sleep(random.uniform(0.5, 1.5))  # Simulate processing time
            output_queue.put(item)

    @staticmethod
    def default_error_func(error_queue):
        while True:
            error_item = error_queue.get()
            if error_item is None:
                break

            item, error = error_item
            logger.error(f'Error Worker {multiprocessing.current_process().name} received: {item} with error {error}')

    def run(self):

        # Create processes for each stage
        stage_processes = []
        for stage_index, stage in enumerate(self.stages):
            num_workers = stage['num_workers']
            extras = stage.get('extras')
            global_variable = stage.get('global_variable')
            if extras:
                assert isinstance(extras, list), "extras must be a list"
                assert len(extras) == num_workers, "extras must have same length of that of num_workers in that stage"
                processes = [multiprocessing.Process(target=self.stage_funcs[stage_index], args=(stage['input_queue'], stage['output_queue'], stage_index, self.error_queue, extras[i])) for i in range(num_workers)]
            elif global_variable:
                processes = [multiprocessing.Process(target=self.stage_funcs[stage_index], args=(stage['input_queue'], stage['output_queue'], stage_index, self.error_queue, global_variable)) for _ in range(num_workers)]
            else:
                processes = [multiprocessing.Process(target=self.stage_funcs[stage_index], args=(stage['input_queue'], stage['output_queue'], stage_index, self.error_queue)) for _ in range(num_workers)]
            stage_processes.append(processes)

        # Start processes
        for processes in stage_processes:
            for p in processes:
                p.start()

        # Start the error worker process
        error_worker_process = multiprocessing.Process(target=self.error_func, args=(self.error_queue,))
        error_worker_process.start()

        # Put initial items into the first queue
        for item in self.items_to_process:
            self.stages[0]['input_queue'].put(item)

        # Send the correct number of None values to the first queue
        for _ in range(self.stages[0]['num_workers'] * len(self.items_to_process)):
            self.stages[0]['input_queue'].put(None)

        # Wait for all processes to finish
        for processes in stage_processes:
            for p in processes:
                p.join()

        # Send a None value to the error worker process to indicate that no more errors will be added
        self.error_queue.put(None)

        # Wait for the error worker process to finish
        error_worker_process.join()


# Custom functions for each stage
def stage_1_func(input_queue, output_queue, stage_index, error_queue):
    while True:
        item = input_queue.get()
        if item is None:
            break
        print(f'Stage {stage_index + 1} Worker {multiprocessing.current_process().name} received: {item}')
        time.sleep(random.uniform(0.5, 1.5))  # Simulate processing time
        output_queue.put(item * 2)  # Multiply the input by 2


def stage_2_func(input_queue, output_queue, stage_index, error_queue):
    while True:
        item = input_queue.get()
        if item is None:
            break
        print(f'Stage {stage_index + 1} Worker {multiprocessing.current_process().name} received: {item}')
        time.sleep(random.uniform(0.5, 1.5))  # Simulate processing time
        output_queue.put(item + 10)  # Add 10 to the input


def stage_3_func(input_queue, output_queue, stage_index, error_queue):
    while True:
        item = input_queue.get()
        if item is None:
            break
        print(f'Stage {stage_index + 1} Worker {multiprocessing.current_process().name} received: {item}')
        error_queue.put((item, "chumma error"))
        # No more processing, just print the result


if __name__ == '__main__':
    initial_queue = multiprocessing.Queue()
    middle_queue = multiprocessing.Queue()
    secondary_queue = multiprocessing.Queue()
    final_queue = multiprocessing.Queue()

    stages = [
        {'num_workers': 3, 'func': stage_1_func, 'input_queue': initial_queue, 'output_queue': middle_queue},
        {'num_workers': 2, 'func': stage_2_func, 'input_queue': middle_queue, 'output_queue': secondary_queue},
        {'num_workers': 1, 'func': stage_3_func, 'input_queue': secondary_queue, 'output_queue': final_queue},
    ]

    items_to_process = [1, 2, 3, 4, 5]
    pipeline = PipelineV2(stages=stages, items_to_process=items_to_process)
    pipeline.run()
