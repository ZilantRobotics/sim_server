# Simulation Server

## Purpoose
This is the web application part for HITL simulator project. Currently, it supports
user login, uploading firmware, config and mission files and executing them with [workers](https://github.com/ZilantRobotics/sim_worker).

## Running
Please, observe the `.env` file for configuration options, to run this application in dev
mode, please execute the following command

`python3 -m flask run`

Default configuration options do match those in worker, so ideally you should just execute this command first,
then the one from the worker repo and got yourself a working simulator setup.

## System requirements
* Python: 3.9
* OS: Ubuntu 22.04
* CPU: AMD FX 8300 or better, or comparable ARM64 processor


