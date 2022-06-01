# Testing Report (Pigeonhole)

Revision History:

<style>#rev +table td:nth-child(1) { white-space: nowrap }</style>
<div id="rev"></div>

| Date   | Author    | Description                     |
|--------|-----------|---------------------------------|
| Apr 20 | Ciel ZHAO | Converted the template          |
| Apr 26 | Wen Xueru | Provided the TR of Algorithm    |
| Apr 26 | Wen Xueru | Fill in the necessary contents. |

[toc]

## Introduction

This document provides the testing method and results, corresponding to the requirement from the customer. It consists of 3 parts, the testing cases, the test plan, and the testing results.

### How to use the document

You may refer to the content section for the structure of the document, in which Sec. Testing Cases collect the unit and module test information from each team; Sec. Testing Plan shows the steps and expected results of the integration test; Sec. Result describes the real world data out of the test, and the correspondence to the requirements.

## Testing Cases

Testing cases on unit and module testing are proposed.

- Unit testing considers checking a single component of the system.
- Module testing considers checking overlap modules in the system.

### Algorithm

#### Train

##### Test 1.Train a model from scratch.

- [ ] Use `train.py --data_file * --out_model_file *` to train a model from scratch.
- [ ] Report error if data_file is not exist.
- [ ] Report error if data_file is not readable.
- [ ] Report error if data_file is not correctly formatted.
- [ ] Report error if fail to create out_model_file.
- [ ] Save the model parameters and corresponding performance index.

##### Test 2.Fine tine the model.

- [ ] Use `train.py --data_file * --out_model_file * --in_model_file *` to fine tune a model.
- [ ] Report error if data_file is not exist.
- [ ] Report error if data_file is not readable.
- [ ] Report error if data_file is not correctly formatted.
- [ ] Report error if in_model_file is not exist.
- [ ] Report error if in_model_file is not readable.
- [ ] Report error if in_model_file is not correctly formatted.
- [ ] Report error if fail to create out_model_file.
- [ ] Save the model parameters and corresponding performance index.

#### Predict

##### Test 3.Predict the result.

- [ ] Use `predict.py --in_model_file *` to use some model for prediction.
- [ ] Report error if in_model_file is not exist.
- [ ] Report error if in_model_file is not readable.
- [ ] Report error if in_model_file is not correctly formatted.
- [ ] Report error if fail to create out_model_file.
- [ ] Report error if input data flow is not correctly formatted.
- [ ] Output the result in the stdout.

## Testing Plan

Here comes the complete testing plan for integration, referring to the workflows in the system design document.

## Testing Results

The results of the integration are listed here and you may find the correspondence to the requirements in the requirement analysist document.

| Test Case No. | Module | Result | Corresponding Requirement |
|---------------|--------|--------|---------------------------|
|               |        |        |                           |
|               |        |        |                           |
|               |        |        |                           |
|               |        |        |                           |
|               |        |        |                           |
