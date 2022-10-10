# mindrl
公司要求后续开源用mindspore，目前需要自己造一些轮子。
## :page_facing_up: Description
感觉现在的tianshou生态是最逼近SB3的，可以从tianshou开始。
## :wrench: Dependencies
- Python == 3.8 (Recommend to use [Anaconda](https://www.anaconda.com/download/#linux) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html))
- [PyTorch == 1.11.0](https://pytorch.org/)
- 笔记本电脑
### Installation
1. Clone repo
    ```bash
    git clone https://github.com/superboySB/mindrl.git
    cd mindrl
    ```
   
2. [Optional] Create Virtual Environment
    ```
   conda create -n mindrl python==3.7
   conda activate mindrl
   ```
3. Install minimal dependent packages
    ```sh
    pip install https://ms-release.obs.cn-north-4.myhuaweicloud.com/1.8.1/MindSpore/cpu/x86_64/mindspore-1.8.1-cp37-cp37m-linux_x86_64.whl  # 安装CPU版本的mindspore
    pip install -e . 
    
    # for reinforcement
    git clone https://gitee.com/mindspore/reinforcement.git && cd reinforcement/
    git checkout r0.5
    pip install -r requirements.txt
    pip install -e .
    
    ```
4. [Optional] If you want to install all of RL environments for developing, run:
	```sh
	# 暂时不安装GPU版本的mindspore
	pip install -e .[dev]
	```


## :computer: Training

Test all algorithms in Tianshou
```bash
python test/discrete/test_dqn.py

python train.py -h
```
Then the usage information will be shown as following, more configuration can be found in the default config file [config/default.json](https://github.com/BIT-MCS/DRL-DisasterVC/mcs/config/default.json).
```
Distributed Options:
    --nb-learners <int>         Number of distributed learners [default: 1]
    --nb-workers <int>          Number of distributed workers [default: 4]
    --ray-addr <str>            Ray head node address, None for local [default: None]

Topology Options:
    --actor-host <str>        Name of host actor [default: ImpalaHostActor]
    --actor-worker <str>      Name of worker actor [default: ImpalaWorkerActor]
    --learner <str>           Name of learner [default: ImpalaLearner]
    --exp <str>               Name of host experience cache [default: Rollout]
    --nb-learn-batch <int>    Number of worker batches to learn on (per learner) [default: 2]
    --worker-cpu-alloc <int>     Number of cpus for each rollout worker [default: 8]
    --worker-gpu-alloc <float>   Number of gpus for each rollout worker [default: 0.25]
    --learner-cpu-alloc <int>     Number of cpus for each learner [default: 1]
    --learner-gpu-alloc <float>   Number of gpus for each learner [default: 1]
    --rollout-queue-size <int>   Max length of rollout queue before blocking (per learner) [default: 4]

Environment Options:
    --env <str>             Environment name [default: PongNoFrameskip-v4]
    --rwd-norm <str>        Reward normalizer name [default: Clip]
    --manager <str>         Manager to use [default: SubProcEnvManager]

Script Options:
    --nb-env <int>          Number of env per worker [default: 32]
    --seed <int>            Seed for random variables [default: 0]
    --nb-step <int>         Number of steps to train for [default: 10e6]
    --load-network <path>   Path to network file
    --load-optim <path>     Path to optimizer file
    --resume <path>         Resume training from log ID .../<logdir>/<env>/<log-id>/
    --config <path>         Use a JSON config file for arguments
    --eval                  Run an evaluation after training
    --prompt                Prompt to modify arguments

Optimizer Options:
    --lr <float>               Learning rate [default: 0.0007]
    --grad-norm-clip <float>  Clip gradient norms [default: 0.5]

Logging Options:
    --tag <str>                Name your run [default: None]
    --logdir <path>            Path to logging directory [default: /tmp/adept_logs/]
    --epoch-len <int>          Save a model every <int> frames [default: 1e6]
    --summary-freq <int>       Tensorboard summary frequency [default: 10]

Algorithm Options:
    --use-pixel-control                   Use auxiliary task pixel control
    --pixel-control-loss-gamma <float>    Discount factor for calculate auxiliary loss [default: 0.99]
    --use-mhra                            Use multi-head-relational-attention for feature extraction 
    --num-head <int>                      Num of attention head in mhra [default: 4]
    --minibatch-buffer-size <int>        Num of minibatch buffer size [default: 4]
    --num-sgd <int>                       Num of update times [default: 1]
    --target-worker-clip-rho <float>      Clipped IS ratio for target worker [default: 2]
    --probs-clip <float>                  Advantage Clipped ratio [default: 0.4]
    --gae-lambda <float>                  Lambda in calculate gae estimation [default: 0.995]
    --gae-gamma <float>                   Gamma in calculate gae estimation [default: 0.99]
```
You can also train from config file using the following command:
```
python train.py --config ./config/default.json
```
## :checkered_flag: Testing
Get the usage information of testing:
```
python evaluate.py -h 
```
```
Required:
    --logdir <path>     Path to train logs (.../logs/<env-id>/<log-id>)

Options:
    --epoch <int>           Epoch number to load [default: None]
    --actor <str>           Name of the eval actor [default: ACActorEval]
    --gpu-id <int>          CUDA device ID of GPU [default: 0]
    --nb-episode <int>      Number of episodes to average [default: 30]
    --start <float>         Epoch to start from [default: 0]
    --end <float>           Epoch to end on [default: -1]
    --seed <int>            Seed for random variables [default: 512]
    --custom-network <str>  Name of custom network class
```
To evaluate the trained model, using the following command:
```
python evaluate.py --logdir ${your_log_path}
```
## :clap: Reference
This codebase is based on adept and Ray which are open-sourced. Please refer to that repo for more documentation.
- adept (https://github.com/heronsystems/adeptRL)
- Ray (https://github.com/ray-project/ray)

## :e-mail: Contact
If you have any question, please email `3120211043@bit.edu.cn`.

## Paper
If you are interested in our work, please cite our paper as
```
@inproceedings{10.1145/3447548.3467070,
author = {Wang, Hao and Liu, Chi Harold and Dai, Zipeng and Tang, Jian and Wang, Guoren},
title = {Energy-Efficient 3D Vehicular Crowdsourcing for Disaster Response by Distributed Deep Reinforcement Learning},
doi = {10.1145/3447548.3467070},
booktitle = {Proceedings of the 27th ACM SIGKDD Conference on Knowledge Discovery & Data Mining},
pages = {3679–3687},
numpages = {9}
}

```
