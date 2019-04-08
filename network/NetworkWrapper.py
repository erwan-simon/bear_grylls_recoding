from network.Network2 import MyNetwork
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math
import random

class NetworkWrapper():
    def __init__(self, game, player):
        self.reward = 0
        self.gamma = 0.09
        self.model = MyNetwork(inputs=50, outputs=4, learning_rate=0.0005, dropout=0.3)
        self.memory = []
        self.player = player
        self.game = game
        self.random_moves = 0
        self.total_moves = 0

    def get_state(self):
        state = np.zeros(50)
        vision = self.player.take_a_look()
        for square_index in range(len(vision)):
            state[square_index] = 1 if vision[square_index].food else 0
        state[square_index] = self.player.food
        return state

    def set_reward(self):
        # self.reward = (math.sqrt(math.pow(self.game.board_width, 2) + math.pow(self.game.board_height, 2)) - self.player.get_distance_closest_food())
        self.reward = 0
        if self.player.just_eat:
            self.reward = 100
        vision = self.player.take_a_look()
        for square in vision:
            self.reward += 1 * (math.sqrt(50) - math.sqrt(math.pow(square.x - self.player.x, 2) + math.pow(square.y - self.player.y, 2))) if square.food else 0
        if self.reward != 0:
            self.game.turn_latency = 300
        else:
            self.game.turn_latency = 0
        return self.reward

    def remember(self, state, reward_old, action, reward, next_state, done):
        self.memory.append((state, reward_old, action, reward, next_state, done))

    def request_action(self):
        self.epsilon = 500 - self.game.game_index

        #get old state
        state_old = self.get_state()
        reward_old = self.set_reward()
        self.total_moves += 1
        #perform random actions based on agent.epsilon, or choose the action
        if random.randint(0, 1100) < self.epsilon:
            final_move = random.randint(0, 3)
            self.random_moves += 1
        else:
            # predict action based on the old state
            prediction = self.model.predict(state_old)
            final_move = np.argmax(prediction[0])
        #perform new move and get new state
        self.player.do_action(int(final_move))
        state_new = self.get_state()

        #set treward for the new state
        reward = self.set_reward()

        #train short memory base on the new action and state
        self.train_short_memory(state_old, reward_old, final_move, reward, state_new, self.player.dead)

        # store the new data into a long term memory
        self.remember(state_old, reward_old, final_move, reward, state_new, self.player.dead)

    def replay_new(self):
        # print(f'random moves : {100 * float(self.random_moves) / self.total_moves}')
        self.random_moves = 0
        self.total_moves = 0
        if len(self.memory) > 1000:
            minibatch = random.sample(self.memory, 1000)
        else:
            minibatch = self.memory
        for state, reward_old, action, reward, next_state, done in minibatch:
            target = reward - reward_old
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f)

    def train_short_memory(self, state, reward_old, action, reward, next_state, done):
        target = reward - reward_old
        target_f = self.model.predict(state)
        target_f[0][action] = target
        self.model.fit(state, target_f)

    def end_game(self, scores):
        self.save_agent()
        plot_seaborn()

    def save_agent(self, score):
        torch.save(self.model.state_dict(), f"agent_score_{score}.pth.tar")

    def plot_seaborn(self, array_counter, array_score):
        sns.set(color_codes=True)
        ax = sns.regplot(np.array([array_counter])[0], np.array([array_score])[0], color="b", x_jitter=.1, line_kws={'color':'green'})
        ax.set(xlabel='games', ylabel='score')
        plt.show()
