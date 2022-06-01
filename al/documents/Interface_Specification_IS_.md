# Interface Specification (IS) <Algorithm>

Revision History:

| Date   | Author    | Description                                |
|--------|-----------|--------------------------------------------|
| Apr 11 | DONG Jin  | Converted the template & the first version |
| Apr 16 | Wen Xueru | Add test cases                             |
| Apr 29 | Wen Xueru | Fine tine                                  |

## Introduction

The algorithm module is targeting at training model, fine-tining model and predict result.

## Services

Call the module through the following way to train & Fine-tine the model.
```python3 train.py <data_dir> <new_model> <base_model>```

Call the module through the following way to predict result.
```python3 predict.py <model_file>```

### Services Provided

| Service                                                      | Provided  By |
|--------------------------------------------------------------|--------------|
| 1.server can train the general model                         | train        |
| 2.server can train the personalized model for specific users | train        |
| 3.server can predict the next motion state                   | predict      |

### Access Method

| **Access Method**          | **Parameter name**                     | **Parameter type** | **
Description**                                                                                                         | **Exceptions** | **Map to services** |
|------------------------------|------------------------------------------|----------------------|-------------------------------------------------------------------------------------------------------------------------|----------------|---------------------|
| get_model_instance_for_train | haper_params,[params]                    | Dict,[Dict]          | haper_params can control some data in the training process by changing values such as learning rate.                    |                | 1,2                 |
| get_data                     | path_data                                | String               | path_data provides the location of data and this method can get original data.                                          |                | 1,2                 |
| get_real_time_data           | socket                                   | Socket               | socket continually provide real-time data                                                                               |                | 3                   |
| process_data                 | original_data                            | Dataframe            | when training, data is [n,1800], n is uncertain; when predicting, data is [1,n], containg real-time data for 5 seconds. |                | 1,2,3               |
| get_model_params             | path_params                              | String               | path_params provide the location for one model's params.                                                                |                | 2,3                 |
| save_model_params            | trained_model_params, path_to_save_model | Dict, String         | after the model has been trained, the params will be saved                                                              |                | 1,2                 |
| save_predict_result          | next_motion_state                        | Integer              | next_motion_state will be one of 0,1,2,3,4,5                                                                            |                | 3                   |

### Access Method Effects

| **Access Method**          | **Description**                                                                                                                                 |
|------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| get_model_instance_for_train | when training or predicting, one model will be created.                                                                                         |
| get_data                     | before training, original data will be achieved by file.                                                                                        |
| get_real_time_data           | before predicting, original data will be achieved by socket.                                                                                    |
| process_data                 | after get original data, this method will preprocessing the data and then generate data for training or predicting, the type of data is tensor. |
| get_model_params             | before getting the instance of model, params may be needed.                                                                                     |
| save_model_params            | after training process, the params need to be saved.                                                                                            |
| save_predict_result          | after predicting process, the result need to be saved.                                                                                          |
