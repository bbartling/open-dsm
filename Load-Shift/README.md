# LOAD SHIFT 

![alg](images/rtu_power_and_action_2022-06-14_MOD.png)

Random Forest Classifier for Multi-Class Action Classification
This repository contains code demonstrating the use of a Random Forest Classifier for multi-class action classification. The goal of multi-class classification is to assign instances to one of several classes when there are more than two possible classes. In this case, the action_mapping dictionary is provided to map the action names to numerical labels:

```
action_mapping = {
    'no_action_required': 0,
    'building_precooling_start': 1,
    'load_shifting_idle': 2,
    'float_setpoints_upward': 3
}
```

The RandomForestClassifier, a powerful machine learning algorithm, is utilized in this project. It is capable of handling both binary classification and multi-class classification problems. In the case of this multi-class classification task, the RandomForestClassifier automatically handles the mapping of model outputs to the corresponding action labels based on the provided action_mapping.

The model is trained on a given dataset consisting of various features related to the action labels. After training, the model can make predictions and assign action labels to new instances. The output of the model is a numerical label, representing one of the four possible actions: 'no_action_required', 'building_precooling_start', 'load_shifting_idle', or 'float_setpoints_upward'. The action_mapping dictionary is used to map the numerical labels back to their corresponding action names for easier interpretation and understanding.

By utilizing the RandomForestClassifier and the provided action_mapping, this code provides a solution for multi-class action classification tasks, allowing the model to learn from input features and accurately predict the appropriate action label for new instances.


* TODO test on more data and make into an IoT app with BACnet or rest API to test on live HVAC system

