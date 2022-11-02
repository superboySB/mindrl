import argparse
import os
import pprint

import gym
import numpy as np

import mindspore as ms
from mindspore import nn
from mindspore.common.initializer import Zero, Orthogonal
from tensorboardX import SummaryWriter

from mindrl.data import Collector, VectorReplayBuffer
from mindrl.env import DummyVectorEnv
from mindrl.policy import PGPolicy
from mindrl.trainer import onpolicy_trainer
from mindrl.utils import TensorboardLogger
from mindrl.utils.net.common import Net


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', type=str, default='CartPole-v0')
    parser.add_argument('--reward-threshold', type=float, default=None)
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--buffer-size', type=int, default=20000)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--gamma', type=float, default=0.95)
    parser.add_argument('--epoch', type=int, default=10)
    parser.add_argument('--step-per-epoch', type=int, default=40000)
    parser.add_argument('--episode-per-collect', type=int, default=8)
    parser.add_argument('--repeat-per-collect', type=int, default=2)
    parser.add_argument('--batch-size', type=int, default=64)
    parser.add_argument('--hidden-sizes', type=int, nargs='*', default=[64, 64])
    parser.add_argument('--training-num', type=int, default=8)
    parser.add_argument('--test-num', type=int, default=100)
    parser.add_argument('--logdir', type=str, default='log')
    parser.add_argument('--render', type=float, default=0.)
    parser.add_argument('--rew-norm', type=int, default=1)
    parser.add_argument('--device', type=str, default='CPU', choices=['Ascend', 'CPU', 'GPU'],
                        help='Choose a device to run the dqn example(Default: CPU).')
    args = parser.parse_known_args()[0]
    return args


def test_pg(args=get_args()):
    ms.set_context(device_target=args.device)
    ms.set_context(mode=ms.PYNATIVE_MODE)
    if ms.get_context('device_target') in ['CPU']:
        ms.set_context(enable_graph_kernel=True)
    np.random.seed(args.seed)
    ms.set_seed(args.seed)

    env = gym.make(args.task)
    args.state_shape = env.observation_space.shape or env.observation_space.n
    args.action_shape = env.action_space.shape or env.action_space.n
    if args.reward_threshold is None:
        default_reward_threshold = {"CartPole-v0": 195}
        args.reward_threshold = default_reward_threshold.get(
            args.task, env.spec.reward_threshold
        )
    # train_envs = gym.make(args.task)
    # you can also use mindrl.env.SubprocVectorEnv
    train_envs = DummyVectorEnv(
        [lambda: gym.make(args.task) for _ in range(args.training_num)]
    )
    # test_envs = gym.make(args.task)
    test_envs = DummyVectorEnv(
        [lambda: gym.make(args.task) for _ in range(args.test_num)]
    )
    # seed
    train_envs.seed(args.seed)
    test_envs.seed(args.seed)
    # model
    net = Net(
        args.state_shape,
        args.action_shape,
        hidden_sizes=args.hidden_sizes,
        softmax=True
    )
    optim = nn.Adam(net.trainable_params(), learning_rate=args.lr)
    dist = nn.probability.distribution.Categorical
    policy = PGPolicy(
        net,
        optim,
        dist,
        args.gamma,
        reward_normalization=args.rew_norm,
        action_space=env.action_space,
    )
    for m in net.cells():
        if isinstance(m, nn.Dense):
            # orthogonal initialization
            m.weight.set_data(Orthogonal(gain=np.sqrt(2)))
            m.bias.set_data(Zero())

    # collector
    train_collector = Collector(
        policy, train_envs, VectorReplayBuffer(args.buffer_size, len(train_envs))
    )
    test_collector = Collector(policy, test_envs)
    # log
    log_path = os.path.join(args.logdir, args.task, 'pg')
    writer = SummaryWriter(log_path)
    logger = TensorboardLogger(writer)

    def save_best_fn(policy):
        ms.save_checkpoint(policy, os.path.join(log_path, 'policy.ckpt'))

    def stop_fn(mean_rewards):
        return mean_rewards >= args.reward_threshold

    # trainer
    result = onpolicy_trainer(
        policy,
        train_collector,
        test_collector,
        args.epoch,
        args.step_per_epoch,
        args.repeat_per_collect,
        args.test_num,
        args.batch_size,
        episode_per_collect=args.episode_per_collect,
        stop_fn=stop_fn,
        save_best_fn=save_best_fn,
        logger=logger,
    )
    assert stop_fn(result['best_reward'])

    if __name__ == '__main__':
        pprint.pprint(result)
        # Let's watch its performance!
        env = gym.make(args.task)
        policy.set_train(False)
        collector = Collector(policy, env)
        result = collector.collect(n_episode=1, render=args.render)
        rews, lens = result["rews"], result["lens"]
        print(f"Final reward: {rews.mean()}, length: {lens.mean()}")


if __name__ == '__main__':
    test_pg()
