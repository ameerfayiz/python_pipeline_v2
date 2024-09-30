# PipelineV2

PipelineV2 is a flexible and efficient multi-stage processing pipeline implemented in Python using multiprocessing. It allows you to define multiple processing stages, each with its own number of workers, and process items through these stages concurrently.

## Features

- Multi-stage processing with customizable number of workers per stage
- Custom stage functions support
- Built-in error handling with customizable error function
- Support for passing extra arguments to stage functions
- Efficient use of multiprocessing for parallel execution

## Installation

To use PipelineV2, simply copy the `PipelineV2` class into your project. Make sure you have Python 3.x installed.

## Usage

Here's a basic example of how to use PipelineV2:

```python
from pipeline_v2 import PipelineV2
import multiprocessing

# Define your stage functions
def stage_1_func(input_queue, output_queue, stage_index, error_queue):
    # Your stage 1 processing logic here
    pass

def stage_2_func(input_queue, output_queue, stage_index, error_queue):
    # Your stage 2 processing logic here
    pass

def stage_3_func(input_queue, output_queue, stage_index, error_queue):
    # Your stage 3 processing logic here
    pass

# Set up your pipeline
initial_queue = multiprocessing.Queue()
middle_queue = multiprocessing.Queue()
final_queue = multiprocessing.Queue()

stages = [
    {'num_workers': 3, 'func': stage_1_func, 'input_queue': initial_queue, 'output_queue': middle_queue},
    {'num_workers': 2, 'func': stage_2_func, 'input_queue': middle_queue, 'output_queue': final_queue},
    {'num_workers': 1, 'func': stage_3_func, 'input_queue': final_queue, 'output_queue': None},
]

items_to_process = [1, 2, 3, 4, 5]

# Create and run the pipeline
pipeline = PipelineV2(stages=stages, items_to_process=items_to_process)
pipeline.run()
```

## Customization

### Custom Stage Functions

You can define custom functions for each stage. These functions should accept at least four arguments:

1. `input_queue`: Queue to receive items from the previous stage
2. `output_queue`: Queue to send processed items to the next stage
3. `stage_index`: Index of the current stage
4. `error_queue`: Queue to send error information

### Error Handling

PipelineV2 includes a default error handling function, but you can provide your own by passing it to the `error_func` parameter when initializing the pipeline.

### Extra Arguments

You can pass extra arguments to stage functions using the `extras` key in the stage dictionary:

```python
stages = [
    {'num_workers': 2, 'func': custom_func, 'input_queue': q1, 'output_queue': q2, 'extras': [arg1, arg2]},
    # ...
]
```

## Contributing

Contributions to PipelineV2 are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).
