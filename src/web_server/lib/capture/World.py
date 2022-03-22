import random

import numpy as np
import scipy.signal
import scipy.ndimage
import scipy.stats


class DiamondSquare(object):
    def __init__(self, noise_factor=0.05):
        assert (0 <= noise_factor < 1)

        self.noise_multiplier = noise_factor

    def run(self, ground: np.array, step_size=None):
        if step_size is None:
            step_size = ground.shape[0] - 1

        while step_size > 1:
            random_value = step_size / 2
            self.diamond(ground, step_size, random_value)
            self.square(ground, step_size, random_value)
            step_size = step_size // 2
            random_value *= 2 ** -self.noise_multiplier
        return ground

    def diamond(self, ground, step_size, random_value):
        for x in range(0, ground.shape[0] - 1, step_size):
            for y in range(0, ground.shape[1] - 1, step_size):
                value = random.uniform(-random_value / 2, random_value / 2)
                value += (
                                 ground[x, y] +
                                 ground[x, y + step_size] +
                                 ground[x + step_size, y] +
                                 ground[x + step_size, y + step_size]
                         ) / 4
                ground[x + step_size // 2, y + step_size // 2] = value

    def square(self, ground, step_size, random_value):
        for x in range(0, ground.shape[0], step_size // 2):
            for y in range(0, ground.shape[1], step_size // 2):
                if x % step_size == y % step_size:
                    continue

                value = random.uniform(-random_value / 2, random_value / 2)
                div_value = 0

                # We have an offset at step 0, 2, 4, etc..
                if x - step_size // 2 >= 0:
                    value += ground[x - step_size // 2, y]
                    div_value += 1
                if y - step_size // 2 >= 0:
                    value += ground[x, y - step_size // 2]
                    div_value += 1
                if x + step_size // 2 < ground.shape[0]:
                    value += ground[x + step_size // 2, y]
                    div_value += 1
                if y + step_size // 2 < ground.shape[1]:
                    value += ground[x, y + step_size // 2]
                    div_value += 1

                ground[x, y] = value / div_value


class World(object):
    WATER_VALUE = 1
    GROUND_VALUE = 2
    MOUNTAIN_VALUE = 3

    def __init__(self, n=5, random_factor=4, noise_factor=0.1):
        self.size = 2 ** n + 1

        self.min_z = 0
        self.max_z = 1

        self.diamond_star = DiamondSquare(noise_factor=noise_factor)

        self.ground = np.zeros((self.size, self.size), dtype=float)
        self.generate(random_factor)

    def generate(self, n=4):
        for i in range(0, self.size, self.size // (2 ** n)):
            for j in range(0, self.size, self.size // (2 ** n)):
                self.ground[i, j] = np.random.randint(self.min_z, self.max_z)

        self.ground = self.diamond_star.run(self.ground, step_size=self.ground.shape[0] // 4)
        self.ground = np.array(scipy.ndimage.gaussian_filter(self.ground, 1))

        ground_mean = np.mean(self.ground)
        ground_std = np.std(self.ground)

        water_percentile = 0.3
        mountain_percentile = 0.9

        water_threshold = scipy.stats.norm.ppf(water_percentile, loc=ground_mean, scale=ground_std)
        mountain_threshold = scipy.stats.norm.ppf(mountain_percentile, loc=ground_mean, scale=ground_std)

        water = self.ground < water_threshold
        mountain = self.ground > mountain_threshold
        ground = 1 - (water + mountain)

        self.ground = water * self.WATER_VALUE + ground * self.GROUND_VALUE + mountain * self.MOUNTAIN_VALUE

        self.remove_islands(threshold=0.05)

    def remove_islands(self, threshold=0.05):
        processed = self.ground == 1
        is_done = False
        while not is_done:
            is_done = True

            processed[]




def t_value(x):
    return np.exp(-x ** 2 / 2) / np.sqrt(2 * np.pi)


if __name__ == "__main__":
    for i in range(10):
        percent = (i + 0.0000001) / 10

        world = World(n=7, random_factor=1, noise_factor=0.1)

        import matplotlib.pyplot as plt

        plt.imshow(world.ground, cmap='autumn', interpolation='nearest')

        plt.title("2-D Heat Map")
        plt.show()
